import json
import os
import secrets
import time
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

MEMORY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memory_store")
TOKEN_PATH = os.path.join(MEMORY_DIR, "google_token.json")
CREDENTIALS_PATH = os.path.join(MEMORY_DIR, "google_credentials.json")
os.makedirs(MEMORY_DIR, exist_ok=True)

_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

_SERVICE_CACHE: dict[str, Any] = {}
_FLOW_STORE: dict[str, Any] = {}


def is_authenticated() -> bool:
    creds = _load_token()
    return creds is not None and creds.valid


def get_auth_url(redirect_uri: str) -> str | None:
    if not os.path.exists(CREDENTIALS_PATH):
        return None
    flow = Flow.from_client_secrets_file(CREDENTIALS_PATH, scopes=_SCOPES)
    flow.redirect_uri = redirect_uri
    state = secrets.token_urlsafe(16)
    auth_url, _ = flow.authorization_url(
        prompt="consent", access_type="offline",
        state=state, code_challenge_method="S256",
    )
    _FLOW_STORE[state] = {"code_verifier": flow.code_verifier, "redirect_uri": redirect_uri}
    return auth_url


def handle_callback(auth_code: str, state: str, redirect_uri: str) -> bool:
    try:
        stored = _FLOW_STORE.pop(state, None)
        flow = Flow.from_client_secrets_file(CREDENTIALS_PATH, scopes=_SCOPES)
        flow.redirect_uri = redirect_uri
        if stored:
            flow.code_verifier = stored["code_verifier"]
        flow.fetch_token(code=auth_code)
        _save_token(flow.credentials)
        return True
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return False


def _load_token() -> Credentials | None:
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        with open(TOKEN_PATH, "r") as f:
            data = json.load(f)
        creds = Credentials.from_authorized_user_info(data, _SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            _save_token(creds)
        return creds
    except Exception:
        return None


def _save_token(creds: Credentials):
    data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
    }
    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f, indent=2)


def get_service(api_name: str, api_version: str, prefix: str = "calendar"):
    cache_key = f"{api_name}:{api_version}"
    if cache_key in _SERVICE_CACHE:
        return _SERVICE_CACHE[cache_key]
    creds = _load_token()
    if not creds:
        return None
    service = build(api_name, api_version, credentials=creds)
    _SERVICE_CACHE[cache_key] = service
    return service


def get_calendar_service():
    return get_service("calendar", "v3")


def get_gmail_service():
    return get_service("gmail", "v1")
