# Friday API Reference

Base URL: `http://localhost:8080/api/v1`

All endpoints require `X-API-Key` header if `API_SECRET` is configured. Responses are JSON. Auth failures return `401`.

---

## Core

### `POST /chat` — Streaming chat completion

```json
{ "message": "Hello", "session_id": "default", "persona": "friday" }
```

Returns SSE stream (`text/event-stream`) with events: `plan`, `task_start`, `tokens`, `tool_result`, `task_done`, `fast`, `done`.

### `GET /health` — Server health

```json
{ "status": "ok", "sessions": 1 }
```

### `GET /metrics` — LLM & tool metrics

```json
{ "llm_calls": 42, "tokens_used": 15000, "failures": 0, "avg_tool_duration_ms": { "search": 120 } }
```

---

## Sessions

### `GET /sessions` — List sessions

```json
{ "sessions": [{ "id": "abc123", "language": "english" }] }
```

### `POST /sessions` — Create session

| Field | Type | Default |
|-------|------|---------|
| `language` | `"english"` / `"hinglish"` | `"english"` |

```json
{ "session_id": "abc123", "language": "english" }
```

### `DELETE /sessions/:id` — Delete session

```json
{ "status": "deleted" }
```

---

## Data — Intelligence Panel

All data endpoints are `GET` and return the latest cached data (TTL varies).

| Endpoint | Returns |
|----------|---------|
| `/news` | `{ articles: [{ title, url, source, time, image? }] }` |
| `/weather` | `{ temperature, feels_like, humidity, wind_speed, weather_code, location }` |
| `/stocks?symbols=AAPL,GOOG` | `{ stocks: [{ symbol, price, change, change_pct, sparkline }] }` |
| `/crypto` | `{ crypto: [{ symbol, name, price, change_24h, market_cap }] }` |
| `/github-trending` | `{ repos: [{ name, url, description, stars, language }] }` |
| `/earthquakes` | `{ earthquakes: [{ mag, place, time, depth, url }] }` |
| `/space` | `{ iss_lat, iss_lon, astronauts, astronaut_names }` |
| `/cve` | `{ cve: [{ id, severity, score, description, published }] }` |
| `/global-time` | `{ clocks: [{ zone, time, offset }] }` |

---

## System

### `GET /system-info`

```json
{ "hostname": "my-pc", "os": "Windows", "cpu_cores": 8, "uptime_seconds": 3600, "llm_calls": 42 }
```

### `GET /screen`

Captures the current desktop screen and returns a base64 PNG.

```json
{ "image": "<base64>", "width": 1920, "height": 1080, "timestamp": 1717000000 }
```

### `GET /output-dir?session_id=default`

```json
{ "output_dir": "/home/user/projects" }
```

### `PUT /output-dir`

```json
{ "session_id": "default", "path": "/home/user/projects" }
```

---

## Memory

### `GET /memory`

```json
{ "vector_memories": [...], "key_memories": [...], "vector_count": 5, "key_count": 3 }
```

### `POST /memory/search`

```json
{ "query": "what did I work on", "top_k": 5 }
```

```json
{ "results": [{ "text": "...", "score": 0.85 }], "count": 3 }
```

### `DELETE /memory`

Clears all memory.

```json
{ "status": "cleared", "cleared_vectors": 5, "cleared_keys": 3 }
```

---

## Google Calendar & Email

### `GET /auth/google`

Returns OAuth URL. On callback, tokens are stored server-side.

```json
{ "url": "https://accounts.google.com/o/oauth2/auth?...", "status": "pending" }
```

After successful auth, subsequent calls return:

```json
{ "status": "authenticated" }
```

### `GET /calendar/events`

```json
{ "events": [{ "summary": "Meeting", "start": "2024-01-01T10:00", "end": "..." }] }
```

### `GET /email/inbox`

```json
{ "messages": [{ "id": "...", "from": "alice@...", "subject": "...", "date": "...", "snippet": "..." }] }
```

### `GET /email/unread`

```json
{ "unread": 5 }
```

---

## Alerts

### `GET /alerts`

```json
{ "alerts": [{ "type": "screen_change", "title": "...", "description": "...", "severity": "info", "timestamp": 1717000000 }], "count": 3 }
```

---

## Autopilot

### `POST /autopilot` — Decompose & run a goal

| Field | Type | Required |
|-------|------|----------|
| `goal` | string | ✅ |

```json
{ "message": "organize my desktop and summarize" }
```

Executes a goal as a multi-step plan; emits SSE `plan` / `task_start` / `task_done` / `done` events on the chat stream.

---

## Knowledge Graph

### `GET /knowledge` — List entities & relations

```json
{ "entities": [{ "id": "...", "name": "Alice", "type": "person", "mentions": 5 }], "relations": [{ "source": "...", "target": "...", "type": "works_with" }] }
```

### `POST /knowledge` — Extract entities from text

| Field | Type | Required |
|-------|------|----------|
| `text` | string | ✅ |

```json
{ "extracted": [{ "name": "Alice", "type": "person" }] }
```

### `POST /knowledge/query` — Semantic graph query

```json
{ "query": "what projects does Alice work on", "top_k": 5 }
```

```json
{ "results": [{ "entity": "Alice", "relation": "works_on", "target": "Friday", "score": 0.9 }], "count": 2 }
```

### `GET /knowledge/continuity` — Session continuity context

```json
{ "context": "Last time you were working on the autopilot engine...", "entities": ["autopilot", "diary"] }
```

---

## Computer Control

All control actions require user confirmation first (security gate). On non-Windows / headless systems, missing `pyautogui`/`pywin32` degrade gracefully.

### `GET /computer/status`

```json
{ "platform": "Windows", "mouse_keyboard": true, "window_management": true }
```

### `GET /computer/windows`

```json
{ "windows": [{ "title": "Friday — VS Code", "handle": 123456 }] }
```

### `GET /computer/summary`

```json
{ "desktop": { "platform": "Windows", "window_count": 4, "suggestions": ["open vscode", "close terminal"] } }
```

---

## Plugin Marketplace

### `GET /plugins` — List installed + available

```json
{ "installed": [{ "name": "computer_control", "version": "1.0.0" }], "marketplace": [{ "name": "fun", "description": "...", "version": "1.0.0", "installed": false }] }
```

### `POST /plugins/install`

| Field | Type | Required |
|-------|------|----------|
| `name` | string | ✅ |

### `POST /plugins/uninstall`

| Field | Type | Required |
|-------|------|----------|
| `name` | string | ✅ |

---

## Custom Tools

### `GET /tools/custom` — List built tools

### `POST /tools/custom` — Build a tool from natural language

| Field | Type | Required |
|-------|------|----------|
| `description` | string | ✅ |

```json
{ "name": "get_weather", "description": "Fetches weather for a city", "status": "created" }
```

### `DELETE /tools/custom/<name>` — Remove a tool

---

## Local RAG

### `POST /rag/ingest`

| Field | Type | Required |
|-------|------|----------|
| `text` | string | ✅ |
| `source` | string | |

```json
{ "status": "ingested", "chunks": 12, "source": "notes.txt" }
```

### `POST /rag/search`

| Field | Type | Required |
|-------|------|----------|
| `query` | string | ✅ |
| `top_k` | int | |

```json
{ "results": [{ "text": "...", "score": 0.91, "source": "notes.txt" }], "count": 3 }
```

---

## Privacy / Blackout

### `GET /privacy`

```json
{ "blackout": false, "network_tools_blocked": 0, "local_provider": "ollama" }
```

### `POST /privacy`

| Field | Type | Description |
|-------|------|-------------|
| `blackout` | bool | Enable/disable local-only mode |

```json
{ "blackout": true }
```

---

## Briefing

### `GET /briefing`

Morning Pulse template-based briefing (zero LLM cost).

```json
{ "greeting": "Good morning!", "summary": "...", "sections": ["Weather: 22°C...", "News: ..."], "timestamp": 1717000000 }
```

---

## Automations

### `GET /automations` — List all

```json
{ "automations": [{ "id": "abc", "name": "Morning Briefing", "trigger_type": "cron", "trigger_config": { "cron": "0 8 * * *" }, "action": "briefing", "enabled": true, ... }] }
```

### `POST /automations` — Create

| Field | Type | Required |
|-------|------|----------|
| `name` | string | ✅ |
| `trigger_type` | `"cron"` / `"threshold"` / `"event"` | ✅ |
| `trigger_config` | object | ✅ |
| `action` | `"notification"` / `"briefing"` / `"tool_call"` | ✅ |
| `action_params` | object | |

```json
{ "id": "abc", "name": "Morning Briefing", ... }
```

### `GET /automations/:id` — Get one

### `PUT /automations/:id` — Update

Any subset of fields.

### `DELETE /automations/:id` — Delete

```json
{ "status": "deleted" }
```

### `POST /automations/:id/toggle` — Enable/disable

```json
{ "id": "abc", "enabled": false, ... }
```

### `POST /automations/:id/trigger` — Run now

```json
{ "type": "briefing", "source": "automation" }
```

---

## Vision

### `GET /vision/screen` — Capture + describe screen

```json
{ "description": "The screen shows VS Code with a Python file...", "text": "def hello():...", "width": 1920, "height": 1080, "timestamp": 1717000000 }
```

### `POST /vision/analyze` — Analyze an arbitrary image

| Field | Type | Required |
|-------|------|----------|
| `image` | string (base64 PNG) | ✅ |
| `prompt` | string (optional, defaults to "Describe what you see...") | |

```json
{ "description": "A person sitting at a desk...", "text": null, "timestamp": 1717000000 }
```

---

## Real-time Events (SSE)

### `GET /events` — Server-Sent Events stream

```
Cache-Control: no-cache
Content-Type: text/event-stream

data: {"type":"metrics","data":{"latency":42}}

data: {"type":"system_info","data":{"hostname":"my-pc"}}
...
```

Event types:

| Event | Data | Interval |
|-------|------|----------|
| `metrics` | `{ latency, tokenUsage, llm_calls, failures }` | 5s |
| `system_info` | `{ hostname, os, cpu_cores, uptime_seconds, model }` | 30s |
| `memory` | `{ vector_count, key_count, ... }` | 10s |
| `screen` | `{ image, width, height, timestamp }` | 3s |
| `alerts` | `{ type, title, description, severity }` | on change |
| `clocks` | `{ clocks: [...] }` | 60s |
| `briefing` | `{ summary, sections, greeting }` | daily on first load |
| `automation_run` | `{ id, name, status, result }` | on trigger |
| `vision` | `{ description, text, timestamp }` | on screen change (every 15s) |

Auth via query param: `GET /events?key=YOUR_API_SECRET`
