"""Local API server for Friday desktop - streams Agent events via SSE"""

import asyncio
import base64
import io
import json
import os
import platform
import re
import sys
import time
import uuid
import xml.etree.ElementTree as ET
from datetime import UTC, date, datetime, timedelta
from functools import wraps
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quart import Quart, Response, jsonify, request
from quart_cors import cors

from agent.core import Agent
from core.automations import get_automation_engine
from core.briefing import BriefingEngine
from core.diary import get_diary
from core.logger import get_metrics
from core.memory import get_memory_manager
from core.proactive import CalendarMonitor, EmailMonitor, ProactiveMonitor, ScreenMonitor, SystemMonitor
from core.registry import discover_plugins
from core.security import get_approval_registry
from core.vision import get_vision_engine

# ─── API Version Prefix ──────────────────────────────────────────
API_PREFIX = "/api/v1"

# ─── Shared async HTTP client ────────────────────────────────────
_async_client: httpx.AsyncClient | None = None


def get_async_client() -> httpx.AsyncClient:
    global _async_client
    if _async_client is None:
        _async_client = httpx.AsyncClient(
            timeout=10.0,
            headers={"User-Agent": "Friday/1.0"},
        )
    return _async_client


# ─── SSE Event Broadcaster ──────────────────────────────────────
class EventBroadcaster:
    def __init__(self):
        self._subscribers: list[asyncio.Queue] = []
        self._lock = asyncio.Lock()

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=256)
        async with self._lock:
            self._subscribers.append(q)
        return q

    async def unsubscribe(self, q: asyncio.Queue):
        async with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    async def broadcast(self, event_type: str, data: dict):
        msg = json.dumps({"type": event_type, "data": data}, ensure_ascii=False) + "\n\n"
        async with self._lock:
            dead: list[asyncio.Queue] = []
            for q in self._subscribers:
                try:
                    q.put_nowait(msg)
                except asyncio.QueueFull:
                    dead.append(q)
            for q in dead:
                self._subscribers.remove(q)


_broadcaster = EventBroadcaster()


# ─── Load env vars ───────────────────────────────────────────────
def _load_dotenv():
    root = Path(__file__).resolve().parent.parent
    env_path = root / ".env"
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip("\"'")
            if not os.environ.get(key):
                os.environ[key] = val


_load_dotenv()

# ─── Security ────────────────────────────────────────────────────
_API_SECRET = os.environ.get("API_SECRET", "")
_FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")


def require_auth(f):
    """Decorator that checks X-API-Key header against API_SECRET.
    If API_SECRET is empty, auth is skipped (local dev mode)."""

    @wraps(f)
    async def wrapper(*args, **kwargs):
        if _API_SECRET:
            key = request.headers.get("X-API-Key", "")
            if key != _API_SECRET:
                return jsonify({"error": "Unauthorized"}), 401
        return await f(*args, **kwargs)

    return wrapper


# ─── Validation helpers ──────────────────────────────────────────
_MAX_MESSAGE_LENGTH = 10_000
_VALID_LANGUAGES = {"english", "hinglish"}


def validate_chat_input(data: dict) -> str | None:
    msg = data.get("message", "")
    if not isinstance(msg, str):
        return "message must be a string"
    if not msg.strip():
        return "message cannot be empty"
    if len(msg) > _MAX_MESSAGE_LENGTH:
        return f"message exceeds {_MAX_MESSAGE_LENGTH} characters"
    return None


def validate_session_language(lang: str) -> str | None:
    if lang and lang.lower() not in _VALID_LANGUAGES:
        return f"invalid language '{lang}', must be one of {_VALID_LANGUAGES}"
    return None


def validate_output_path(path: str) -> str | None:
    # Prevent path traversal
    if ".." in path or path.startswith("~"):
        return "invalid path: directory traversal not allowed"
    return None


# ─── App setup ───────────────────────────────────────────────────
app = Quart(__name__)
app = cors(
    app,
    allow_origin=_FRONTEND_ORIGIN,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)

discover_plugins()

_agents: dict[str, Agent] = {}
_proactive: ProactiveMonitor | None = None
_diary = get_diary()


def get_proactive() -> ProactiveMonitor:
    global _proactive
    if _proactive is None:
        _proactive = ProactiveMonitor()
        _proactive.add_monitor(ScreenMonitor(interval=3.0))
        _proactive.add_monitor(CalendarMonitor(interval=60.0))
        _proactive.add_monitor(EmailMonitor(interval=120.0))
        _proactive.add_monitor(SystemMonitor(interval=30.0))
        _proactive.start()
    return _proactive


def _get_agent(session_id: str, persona: str | None = None) -> Agent:
    if session_id not in _agents:
        _agents[session_id] = Agent(persona=persona)
    elif persona and _agents[session_id].persona != persona:
        _agents[session_id].persona = persona
        _agents[session_id].clear()
    return _agents[session_id]


from cachetools import TTLCache  # noqa: E402

TTL_CACHE: TTLCache = TTLCache(maxsize=500, ttl=300)


def ttl_cache(seconds: int = 60):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            key = f.__name__ + str(request.query_string.decode())
            if key in TTL_CACHE:
                return jsonify(TTL_CACHE[key])
            result = await f(*args, **kwargs)
            if isinstance(result, tuple):
                body, status = result
                if status == 200 and body is not None:
                    TTL_CACHE[key] = body
                return result
            if hasattr(result, "status_code") and result.status_code == 200:
                try:
                    import json as _json

                    data = _json.loads((await result.get_data()).decode())
                    TTL_CACHE[key] = data
                except Exception:
                    pass
            return result

        return wrapper

    return decorator


# ─── Chat ────────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/chat", methods=["POST"])
@require_auth
async def chat():
    data = await request.get_json()
    err = validate_chat_input(data)
    if err:
        return jsonify({"error": err}), 422
    user_input = data.get("message", "")
    session_id = data.get("session_id", "default")
    persona = data.get("persona")
    agent = _get_agent(session_id, persona=persona)

    async def generate():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()
        import concurrent.futures

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        def _run():
            last_text = ""
            try:
                for event in agent.run(user_input):
                    last_text = event.get("content", last_text)
                    loop.call_soon_threadsafe(queue.put_nowait, event)
            except Exception as e:
                loop.call_soon_threadsafe(queue.put_nowait, {"type": "done", "content": f"Error: {e}", "final": True})
            finally:
                try:
                    _diary.record(
                        title=(user_input.strip() or "Chat")[:160],
                        body=(last_text.strip() or "_no response_")[:500],
                        kind="conversation",
                    )
                except Exception:
                    pass
                try:
                    from core.knowledge import get_knowledge_graph

                    get_knowledge_graph().store(user_input)
                except Exception:
                    pass
                loop.call_soon_threadsafe(queue.put_nowait, None)

        executor.submit(_run)
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=300)
                if event is None:
                    break
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except TimeoutError:
            yield json.dumps({"type": "done", "content": "Request timed out", "final": True}) + "\n"
        finally:
            executor.shutdown(wait=False)

    return Response(generate(), mimetype="text/event-stream")


# ─── Autopilot ────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/autopilot", methods=["POST"])
@require_auth
async def autopilot():
    """Stream an autonomous multi-task run: plan -> ordered steps -> verify."""
    data = await request.get_json() or {}
    goal = data.get("goal", "")
    if not goal:
        return jsonify({"error": "goal is required"}), 422
    session_id = data.get("session_id", "default")
    workspace = data.get("workspace") or os.getenv("FRIDAY_WORKSPACE")
    if workspace:
        err = validate_output_path(workspace)
        if err:
            return jsonify({"error": err}), 422
    agent = _get_agent(session_id)

    async def generate():
        loop = asyncio.get_event_loop()
        queue: asyncio.Queue = asyncio.Queue()
        import concurrent.futures

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        def _run():
            last_text = ""
            try:
                for event in agent.run_autopilot(goal, workspace):
                    last_text = event.get("content", last_text)
                    loop.call_soon_threadsafe(queue.put_nowait, event)
            except Exception as e:
                loop.call_soon_threadsafe(
                    queue.put_nowait, {"type": "done", "content": f"Autopilot error: {e}", "final": True}
                )
            finally:
                try:
                    _diary.record(
                        title=(goal.strip() or "Autopilot run")[:160],
                        body=(last_text.strip() or "_run finished_")[:500],
                        kind="autopilot",
                    )
                except Exception:
                    pass
                loop.call_soon_threadsafe(queue.put_nowait, None)

        executor.submit(_run)
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=600)
                if event is None:
                    break
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except TimeoutError:
            yield json.dumps({"type": "done", "content": "Autopilot timed out", "final": True}) + "\n"
        finally:
            executor.shutdown(wait=False)

    return Response(generate(), mimetype="text/event-stream")


# ─── Sessions ────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/sessions", methods=["GET"])
@require_auth
async def list_sessions():
    return jsonify({"sessions": [{"id": sid, "language": a.language} for sid, a in _agents.items()]})


@app.route(f"{API_PREFIX}/sessions", methods=["POST"])
@require_auth
async def create_session():
    data = await request.get_json() or {}
    session_id = str(uuid.uuid4())[:8]
    lang = data.get("language", "english")
    err = validate_session_language(lang)
    if err:
        return jsonify({"error": err}), 422
    _agents[session_id] = Agent(language=lang)
    return jsonify({"session_id": session_id, "language": lang}), 201


@app.route(f"{API_PREFIX}/sessions/<session_id>", methods=["DELETE"])
@require_auth
async def delete_session(session_id):
    if session_id not in _agents:
        return jsonify({"error": "session not found"}), 404
    _agents.pop(session_id, None)
    return jsonify({"status": "deleted"})


# ─── Output directory ────────────────────────────────────────────
@app.route(f"{API_PREFIX}/output-dir", methods=["PUT"])
@require_auth
async def set_output_dir():
    data = await request.get_json()
    session_id = data.get("session_id", "default")
    path = data.get("path", "")
    err = validate_output_path(path)
    if err:
        return jsonify({"error": err}), 422
    agent = _get_agent(session_id)
    agent.set_output_dir(path or None)
    return jsonify({"status": "ok", "output_dir": path})


@app.route(f"{API_PREFIX}/output-dir", methods=["GET"])
@require_auth
async def get_output_dir():
    session_id = request.args.get("session_id", "default")
    agent = _get_agent(session_id)
    return jsonify({"output_dir": agent.output_dir or ""})


# ─── Tool call approvals ─────────────────────────────────────────
@app.route(f"{API_PREFIX}/approvals", methods=["GET"])
@require_auth
async def list_approvals():
    return jsonify({"approvals": get_approval_registry().pending()})


@app.route(f"{API_PREFIX}/approvals/<request_id>", methods=["POST"])
@require_auth
async def resolve_approval(request_id):
    data = await request.get_json() or {}
    allowed = bool(data.get("allowed", False))
    resolved = get_approval_registry().resolve(request_id, allowed)
    if not resolved:
        return jsonify({"error": "approval request not found"}), 404
    return jsonify({"status": "ok", "request_id": request_id, "allowed": allowed})


# ─── Metrics & Health ────────────────────────────────────────────
@app.route(f"{API_PREFIX}/metrics")
@require_auth
async def metrics():
    return jsonify(get_metrics())


@app.route(f"{API_PREFIX}/health")
async def health():
    return jsonify({"status": "ok", "sessions": len(_agents)})


# ─── Alerts ──────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/alerts/stream")
@require_auth
async def alert_stream():
    pm = get_proactive()

    async def generate():
        while True:
            alerts = await pm.get_alerts()
            for alert in alerts:
                yield f"data: {json.dumps(alert.to_dict(), ensure_ascii=False)}\n\n"
            await asyncio.sleep(1)

    return Response(generate(), mimetype="text/event-stream")


@app.route(f"{API_PREFIX}/alerts")
@require_auth
async def alerts_list():
    pm = get_proactive()
    alerts = await pm.get_alerts()
    return jsonify({"alerts": [a.to_dict() for a in alerts], "count": len(alerts)})


# ─── System Info ─────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/system-info")
@require_auth
@ttl_cache(30)
async def system_info():
    metrics = get_metrics()
    return jsonify(
        {
            "hostname": platform.node(),
            "os": f"{platform.system()} {platform.release()}",
            "cpu_cores": os.cpu_count(),
            "python_version": sys.version.split()[0],
            "uptime_seconds": metrics.get("uptime_seconds", 0),
            "llm_calls": metrics.get("llm_calls", 0),
            "tokens_used": metrics.get("tokens_used", 0),
            "failures": metrics.get("failures", 0),
            "retries": metrics.get("retries", 0),
            "model": "openrouter/free",
            "provider": "OpenRouter",
        }
    )


# ─── News ────────────────────────────────────────────────────────
_NEWS_RSS = [
    "https://hnrss.org/frontpage",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "http://feeds.bbci.co.uk/news/rss.xml",
]


@app.route(f"{API_PREFIX}/news")
@require_auth
@ttl_cache(300)
async def news():
    client = get_async_client()
    items = []
    for url in _NEWS_RSS:
        try:
            resp = await client.get(url, timeout=5)
            root = ET.fromstring(resp.content)
            for entry in root.findall(".//item")[:6]:
                title = entry.findtext("title", "")
                link = entry.findtext("link", "")
                desc = entry.findtext("description", "")
                pub = entry.findtext("pubDate", "")
                img = ""
                ns = {"media": "http://search.yahoo.com/mrss/"}
                for m in entry.findall("media:content", ns):
                    img = m.get("url", "")
                    break
                if not img:
                    m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
                    if m:
                        img = m.group(1)
                items.append(
                    {
                        "title": title,
                        "url": link,
                        "image": img,
                        "source": url.split("/")[2],
                        "time": pub,
                    }
                )
        except Exception:
            continue
    return jsonify({"articles": items})


# ─── Weather ─────────────────────────────────────────────────────
_WEATHER_LAT = 33.68
_WEATHER_LON = 73.05
_WEATHER_LOCATION = "Islamabad"


@app.route(f"{API_PREFIX}/weather")
@require_auth
@ttl_cache(300)
async def weather():
    try:
        lat = request.args.get("lat", _WEATHER_LAT)
        lon = request.args.get("lon", _WEATHER_LON)
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
            f"&timezone=auto"
        )
        client = get_async_client()
        resp = await client.get(url, timeout=5)
        data = resp.json()
        cur = data.get("current", {})
        return jsonify(
            {
                "temperature": cur.get("temperature_2m"),
                "feels_like": cur.get("apparent_temperature"),
                "humidity": cur.get("relative_humidity_2m"),
                "wind_speed": cur.get("wind_speed_10m"),
                "weather_code": cur.get("weather_code", 0),
                "location": request.args.get("location", _WEATHER_LOCATION),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 502


# ─── Stocks ─────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/stocks")
@require_auth
@ttl_cache(60)
async def stocks():
    symbols = request.args.get("symbols", "AAPL,GOOG,MSFT,NVDA,BTC-USD")
    try:
        import yfinance as yf

        def _fetch():
            tickers = yf.Tickers([s.strip() for s in symbols.split(",")])
            results = []
            for sym in symbols.split(","):
                sym = sym.strip()
                try:
                    t = tickers.tickers[sym]
                    info = t.info or {}
                    hist = t.history(period="7d")
                    close = hist["Close"].tolist() if not hist.empty else []
                    price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or 0
                    prev_close = info.get("previousClose") or price
                    change = price - prev_close
                    change_pct = (change / prev_close * 100) if prev_close else 0
                    results.append(
                        {
                            "symbol": sym.upper(),
                            "price": round(price, 2),
                            "change": round(change, 2),
                            "change_pct": round(change_pct, 2),
                            "sparkline": [round(v, 2) for v in close],
                        }
                    )
                except Exception:
                    results.append({"symbol": sym.upper(), "price": 0, "change": 0, "change_pct": 0, "sparkline": []})
            return results

        results = await asyncio.to_thread(_fetch)
        return jsonify({"stocks": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 502


# ─── GitHub Trending ─────────────────────────────────────────────
@app.route(f"{API_PREFIX}/github-trending")
@require_auth
@ttl_cache(300)
async def github_trending():
    try:
        client = get_async_client()
        resp = await client.get(
            "https://github.com/trending",
            headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"},
            timeout=10,
        )
        html = resp.text
        repos = []
        for article in re.findall(r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>', html, re.DOTALL)[:10]:
            h = re.search(r'href="/([^/"]+/[^/"]+)"', article)
            full_name = h.group(1) if h else ""
            desc_m = re.search(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', article, re.DOTALL)
            desc = desc_m.group(1).strip() if desc_m else ""
            desc = re.sub(r"<[^>]+>", "", desc).strip()
            star_m = re.search(r'<span[^>]*class="[^"]*d-inline-block[^"]*"[^>]*>.*?(\d[\d,]*)\s*</span>', article)
            stars = star_m.group(1).replace(",", "") if star_m else "0"
            lang_m = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>', article)
            lang = lang_m.group(1).strip() if lang_m else ""
            repos.append(
                {
                    "name": full_name,
                    "url": f"https://github.com/{full_name}",
                    "description": desc,
                    "stars": int(stars) if stars.isdigit() else 0,
                    "language": lang,
                }
            )
        return jsonify({"repos": repos})
    except Exception as e:
        return jsonify({"error": str(e)}), 502


# ─── Earthquakes ─────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/earthquakes")
@require_auth
@ttl_cache(120)
async def earthquakes():
    try:
        client = get_async_client()
        resp = await client.get(
            "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson",
            timeout=8,
        )
        data = resp.json()
        items = []
        for f in data.get("features", [])[:8]:
            props = f.get("properties", {})
            coords = f.get("geometry", {}).get("coordinates", [0, 0, 0])
            items.append(
                {
                    "mag": props.get("mag", 0),
                    "place": props.get("place", "Unknown"),
                    "time": datetime.fromtimestamp(props.get("time", 0) / 1000, tz=UTC).isoformat(),
                    "depth": round(coords[2], 1),
                    "url": props.get("url", ""),
                }
            )
        return jsonify({"earthquakes": items})
    except Exception as e:
        return jsonify({"earthquakes": [], "error": str(e)})


# ─── Crypto ──────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/crypto")
@require_auth
@ttl_cache(120)
async def crypto():
    try:
        client = get_async_client()
        resp = await client.get(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=6&sparkline=false",
            headers={"Accept": "application/json"},
            timeout=8,
        )
        data = resp.json()
        coins = []
        for c in data:
            coins.append(
                {
                    "symbol": c.get("symbol", "").upper(),
                    "name": c.get("name", ""),
                    "price": round(c.get("current_price", 0), 2),
                    "change_24h": round(c.get("price_change_percentage_24h", 0), 1),
                    "market_cap": c.get("market_cap", 0),
                }
            )
        return jsonify({"crypto": coins})
    except Exception as e:
        return jsonify({"crypto": [], "error": str(e)})


# ─── Space ──────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/space")
@require_auth
@ttl_cache(60)
async def space():
    try:
        client = get_async_client()
        iss_resp, astro_resp = await asyncio.gather(
            client.get("http://api.open-notify.org/iss-now.json", timeout=5),
            client.get("http://api.open-notify.org/astros.json", timeout=5),
        )
        iss_data = iss_resp.json()
        astro_data = astro_resp.json()
        iss_pos = iss_data.get("iss_position", {})
        people = astro_data.get("people", [])
        return jsonify(
            {
                "iss_lat": float(iss_pos.get("latitude", 0)),
                "iss_lon": float(iss_pos.get("longitude", 0)),
                "astronauts": astro_data.get("number", 0),
                "astronaut_names": [p.get("name", "") for p in people],
            }
        )
    except Exception as e:
        return jsonify({"iss_lat": 0, "iss_lon": 0, "astronauts": 0, "astronaut_names": [], "error": str(e)})


# ─── World Clocks ────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/global-time")
@require_auth
@ttl_cache(10)
async def global_time():
    now = datetime.now(UTC)
    zones = [
        ("London", "Europe/London"),
        ("New York", "America/New_York"),
        ("Tokyo", "Asia/Tokyo"),
        ("Dubai", "Asia/Dubai"),
        ("Sydney", "Australia/Sydney"),
    ]
    clocks = []
    for label, tz_name in zones:
        try:
            import zoneinfo

            tz = zoneinfo.ZoneInfo(tz_name)
            local = now.astimezone(tz)
            offset = local.strftime("%z")
            offset_fmt = f"UTC{offset[:3]}:{offset[3:]}" if offset else "UTC"
            clocks.append(
                {
                    "zone": label,
                    "time": local.strftime("%H:%M"),
                    "offset": offset_fmt,
                }
            )
        except Exception:
            clocks.append({"zone": label, "time": "--:--", "offset": ""})
    return jsonify({"clocks": clocks})


# ─── CVEs ────────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/cve")
@require_auth
@ttl_cache(600)
async def cve():
    try:
        start = (datetime.now(UTC) - timedelta(days=3)).strftime("%Y-%m-%dT00:00:00.000")
        url = (
            f"https://services.nvd.nist.gov/rest/json/cves/2.0"
            f"?pubStartDate={start}&pubEndDate={datetime.now(UTC).strftime('%Y-%m-%dT23:59:59.999')}"
            f"&resultsPerPage=8&cvssScore=7"
        )
        client = get_async_client()
        resp = await client.get(url, timeout=10)
        data = resp.json()
        vulns = data.get("vulnerabilities", [])
        items = []
        for v in vulns[:6]:
            cve = v.get("cve", {})
            metrics = cve.get("metrics", {})
            cvss = (metrics.get("cvssMetricV31", [{}])[0] or metrics.get("cvssMetricV30", [{}])[0] or {}).get(
                "cvssData", {}
            )
            score = cvss.get("baseScore", 0)
            sev = cvss.get("baseSeverity", "UNKNOWN")
            items.append(
                {
                    "id": cve.get("id", ""),
                    "severity": sev,
                    "score": score,
                    "description": (cve.get("descriptions", [{}])[0] or {}).get("value", ""),
                    "published": cve.get("published", ""),
                }
            )
        return jsonify({"cve": items})
    except Exception as e:
        return jsonify({"cve": [], "error": str(e)})


# ─── Screen Capture ──────────────────────────────────────────────
_SCREEN_CACHE: tuple[float, dict] | None = None
_SCREEN_TTL = 2.0


@app.route(f"{API_PREFIX}/screen")
@require_auth
async def screen_capture():
    global _SCREEN_CACHE
    now = time.time()
    if _SCREEN_CACHE and now - _SCREEN_CACHE[0] < _SCREEN_TTL:
        return jsonify(_SCREEN_CACHE[1])
    try:
        from PIL import ImageGrab

        img = await asyncio.to_thread(ImageGrab.grab)
        buf = io.BytesIO()
        await asyncio.to_thread(lambda: img.save(buf, format="PNG", optimize=True))
        b64 = base64.b64encode(buf.getvalue()).decode()
        result = {"image": b64, "width": img.width, "height": img.height, "timestamp": now}
        _SCREEN_CACHE = (now, result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Memory ──────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/memory", methods=["GET"])
@require_auth
async def memory_list():
    memory = get_memory_manager()
    memories = memory.vector.list_all(limit=50)
    kw_memories = memory.long_term.list_all().get("entries", [])
    emb_memories = memory.embeddings.list_all(limit=50)
    return jsonify(
        {
            "vector_memories": memories,
            "embedding_memories": emb_memories,
            "key_memories": kw_memories,
            "vector_count": memory.vector.count(),
            "embedding_count": memory.embeddings.count(),
            "key_count": len(kw_memories),
        }
    )


@app.route(f"{API_PREFIX}/memory/search", methods=["POST"])
@require_auth
async def memory_search():
    body = await request.get_json()
    query = body.get("query", "")
    if not isinstance(query, str) or not query.strip():
        return jsonify({"results": [], "count": 0})
    top_k = min(int(body.get("top_k", 5)), 50)
    memory = get_memory_manager()
    results = memory.search(query, top_k)
    return jsonify({"results": results, "count": len(results)})


# ─── Knowledge Graph ─────────────────────────────────────────────
@app.route(f"{API_PREFIX}/knowledge", methods=["GET"])
@require_auth
async def knowledge_list():
    from core.knowledge import get_knowledge_graph

    data = get_knowledge_graph().all()
    return jsonify(data)


@app.route(f"{API_PREFIX}/knowledge", methods=["POST"])
@require_auth
async def knowledge_store():
    body = await request.get_json() or {}
    text = body.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "text is required"}), 422
    from core.knowledge import get_knowledge_graph

    added = get_knowledge_graph().store(text)
    return jsonify({"added": added, "count": len(added)})


@app.route(f"{API_PREFIX}/knowledge/query", methods=["POST"])
@require_auth
async def knowledge_query():
    body = await request.get_json() or {}
    term = body.get("term", "")
    if not isinstance(term, str) or not term.strip():
        return jsonify({"results": [], "count": 0})
    from core.knowledge import get_knowledge_graph

    results = get_knowledge_graph().query(term)
    return jsonify({"results": results, "count": len(results)})


@app.route(f"{API_PREFIX}/knowledge/continuity", methods=["GET"])
@require_auth
async def knowledge_continuity():
    from core.knowledge import get_knowledge_graph

    return jsonify({"continuity": get_knowledge_graph().continuity()})


@app.route(f"{API_PREFIX}/computer/status", methods=["GET"])
@require_auth
async def computer_status():
    from core.computer import get_computer_control

    return jsonify(get_computer_control().available)


@app.route(f"{API_PREFIX}/computer/windows", methods=["GET"])
@require_auth
async def computer_windows():
    from core.computer import get_computer_control

    return jsonify(get_computer_control().list_windows())


@app.route(f"{API_PREFIX}/computer/summary", methods=["GET"])
@require_auth
async def computer_summary():
    from core.computer import get_computer_control

    return jsonify(get_computer_control().desktop_summary())


@app.route(f"{API_PREFIX}/plugins", methods=["GET"])
@require_auth
async def list_plugins():
    from core.plugin_store import list_marketplace

    return jsonify({"plugins": list_marketplace()})


@app.route(f"{API_PREFIX}/plugins/install", methods=["POST"])
@require_auth
async def install_plugin_api():
    data = await request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 422
    from core.plugin_store import install_plugin

    result = install_plugin(name)
    if not result.get("success"):
        return jsonify(result), 404
    return jsonify(result)


@app.route(f"{API_PREFIX}/plugins/uninstall", methods=["POST"])
@require_auth
async def uninstall_plugin_api():
    data = await request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 422
    from core.plugin_store import uninstall_plugin

    result = uninstall_plugin(name)
    if not result.get("success"):
        return jsonify(result), 404
    return jsonify(result)


# ─── Google Auth ─────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/auth/google")
@require_auth
async def google_auth():
    from core.auth.google import get_auth_url, is_authenticated

    if is_authenticated():
        return jsonify({"status": "authenticated"})
    redirect = f"http://localhost:8080{API_PREFIX}/auth/google/callback"
    url = get_auth_url(redirect)
    if not url:
        return jsonify({"status": "missing_credentials", "message": "Put google_credentials.json in memory_store/"})
    return jsonify({"status": "needs_auth", "url": url})


@app.route(f"{API_PREFIX}/auth/google/callback")
async def google_auth_callback():
    from core.auth.google import handle_callback

    code = request.args.get("code", "")
    state = request.args.get("state", "")
    redirect = f"http://localhost:8080{API_PREFIX}/auth/google/callback"
    ok = handle_callback(code, state, redirect)
    if ok:
        return "<html><body><h3>Authenticated!</h3><p>You can close this tab and return to Friday.</p><script>window.close()</script></body></html>"
    return "<html><body><p>Auth failed.</p></body></html>", 400


# ─── Calendar ────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/calendar/events")
@require_auth
@ttl_cache(120)
async def calendar_events():
    try:
        from core.auth.google import get_calendar_service, is_authenticated

        if not is_authenticated():
            return jsonify({"events": [], "error": "not_authenticated"})
        from datetime import datetime, timedelta

        service = get_calendar_service()
        now = datetime.now(UTC).isoformat()
        later = (datetime.now(UTC) + timedelta(days=7)).isoformat()
        events = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                timeMax=later,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        items = []
        for e in events.get("items", []):
            start = e["start"].get("dateTime", e["start"].get("date", ""))
            end = e["end"].get("dateTime", e["end"].get("date", ""))
            items.append(
                {
                    "summary": e.get("summary", ""),
                    "start": start,
                    "end": end,
                    "location": e.get("location", ""),
                }
            )
        return jsonify({"events": items, "count": len(items)})
    except Exception as ex:
        return jsonify({"events": [], "error": str(ex)})


# ─── Email ───────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/email/inbox")
@require_auth
@ttl_cache(60)
async def email_inbox():
    try:
        from core.auth.google import get_gmail_service, is_authenticated

        if not is_authenticated():
            return jsonify({"messages": [], "error": "not_authenticated"})
        service = get_gmail_service()
        results = service.users().messages().list(userId="me", maxResults=10).execute()
        messages = []
        for msg in results.get("messages", []):
            meta = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata", metadataHeaders=["From", "Subject", "Date"])
                .execute()
            )
            headers = {h["name"]: h["value"] for h in meta.get("payload", {}).get("headers", [])}
            messages.append(
                {
                    "id": msg["id"],
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "snippet": meta.get("snippet", ""),
                }
            )
        return jsonify({"messages": messages, "count": len(messages)})
    except Exception as ex:
        return jsonify({"messages": [], "error": str(ex)})


@app.route(f"{API_PREFIX}/email/unread")
@require_auth
@ttl_cache(30)
async def email_unread():
    try:
        from core.auth.google import get_gmail_service, is_authenticated

        if not is_authenticated():
            return jsonify({"unread": 0})
        service = get_gmail_service()
        results = service.users().messages().list(userId="me", q="is:unread", maxResults=0).execute()
        return jsonify({"unread": results.get("resultSizeEstimate", 0)})
    except Exception as ex:
        return jsonify({"unread": 0, "error": str(ex)})


@app.route(f"{API_PREFIX}/memory", methods=["DELETE"])
@require_auth
async def memory_clear():
    memory = get_memory_manager()
    memory.vector.clear()
    return jsonify({"success": True, "message": "Vector memory cleared"})


@app.route(f"{API_PREFIX}/memory/<entry_id>", methods=["DELETE"])
@require_auth
async def memory_delete(entry_id: str):
    memory = get_memory_manager()
    result = memory.delete_entry(entry_id)
    return jsonify(result), 200 if result["success"] else 404


# ─── Unified SSE Events ─────────────────────────────────────────
@app.route(f"{API_PREFIX}/events")
async def event_stream():
    if _API_SECRET:
        key = request.args.get("key", "") or request.headers.get("X-API-Key", "")
        if key != _API_SECRET:
            return jsonify({"error": "Unauthorized"}), 401
    queue = await _broadcaster.subscribe()

    async def generate():
        try:
            while True:
                msg = await queue.get()
                yield f"data: {msg}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            await _broadcaster.unsubscribe(queue)

    return Response(generate(), mimetype="text/event-stream")


# ─── Briefing ─────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/briefing")
@require_auth
async def get_briefing():
    engine = BriefingEngine(client=get_async_client())
    briefing = await engine.synthesize()
    return jsonify(
        {
            "greeting": briefing.greeting,
            "summary": briefing.summary,
            "sections": briefing.sections,
            "timestamp": briefing.timestamp,
        }
    )


async def _push_briefing():
    await asyncio.sleep(5)
    engine = BriefingEngine(client=get_async_client())
    last_briefing_date = None
    while True:
        try:
            today = datetime.now(UTC).date()
            if last_briefing_date != today:
                briefing = await engine.synthesize()
                await _broadcaster.broadcast(
                    "briefing",
                    {
                        "summary": briefing.summary,
                        "sections": briefing.sections,
                        "greeting": briefing.greeting,
                        "yesterday": _diary.morning_note(),
                    },
                )
                last_briefing_date = today
        except Exception:
            pass
        await asyncio.sleep(300)


# ─── Diary ────────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/diary")
@require_auth
async def get_diary_page():
    day = request.args.get("date")
    if day:
        try:
            from datetime import date as date_cls

            date_cls.fromisoformat(day)
        except ValueError:
            return jsonify({"error": "invalid date"}), 422
    return jsonify({"date": day or str(date.today()), "content": _diary.read(date.fromisoformat(day) if day else None)})


@app.route(f"{API_PREFIX}/diary/recent")
@require_auth
async def get_diary_recent():
    return jsonify({"days": _diary.recent()})


@app.route(f"{API_PREFIX}/diary/nightly", methods=["POST"])
@require_auth
async def post_diary_nightly():
    path = _diary.write_day_entry()
    return jsonify({"path": path, "success": True})


async def _push_nightly_digest():
    await asyncio.sleep(15)
    last_write = None
    while True:
        try:
            today = datetime.now(UTC).date()
            if last_write != today:
                today_page = _diary.read()
                if "nightly digest" not in today_page.lower():
                    _diary.write_day_entry()
                    await _broadcaster.broadcast("diary", {"date": today.isoformat(), "status": "written"})
                last_write = today
        except Exception:
            pass
        await asyncio.sleep(3600)


# ─── Automations ─────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/automations", methods=["GET"])
@require_auth
async def list_automations():
    engine = get_automation_engine()
    autos = [a.to_dict() for a in engine.list_all()]
    return jsonify({"automations": autos})


@app.route(f"{API_PREFIX}/automations", methods=["POST"])
@require_auth
async def create_automation():
    data = await request.get_json() or {}
    name = data.get("name", "").strip()
    trigger_type = data.get("trigger_type", "")
    trigger_config = data.get("trigger_config", {})
    action = data.get("action", "")
    action_params = data.get("action_params", {})
    if not name or trigger_type not in ("cron", "threshold", "event") or not action:
        return jsonify({"error": "name, trigger_type, and action are required"}), 422
    engine = get_automation_engine()
    auto = engine.create(name, trigger_type, trigger_config, action, action_params)
    return jsonify(auto.to_dict()), 201


@app.route(f"{API_PREFIX}/automations/<auto_id>", methods=["GET"])
@require_auth
async def get_automation(auto_id):
    engine = get_automation_engine()
    auto = engine.get(auto_id)
    if not auto:
        return jsonify({"error": "automation not found"}), 404
    return jsonify(auto.to_dict())


@app.route(f"{API_PREFIX}/automations/<auto_id>", methods=["PUT"])
@require_auth
async def update_automation(auto_id):
    data = await request.get_json() or {}
    engine = get_automation_engine()
    auto = engine.update(auto_id, **data)
    if not auto:
        return jsonify({"error": "automation not found"}), 404
    return jsonify(auto.to_dict())


@app.route(f"{API_PREFIX}/automations/<auto_id>", methods=["DELETE"])
@require_auth
async def delete_automation(auto_id):
    engine = get_automation_engine()
    if engine.delete(auto_id):
        return jsonify({"status": "deleted"})
    return jsonify({"error": "automation not found"}), 404


@app.route(f"{API_PREFIX}/automations/<auto_id>/toggle", methods=["POST"])
@require_auth
async def toggle_automation(auto_id):
    engine = get_automation_engine()
    auto = engine.toggle(auto_id)
    if not auto:
        return jsonify({"error": "automation not found"}), 404
    return jsonify(auto.to_dict())


@app.route(f"{API_PREFIX}/automations/<auto_id>/trigger", methods=["POST"])
@require_auth
async def trigger_automation(auto_id):
    engine = get_automation_engine()
    auto = engine.get(auto_id)
    if not auto:
        return jsonify({"error": "automation not found"}), 404
    result = engine.execute(auto)
    engine.record_run(auto_id, "success" if result.get("type") != "error" else "error")
    return jsonify(result)


async def _push_automations():
    await asyncio.sleep(10)
    engine = get_automation_engine()
    last_check: dict[str, float] = {}
    while True:
        await asyncio.sleep(30)
        try:
            for auto in engine.list_all():
                if not auto.enabled:
                    continue
                if auto.trigger_type == "cron" and engine.should_fire_cron(auto.id, last_check):
                    last_check[auto.id] = time.time()
                    result = engine.execute(auto)
                    status = "success" if result.get("type") != "error" else "error"
                    engine.record_run(auto.id, status)
                    await _broadcaster.broadcast(
                        "automation_run",
                        {
                            "id": auto.id,
                            "name": auto.name,
                            "status": status,
                            "result": result,
                            "timestamp": time.time(),
                        },
                    )
        except Exception:
            pass


# ─── Vision ──────────────────────────────────────────────────────
@app.route(f"{API_PREFIX}/vision/screen")
@require_auth
async def vision_screen():
    engine = get_vision_engine()
    result = await asyncio.to_thread(engine.describe_screen)
    return jsonify(result)


@app.route(f"{API_PREFIX}/vision/analyze", methods=["POST"])
@require_auth
async def vision_analyze():
    data = await request.get_json() or {}
    image = data.get("image", "")
    prompt = data.get("prompt")
    if not image:
        return jsonify({"error": "image (base64) is required"}), 422
    engine = get_vision_engine()
    loop = asyncio.get_event_loop()
    description = await loop.run_in_executor(None, engine.analyze_image, image, prompt)
    text = await loop.run_in_executor(None, engine.extract_text, image)
    return jsonify(
        {
            "description": description,
            "text": text,
            "timestamp": time.time(),
        }
    )


async def _push_vision():
    await asyncio.sleep(15)
    engine = get_vision_engine()
    while True:
        await asyncio.sleep(15)
        try:
            if engine.screen_changed_since_last_check():
                result = await asyncio.to_thread(engine.describe_screen)
                await _broadcaster.broadcast(
                    "vision",
                    {
                        "description": result.get("description", ""),
                        "text": result.get("text"),
                        "timestamp": result.get("timestamp", time.time()),
                    },
                )
        except Exception:
            pass


async def _push_metrics():
    while True:
        await asyncio.sleep(5)
        try:
            data = get_metrics()
            durations = data.get("avg_tool_duration_ms", {})
            vals = [v for v in durations.values() if isinstance(v, (int, float))]
            avg_latency = round(sum(vals) / len(vals)) if vals else 0
            await _broadcaster.broadcast(
                "metrics",
                {
                    "latency": avg_latency,
                    "tokenUsage": data.get("tokens_used", 0),
                    "llm_calls": data.get("llm_calls", 0),
                    "failures": data.get("failures", 0),
                },
            )
        except Exception:
            pass


async def _push_system_info():
    while True:
        await asyncio.sleep(30)
        try:
            metrics = get_metrics()
            await _broadcaster.broadcast(
                "system_info",
                {
                    "hostname": platform.node(),
                    "os": f"{platform.system()} {platform.release()}",
                    "cpu_cores": os.cpu_count(),
                    "python_version": sys.version.split()[0],
                    "uptime_seconds": metrics.get("uptime_seconds", 0),
                    "llm_calls": metrics.get("llm_calls", 0),
                    "tokens_used": metrics.get("tokens_used", 0),
                    "failures": metrics.get("failures", 0),
                    "retries": metrics.get("retries", 0),
                    "model": "openrouter/free",
                    "provider": "OpenRouter",
                },
            )
        except Exception:
            pass


async def _push_memory():
    while True:
        await asyncio.sleep(15)
        try:
            memory = get_memory_manager()
            data = {
                "vector_count": memory.vector.count(),
                "embedding_count": memory.embeddings.count(),
                "key_count": len(memory.long_term.list_all().get("entries", [])),
            }
            await _broadcaster.broadcast("memory", data)
        except Exception:
            pass


async def _push_alerts():
    pm = get_proactive()
    sent = set()
    while True:
        await asyncio.sleep(2)
        try:
            alerts = await pm.get_alerts()
            for a in alerts:
                key = f"{a.timestamp}-{a.title}"
                if key not in sent:
                    sent.add(key)
                    if len(sent) > 200:
                        sent.clear()
                    await _broadcaster.broadcast("alert", a.to_dict())
        except Exception:
            pass


async def _push_screen():
    while True:
        await asyncio.sleep(3)
        try:
            from PIL import ImageGrab

            img = await asyncio.to_thread(ImageGrab.grab)
            buf = io.BytesIO()
            await asyncio.to_thread(lambda: img.save(buf, format="PNG", optimize=True))
            b64 = base64.b64encode(buf.getvalue()).decode()
            await _broadcaster.broadcast(
                "screen",
                {
                    "image": b64,
                    "width": img.width,
                    "height": img.height,
                    "timestamp": time.time(),
                },
            )
        except Exception:
            pass


async def _push_clocks():
    while True:
        await asyncio.sleep(30)
        try:
            now = datetime.now(UTC)
            zones = [
                ("London", "Europe/London"),
                ("New York", "America/New_York"),
                ("Tokyo", "Asia/Tokyo"),
                ("Dubai", "Asia/Dubai"),
                ("Sydney", "Australia/Sydney"),
            ]
            clocks = []
            for label, tz_name in zones:
                try:
                    import zoneinfo

                    tz = zoneinfo.ZoneInfo(tz_name)
                    local = now.astimezone(tz)
                    offset = local.strftime("%z")
                    offset_fmt = f"UTC{offset[:3]}:{offset[3:]}" if offset else "UTC"
                    clocks.append({"zone": label, "time": local.strftime("%H:%M"), "offset": offset_fmt})
                except Exception:
                    clocks.append({"zone": label, "time": "--:--", "offset": ""})
            await _broadcaster.broadcast("clocks", {"clocks": clocks})
        except Exception:
            pass


# ─── Background loops ────────────────────────────────────────────
async def _memory_consolidation_loop():
    while True:
        try:
            await asyncio.sleep(300)
            memory = get_memory_manager()
            memory.run_maintenance()
        except Exception:
            pass


async def _proactive_loop():
    try:
        get_proactive()
    except Exception:
        pass


if __name__ == "__main__":
    from core.memory.embeddings import SentenceEngine

    SentenceEngine.start_background_load()

    import hypercorn.asyncio
    from hypercorn.config import Config

    cfg = Config()
    cfg.bind = ["127.0.0.1:8080"]
    cfg.keep_alive_timeout = 300
    cfg.body_timeout = 300
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(_memory_consolidation_loop())
    loop.create_task(_proactive_loop())
    loop.create_task(_push_metrics())
    loop.create_task(_push_briefing())
    loop.create_task(_push_nightly_digest())
    loop.create_task(_push_automations())
    loop.create_task(_push_vision())
    loop.create_task(_push_system_info())
    loop.create_task(_push_memory())
    loop.create_task(_push_alerts())
    loop.create_task(_push_screen())
    loop.create_task(_push_clocks())
    loop.run_until_complete(hypercorn.asyncio.serve(app, cfg))
