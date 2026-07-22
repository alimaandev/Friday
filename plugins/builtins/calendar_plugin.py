from datetime import datetime, timezone, timedelta
from typing import Any

from plugins.base import ToolPlugin


class CalendarPlugin(ToolPlugin):
    name = "list_events"
    description = "List upcoming Google Calendar events. Returns events with title, start/end time, and description."
    category = "calendar"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Max events to return", "default": 10},
                "days_ahead": {"type": "integer", "description": "How many days ahead to look", "default": 7},
            },
            "required": [],
        }

    def execute(self, max_results: int = 10, days_ahead: int = 7) -> dict[str, Any]:
        try:
            from core.auth.google import get_calendar_service, is_authenticated
            if not is_authenticated():
                return {"error": "Not authenticated. Run the Google OAuth flow first."}
            service = get_calendar_service()
            now = datetime.now(timezone.utc).isoformat()
            later = (datetime.now(timezone.utc) + timedelta(days=days_ahead)).isoformat()
            events = service.events().list(
                calendarId="primary", timeMin=now, timeMax=later,
                maxResults=max_results, singleEvents=True, orderBy="startTime",
            ).execute()
            items = []
            for e in events.get("items", []):
                start = e["start"].get("dateTime", e["start"].get("date", ""))
                end = e["end"].get("dateTime", e["end"].get("date", ""))
                items.append({
                    "summary": e.get("summary", ""),
                    "start": start,
                    "end": end,
                    "description": (e.get("description", "") or "")[:200],
                    "location": e.get("location", ""),
                })
            return {"events": items, "count": len(items)}
        except Exception as ex:
            return {"error": str(ex)}


class CreateEventPlugin(ToolPlugin):
    name = "create_event"
    description = "Create a new event on Google Calendar."
    category = "calendar"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Event title"},
                "start_time": {"type": "string", "description": "Start time in ISO format (e.g. 2026-07-20T14:00:00)"},
                "end_time": {"type": "string", "description": "End time in ISO format"},
                "description": {"type": "string", "description": "Optional description"},
            },
            "required": ["summary", "start_time", "end_time"],
        }

    def execute(self, summary: str, start_time: str, end_time: str, description: str = "") -> dict[str, Any]:
        try:
            from core.auth.google import get_calendar_service, is_authenticated
            if not is_authenticated():
                return {"error": "Not authenticated. Run the Google OAuth flow first."}
            service = get_calendar_service()
            event = {
                "summary": summary,
                "description": description,
                "start": {"dateTime": start_time, "timeZone": "UTC"},
                "end": {"dateTime": end_time, "timeZone": "UTC"},
            }
            created = service.events().insert(calendarId="primary", body=event).execute()
            return {"success": True, "id": created.get("id", ""), "link": created.get("htmlLink", "")}
        except Exception as ex:
            return {"error": str(ex)}
