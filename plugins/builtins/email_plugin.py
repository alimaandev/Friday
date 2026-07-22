import base64
from typing import Any

from plugins.base import ToolPlugin


def _decode_body(payload: dict) -> str:
    parts = [payload]
    while parts:
        part = parts.pop(0)
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            data = part["body"]["data"]
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        if "parts" in part:
            parts.extend(part["parts"])
    return ""


class EmailPlugin(ToolPlugin):
    name = "list_emails"
    description = "List recent emails from Gmail inbox. Returns sender, subject, and snippet."
    category = "email"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Max emails to return", "default": 10},
                "query": {"type": "string", "description": "Optional Gmail search query"},
            },
            "required": [],
        }

    def execute(self, max_results: int = 10, query: str = "") -> dict[str, Any]:
        try:
            from core.auth.google import get_gmail_service, is_authenticated
            if not is_authenticated():
                return {"error": "Not authenticated. Run the Google OAuth flow first."}
            service = get_gmail_service()
            results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
            messages = []
            for msg in results.get("messages", []):
                meta = service.users().messages().get(userId="me", id=msg["id"], format="metadata",
                    metadataHeaders=["From", "Subject", "Date"]).execute()
                headers = {h["name"]: h["value"] for h in meta.get("payload", {}).get("headers", [])}
                messages.append({
                    "id": msg["id"],
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "snippet": meta.get("snippet", ""),
                })
            return {"messages": messages, "count": len(messages)}
        except Exception as ex:
            return {"error": str(ex)}


class SendEmailPlugin(ToolPlugin):
    name = "send_email"
    description = "Send an email via Gmail."
    category = "email"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body text"},
            },
            "required": ["to", "subject", "body"],
        }

    def execute(self, to: str, subject: str, body: str) -> dict[str, Any]:
        try:
            from core.auth.google import get_gmail_service, is_authenticated
            if not is_authenticated():
                return {"error": "Not authenticated. Run the Google OAuth flow first."}
            service = get_gmail_service()
            raw = f"To: {to}\r\nSubject: {subject}\r\n\r\n{body}"
            encoded = base64.urlsafe_b64encode(raw.encode()).decode()
            service.users().messages().send(userId="me", body={"raw": encoded}).execute()
            return {"success": True, "to": to, "subject": subject}
        except Exception as ex:
            return {"error": str(ex)}


class GetUnreadCountPlugin(ToolPlugin):
    name = "get_unread_count"
    description = "Get the number of unread emails in Gmail inbox."
    category = "email"

    def get_parameters_schema(self):
        return {"type": "object", "properties": {}, "required": []}

    def execute(self) -> dict[str, Any]:
        try:
            from core.auth.google import get_gmail_service, is_authenticated
            if not is_authenticated():
                return {"error": "Not authenticated"}
            service = get_gmail_service()
            results = service.users().messages().list(userId="me", q="is:unread", maxResults=0).execute()
            count = results.get("resultSizeEstimate", 0)
            return {"unread": count}
        except Exception as ex:
            return {"error": str(ex)}
