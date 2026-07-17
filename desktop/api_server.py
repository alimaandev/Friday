"""Local API server for Friday desktop - streams Agent events via SSE"""
import sys, json, asyncio, uuid, os, platform, re, time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from functools import wraps

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.registry import discover_plugins
from core.logger import get_metrics
from agent.core import Agent
from quart import Quart, request, Response, jsonify
from quart_cors import cors

"""TTL cache — stores endpoint results in-memory so repeated polling is instant"""
_cache: dict[str, tuple[float, any]] = {}

def ttl_cache(seconds: int = 60):
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            key = f.__name__ + str(request.query_string.decode())
            now = time.monotonic()
            if key in _cache:
                expire, data = _cache[key]
                if now < expire:
                    return jsonify(data)
            result = await f(*args, **kwargs)
            if isinstance(result, tuple):
                body, status = result
                if status == 200 and body is not None:
                    _cache[key] = (now + seconds, body)
                return result
            if hasattr(result, 'status_code') and result.status_code == 200:
                try:
                    data = await result.get_json()
                    _cache[key] = (now + seconds, data)
                except: pass
            return result
        return wrapper
    return decorator

app = Quart(__name__)
app = cors(app, allow_origin="*", allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

discover_plugins()

_agents: dict[str, Agent] = {}


def _get_agent(session_id: str) -> Agent:
    if session_id not in _agents:
        _agents[session_id] = Agent()
    return _agents[session_id]


@app.route('/api/chat', methods=['POST'])
async def chat():
    data = await request.get_json()
    user_input = data.get('message', '')
    session_id = data.get('session_id', 'default')
    agent = _get_agent(session_id)

    async def generate():
        try:
            for event in agent.run(user_input):
                yield json.dumps(event, ensure_ascii=False) + '\n'
                await asyncio.sleep(0)
        except Exception as e:
            yield json.dumps({"type": "done", "content": f"Error: {e}", "final": True}) + '\n'

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/sessions', methods=['GET'])
async def list_sessions():
    return jsonify({
        "sessions": [
            {"id": sid, "language": a.language}
            for sid, a in _agents.items()
        ]
    })

@app.route('/api/sessions', methods=['POST'])
async def create_session():
    data = await request.get_json() or {}
    session_id = str(uuid.uuid4())[:8]
    lang = data.get("language", "english")
    _agents[session_id] = Agent(language=lang)
    return jsonify({"session_id": session_id, "language": lang}), 201

@app.route('/api/sessions/<session_id>', methods=['DELETE'])
async def delete_session(session_id):
    _agents.pop(session_id, None)
    return jsonify({"status": "deleted"})

@app.route('/api/output-dir', methods=['PUT'])
async def set_output_dir():
    data = await request.get_json()
    session_id = data.get('session_id', 'default')
    path = data.get('path', '')
    agent = _get_agent(session_id)
    agent.set_output_dir(path or None)
    return jsonify({"status": "ok", "output_dir": path})

@app.route('/api/output-dir', methods=['GET'])
async def get_output_dir():
    session_id = request.args.get('session_id', 'default')
    agent = _get_agent(session_id)
    return jsonify({"output_dir": agent.output_dir or ""})

@app.route('/api/metrics')
async def metrics():
    return jsonify(get_metrics())

@app.route('/api/health')
async def health():
    return jsonify({"status": "ok", "sessions": len(_agents)})

@app.route('/api/system-info')
@ttl_cache(30)
async def system_info():
    metrics = get_metrics()
    return jsonify({
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
    })

_NEWS_RSS = [
    "https://hnrss.org/frontpage",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "http://feeds.bbci.co.uk/news/rss.xml",
]


@app.route('/api/news')
@ttl_cache(300)
async def news():
    items = []
    for url in _NEWS_RSS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Friday/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                root = ET.fromstring(resp.read())
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
                        import re
                        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
                        if m:
                            img = m.group(1)
                    items.append({
                        "title": title,
                        "url": link,
                        "image": img,
                        "source": url.split("/")[2],
                        "time": pub,
                    })
        except Exception:
            continue
    return jsonify({"articles": items})

_WEATHER_LAT = 33.68
_WEATHER_LON = 73.05
_WEATHER_LOCATION = "Islamabad"


@app.route('/api/weather')
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
        req = urllib.request.Request(url, headers={"User-Agent": "Friday/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        cur = data.get("current", {})
        return jsonify({
            "temperature": cur.get("temperature_2m"),
            "feels_like": cur.get("apparent_temperature"),
            "humidity": cur.get("relative_humidity_2m"),
            "wind_speed": cur.get("wind_speed_10m"),
            "weather_code": cur.get("weather_code", 0),
            "location": request.args.get("location", _WEATHER_LOCATION),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route('/api/stocks')
@ttl_cache(60)
async def stocks():
    symbols = request.args.get("symbols", "AAPL,GOOG,MSFT,NVDA,BTC-USD")
    try:
        import yfinance as yf
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
                results.append({
                    "symbol": sym.upper(),
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "sparkline": [round(v, 2) for v in close],
                })
            except Exception:
                results.append({"symbol": sym.upper(), "price": 0, "change": 0, "change_pct": 0, "sparkline": []})
        return jsonify({"stocks": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route('/api/github-trending')
@ttl_cache(300)
async def github_trending():
    try:
        req = urllib.request.Request(
            "https://github.com/trending",
            headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8")
        repos = []
        for article in re.findall(r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>', html, re.DOTALL)[:10]:
            h = re.search(r'href="/([^/"]+/[^/"]+)"', article)
            full_name = h.group(1) if h else ""
            desc_m = re.search(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', article, re.DOTALL)
            desc = desc_m.group(1).strip() if desc_m else ""
            desc = re.sub(r'<[^>]+>', '', desc).strip()
            star_m = re.search(r'<span[^>]*class="[^"]*d-inline-block[^"]*"[^>]*>.*?(\d[\d,]*)\s*</span>', article)
            stars = star_m.group(1).replace(",", "") if star_m else "0"
            lang_m = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>', article)
            lang = lang_m.group(1).strip() if lang_m else ""
            repos.append({
                "name": full_name,
                "url": f"https://github.com/{full_name}",
                "description": desc,
                "stars": int(stars) if stars.isdigit() else 0,
                "language": lang,
            })
        return jsonify({"repos": repos})
    except Exception as e:
        return jsonify({"error": str(e)}), 502


@app.route('/api/earthquakes')
@ttl_cache(120)
async def earthquakes():
    try:
        req = urllib.request.Request(
            "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson",
            headers={"User-Agent": "Friday/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
        items = []
        for f in data.get("features", [])[:8]:
            props = f.get("properties", {})
            coords = f.get("geometry", {}).get("coordinates", [0, 0, 0])
            items.append({
                "mag": props.get("mag", 0),
                "place": props.get("place", "Unknown"),
                "time": datetime.fromtimestamp(props.get("time", 0) / 1000, tz=timezone.utc).isoformat(),
                "depth": round(coords[2], 1),
                "url": props.get("url", ""),
            })
        return jsonify({"earthquakes": items})
    except Exception as e:
        return jsonify({"earthquakes": [], "error": str(e)})


@app.route('/api/crypto')
@ttl_cache(120)
async def crypto():
    try:
        req = urllib.request.Request(
            "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=6&sparkline=false",
            headers={"User-Agent": "Friday/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
        coins = []
        for c in data:
            coins.append({
                "symbol": c.get("symbol", "").upper(),
                "name": c.get("name", ""),
                "price": round(c.get("current_price", 0), 2),
                "change_24h": round(c.get("price_change_percentage_24h", 0), 1),
                "market_cap": c.get("market_cap", 0),
            })
        return jsonify({"crypto": coins})
    except Exception as e:
        return jsonify({"crypto": [], "error": str(e)})


@app.route('/api/space')
@ttl_cache(60)
async def space():
    try:
        iss_req = urllib.request.Request(
            "http://api.open-notify.org/iss-now.json",
            headers={"User-Agent": "Friday/1.0"},
        )
        with urllib.request.urlopen(iss_req, timeout=5) as resp:
            iss_data = json.loads(resp.read())
        iss_pos = iss_data.get("iss_position", {})
        astro_req = urllib.request.Request(
            "http://api.open-notify.org/astros.json",
            headers={"User-Agent": "Friday/1.0"},
        )
        with urllib.request.urlopen(astro_req, timeout=5) as resp:
            astro_data = json.loads(resp.read())
        people = astro_data.get("people", [])
        return jsonify({
            "iss_lat": float(iss_pos.get("latitude", 0)),
            "iss_lon": float(iss_pos.get("longitude", 0)),
            "astronauts": astro_data.get("number", 0),
            "astronaut_names": [p.get("name", "") for p in people],
        })
    except Exception as e:
        return jsonify({"iss_lat": 0, "iss_lon": 0, "astronauts": 0, "astronaut_names": [], "error": str(e)})


@app.route('/api/global-time')
@ttl_cache(10)
async def global_time():
    now = datetime.now(timezone.utc)
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
            clocks.append({
                "zone": label,
                "time": local.strftime("%H:%M"),
                "offset": offset_fmt,
            })
        except Exception:
            clocks.append({"zone": label, "time": "--:--", "offset": ""})
    return jsonify({"clocks": clocks})


@app.route('/api/cve')
@ttl_cache(600)
async def cve():
    try:
        from datetime import timedelta
        start = (datetime.now(timezone.utc) - timedelta(days=3)).strftime("%Y-%m-%dT00:00:00.000")
        url = (
            f"https://services.nvd.nist.gov/rest/json/cves/2.0"
            f"?pubStartDate={start}&pubEndDate={datetime.now(timezone.utc).strftime('%Y-%m-%dT23:59:59.999')}"
            f"&resultsPerPage=8&cvssScore=7"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Friday/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        vulns = data.get("vulnerabilities", [])
        items = []
        for v in vulns[:6]:
            cve = v.get("cve", {})
            metrics = cve.get("metrics", {})
            cvss = (metrics.get("cvssMetricV31", [{}])[0] or metrics.get("cvssMetricV30", [{}])[0] or {}).get("cvssData", {})
            score = cvss.get("baseScore", 0)
            sev = cvss.get("baseSeverity", "UNKNOWN")
            items.append({
                "id": cve.get("id", ""),
                "severity": sev,
                "score": score,
                "description": (cve.get("descriptions", [{}])[0] or {}).get("value", ""),
                "published": cve.get("published", ""),
            })
        return jsonify({"cve": items})
    except Exception as e:
        return jsonify({"cve": [], "error": str(e)})


if __name__ == '__main__':
    import hypercorn.asyncio
    from hypercorn.config import Config
    cfg = Config()
    cfg.bind = ["127.0.0.1:8080"]
    cfg.keep_alive_timeout = 300
    cfg.body_timeout = 300
    asyncio.run(hypercorn.asyncio.serve(app, cfg))
