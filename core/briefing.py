"""Morning Pulse — daily briefing generator that aggregates all data sources."""

import asyncio
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

__all__ = ["Briefing", "BriefingEngine"]


@dataclass
class Briefing:
    greeting: str
    summary: str
    sections: list[str] = field(default_factory=list)
    timestamp: float = 0.0


_WEATHER_LAT = 33.68
_WEATHER_LON = 73.05
_WEATHER_LOCATION = "Islamabad"

_NEWS_RSS = [
    "https://hnrss.org/frontpage",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.bbci.co.uk/news/rss.xml",
]

_STOCK_SYMBOLS = ["AAPL", "GOOG", "MSFT", "NVDA", "BTC-USD"]


class BriefingEngine:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self._client = client or httpx.AsyncClient(timeout=10.0, headers={"User-Agent": "Friday/1.0"})

    async def synthesize(self) -> Briefing:
        data = await asyncio.gather(
            self._get_weather(),
            self._get_news(),
            self._get_crypto(),
            self._get_system_info(),
            return_exceptions=True,
        )
        weather_data, news_data, crypto_data, sys_info = (d if not isinstance(d, Exception) else None for d in data)

        greeting = self._greeting()
        sections: list[str] = []

        cal_text = await self._get_calendar_text()
        if cal_text:
            sections.append(cal_text)

        if weather_data:
            sections.append(self._format_weather(weather_data))

        if news_data:
            sections.append(self._format_news(news_data))

        email_text = await self._get_email_text()
        if email_text:
            sections.append(email_text)

        if crypto_data:
            sections.append(self._format_crypto(crypto_data))

        summary = f"{greeting} {'. '.join(sections)}" if sections else f"{greeting} All clear. No new updates."
        return Briefing(greeting=greeting, summary=summary, sections=sections, timestamp=time.time())

    @staticmethod
    def _greeting() -> str:
        hour = datetime.now(UTC).hour
        if hour < 12:
            return "Good morning."
        if hour < 17:
            return "Good afternoon."
        return "Good evening."

    async def _get_weather(self) -> dict[str, Any] | None:
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={_WEATHER_LAT}&longitude={_WEATHER_LON}"
                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
                f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
                f"&timezone=auto"
            )
            resp = await self._client.get(url, timeout=5)
            data = resp.json()
            cur = data.get("current", {})
            daily = data.get("daily", {})
            return {
                "temperature": cur.get("temperature_2m"),
                "feels_like": cur.get("apparent_temperature"),
                "humidity": cur.get("relative_humidity_2m"),
                "weather_code": cur.get("weather_code", 0),
                "location": _WEATHER_LOCATION,
                "high_today": daily.get("temperature_2m_max", [None])[0] if daily.get("temperature_2m_max") else None,
                "low_today": daily.get("temperature_2m_min", [None])[0] if daily.get("temperature_2m_min") else None,
                "precip_today": daily.get("precipitation_sum", [None])[0] if daily.get("precipitation_sum") else None,
            }
        except Exception:
            return None

    async def _get_news(self) -> list[dict[str, str]] | None:
        try:
            items = []
            for url in _NEWS_RSS:
                resp = await self._client.get(url, timeout=5)
                root = ET.fromstring(resp.content)
                for entry in root.findall(".//item")[:3]:
                    title = entry.findtext("title", "")
                    if title:
                        items.append({"title": title})
            return items[:5]
        except Exception:
            return None

    async def _get_crypto(self) -> list[dict[str, Any]] | None:
        try:
            resp = await self._client.get(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 6, "page": 1},
                timeout=5,
            )
            data = resp.json()
            return [
                {
                    "symbol": c["symbol"].upper(),
                    "name": c["name"],
                    "price": c["current_price"],
                    "change_24h": c["price_change_percentage_24h"],
                }
                for c in data
            ]
        except Exception:
            return None

    async def _get_system_info(self) -> dict[str, Any] | None:
        try:
            import platform as pf

            return {
                "hostname": pf.node(),
                "cpu_cores": os.cpu_count(),
            }
        except Exception:
            return None

    async def _get_calendar_text(self) -> str | None:
        try:
            from core.auth.google import get_calendar_service, is_authenticated

            if not is_authenticated():
                return None
            service = get_calendar_service()
            now = datetime.now(UTC).isoformat()
            later = (datetime.now(UTC) + timedelta(days=1)).isoformat()
            events = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    timeMax=later,
                    maxResults=5,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            items = events.get("items", [])
            if not items:
                return None
            names = [e.get("summary", "Untitled") for e in items[:3]]
            count = len(items)
            if count == 1:
                return f"You have one meeting today: {names[0]}."
            return f"You have {count} meetings today — {', '.join(names[:3])}."
        except Exception:
            return None

    async def _get_email_text(self) -> str | None:
        try:
            from core.auth.google import get_gmail_service, is_authenticated

            if not is_authenticated():
                return None
            service = get_gmail_service()
            results = service.users().messages().list(userId="me", q="is:unread", maxResults=5).execute()
            messages = results.get("messages", [])
            if not messages:
                return None
            urgent = 0
            senders = set()
            for m in messages[:5]:
                msg = service.users().messages().get(userId="me", id=m["id"], format="metadata").execute()
                headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
                subj = headers.get("Subject", "")
                sender = headers.get("From", "").split("<")[0].strip().split("@")[0]
                senders.add(sender)
                urgent_keywords = ["urgent", "important", "asap", "deadline", "action required"]
                if any(k in subj.lower() for k in urgent_keywords):
                    urgent += 1
            if urgent > 0:
                return f"You have {len(messages)} unread emails, {urgent} marked urgent."
            return f"You have {len(messages)} unread emails."
        except Exception:
            return None

    @staticmethod
    def _format_weather(w: dict) -> str:
        codes: dict[int, str] = {
            0: "clear",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            61: "light rain",
            63: "moderate rain",
            65: "heavy rain",
            80: "rain showers",
            95: "thunderstorms",
        }
        cond = codes.get(w.get("weather_code", 0), "unknown")
        temp = w.get("temperature", "?")
        loc = w.get("location", "your area")
        parts = [f"It's {temp}°C and {cond} in {loc}."]
        if w.get("precip_today"):
            parts.append(f"{w['precip_today']}mm rain expected today.")
        return " ".join(parts)

    @staticmethod
    def _format_news(news: list[dict]) -> str:
        if not news:
            return ""
        top = news[0]["title"]
        return f'Top headline: "{top}".'

    @staticmethod
    def _format_crypto(crypto: list[dict]) -> str:
        if not crypto:
            return ""
        movers = [c for c in crypto if c.get("change_24h") and abs(c["change_24h"]) > 1]
        if not movers:
            return ""
        top = movers[0]
        direction = "up" if top["change_24h"] > 0 else "down"
        return f"{top['name']} is {direction} {abs(top['change_24h']):.1f}% at ${top['price']:,.0f}."


import os  # noqa: E402 — used by _get_system_info
