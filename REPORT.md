# Friday — AI Assistant Software Report

**Date:** July 16, 2026
**Location:** `F:\Projects\Friday`
**Total Codebase:** ~3,380 lines across 47 Python files

---

## 1. Overview

Friday is a modular, extensible AI assistant that uses large language models (LLMs) to understand user goals and execute them through tool calls. It supports multiple LLM providers, browser automation, code analysis, memory systems, voice I/O, task scheduling, and plugin-based extensibility.

---

## 2. Architecture

### 2.1 Execution Flow

```
User Input
    │
    ▼
main.py ──► Agent.run()
                │
                ├─ Planner creates Task list from user goal
                │   (LLM decomposes goal into sub-tasks)
                │
                └─ For each Task:
                    │
                    ├─ Executor runs ReAct loop:
                    │   LLM ↔ Tool execution (browser, files, code, etc.)
                    │   Loops until LLM produces final answer
                    │
                    ├─ Verifier checks if task succeeded
                    │   (LLM decides retry or abort)
                    │
                    └─ Returns final response to user
```

### 2.2 Component Stack

| Layer | Modules | Purpose |
|---|---|---|
| **Entry** | `main.py` | CLI/REPL, voice mode, `/commands` |
| **Orchestration** | `agent/core.py`, `agent/llm.py`, `agent/tools.py` | Agent, LLM wrapper, tool discovery |
| **Core Engine** | `core/planner.py`, `core/executor.py`, `core/verifier.py` | Task decomposition, ReAct execution, verification |
| **Infrastructure** | `core/logger.py`, `core/registry.py`, `core/security.py`, `core/session.py` | Logging, plugin registry, permissions, session export |
| **Task Management** | `core/task_manager.py`, `core/scheduler.py`, `core/workflow.py` | Async tasks, cron jobs, workflow recording |
| **Memory** | `core/memory/` (working, long-term, conversation, semantic) | Key-value store, persistent memory, conversation history, semantic search |
| **Providers** | `providers/ollama.py`, `providers/openai_compat.py` | LLM backends (local Ollama, OpenAI, OpenRouter, LM Studio) |
| **Browser** | `browser/` (6 modules) | Playwright-based web automation |
| **Tools/Plugins** | `tools/` (10 modules), `plugins/builtins/` (12 modules) | ~56 tools spanning browser, filesystem, code, memory, tasks, security |
| **Coding** | `coding/ast_utils.py`, `coding/indexer.py`, `coding/test_runner.py` | AST parsing, project indexing, test/lint/format |
| **Voice** | `voice/stt.py`, `voice/tts.py`, `voice/vad.py` | Speech-to-text, text-to-speech, voice activity detection |
| **Tests** | `tests/` (7 files, 63 tests) | Unit tests for config, logger, memory, planner, registry, security |

### 2.3 Data Flow Detail

```
User: "what year is it? then search web for x"

    Agent.run()
    ├─ Planner.create_plan()
    │   └─ LLM returns: [Task(browse_search), Task(browse_get_page_text)]
    │
    ├─ Executor.execute_task(task_1)
    │   └─ _react_loop():
    │       ├─ LLM(user_msg + tools definitions)
    │       ├─ LLM returns: tool_call(get_current_datetime)
    │       ├─ Executor runs get_current_datetime() → "2026-07-16..."
    │       ├─ Result fed back to messages
    │       ├─ LLM produces: "The current year is 2026"
    │       └─ returns final answer
    │
    ├─ Executor.execute_task(task_2)
    │   └─ _react_loop():
    │       ├─ LLM(history + "search for x") → tool_call(browse_search)
    │       ├─ browse_search runs → page text returned
    │       └─ LLM summarizes result
    │
    └─ yields done
```

---

## 3. Features

### 3.1 LLM Provider Support

| Provider | Backend | Model | Config |
|---|---|---|---|
| **Ollama** | Local | qwen2.5:1.5b (default) | `providers/ollama.py` |
| **OpenAI** | Cloud | gpt-4o-mini | `providers/openai_compat.py` |
| **OpenRouter** | Cloud | openrouter/free (auto-routes) | `providers/openai_compat.py` |
| **LM Studio** | Local | Any loaded model | `providers/openai_compat.py` |

Provider selection via `config/providers.toml` → `[default] provider = "openrouter"`.

### 3.2 Tool System (~56 tools)

**Browser (15):** search, navigate, click (text/role/css/coordinates), type (selector/label), press key, hover, scroll, get text, get page text, screenshot, wait.

**Filesystem (3):** read file, write file, list directory.

**Code Analysis (10):** parse AST, get function info, find references, rename symbol, index project, search index, project structure, run tests, lint, format.

**Memory (5):** remember, recall, forget, list memories, semantic search.

**Task Management (12):** submit/status/list/cancel/pause/resume/retry background tasks, schedule add/list/remove cron jobs, workflow start/stop/list.

**System (6):** system info, current datetime, web fetch, ask user, get metrics, get timeline, reset metrics.

**Security (4):** sandbox check, permission list/deny/allow.

### 3.3 Memory Systems

| System | Backend | Key Features |
|---|---|---|
| **Working Memory** | In-memory dict | Ephemeral key-value store per session |
| **Long-Term Memory** | JSON file (`memory_store/long_term.json`) | Persistent, scored by importance + recency + frequency, LRU eviction |
| **Conversation Memory** | In-memory list | Bounded history with automatic trimming |
| **Semantic Memory** | sentence-transformers | Embedding-based search with keyword fallback |

### 3.4 Security

- **Sandbox** — Restricts file I/O to allowed directories
- **Rate Limiter** — Token-bucket algorithm per time window
- **Permission Manager** — Tool allow/deny lists, destructive command blacklist (`rm -rf`, `dd if=`, etc.), interactive confirmation prompts

### 3.5 Voice I/O

- **STT** — Google Speech Recognition via `speech_recognition` + `sounddevice`
- **TTS** — SAPI5 via `pyttsx3`, interruptible
- **VAD** — Frame-based energy threshold detection
- Modes: CLI REPL or voice-only interaction loop

### 3.6 Workflows & Scheduling

- **Workflow Recorder** — Records tool call sequences to JSON files (`workflows/*.json`)
- **Cron Scheduler** — 5-field cron expression parsing, tick every 30s, daemon thread execution
- **Async Task Manager** — Submit, cancel, pause, resume, retry, progress tracking

---

## 4. Project Structure

```
F:\Projects\Friday\
├── main.py                     Entry point (211 lines)
├── agent/
│   ├── core.py                 Agent orchestrator (52 lines)
│   ├── llm.py                  LLM provider wrapper (19 lines)
│   └── tools.py                Tool discovery loader (9 lines)
├── core/
│   ├── executor.py             ReAct loop (132 lines)
│   ├── planner.py              Task decomposition (143 lines)
│   ├── verifier.py             Task verification (45 lines)
│   ├── logger.py               Logging & metrics (159 lines)
│   ├── registry.py             Plugin registry (179 lines)
│   ├── prompt.py               System prompt builder (22 lines)
│   ├── workflow.py             Workflow recording (116 lines)
│   ├── task_manager.py         Async tasks (207 lines)
│   ├── session.py              Session export (67 lines)
│   ├── security.py             Security layers (121 lines)
│   ├── scheduler.py            Cron scheduler (140 lines)
│   └── memory/                 Memory systems (369 lines total)
├── providers/
│   ├── ollama.py               Ollama provider (68 lines)
│   ├── openai_compat.py        OpenAI/OpenRouter provider (106 lines)
│   ├── base.py                 Abstract base (20 lines)
│   └── registry.py             Provider registry (18 lines)
├── config/
│   ├── settings.py             Default constants & prompts (42 lines)
│   ├── providers.py            TOML config loader (25 lines)
│   └── providers.toml          Provider configuration (30 lines)
├── browser/                    Playwright automation (327 lines total)
├── tools/                      Legacy tool functions (276 lines total)
├── plugins/builtins/           Plugin tool implementations (1,185 lines total)
├── voice/                      Voice I/O (210 lines total)
├── coding/                     Code analysis (331 lines total)
├── tests/                      59 unit tests (330 lines total)
└── workflows/                  Saved workflow files
```

---

## 5. Current Status

### 5.1 What Works

- **Full REPL** with text and voice modes, `/commands` (exit, clear, voice, lang, help)
- **Multi-provider LLM** support with streaming, tool calls, automatic failover
- **ReAct execution loop** — LLM decides which tools to call, results fed back, iterates until answer
- **Task planning** — LLM decomposes complex goals into sub-tasks
- **Task verification** — LLM checks task success, triggers retry with error feedback
- **All 56 tools** registered and functional (browser, files, code, memory, tasks, security, system)
- **Browser automation** via Playwright (persistent Chrome profile, anti-detection)
- **Memory systems** (working, long-term, conversation, semantic)
- **Security** (sandbox, rate limiting, permissions)
- **Logging** (structured logs, events, metrics with timeline)
- **Coding tools** (AST parsing, project indexing, test/lint/format)
- **Voice I/O** (speech-to-text, text-to-speech, voice activity detection)
- **Async task manager** with cron scheduling
- **Workflow recording** and replay
- **Session export** to JSON/Markdown
- **59 unit tests** all passing

### 5.2 Known Issues

- OpenRouter free tier may hit rate limits (requires API key or switch provider)
- Some free OpenRouter providers (Cohere, Google AI Studio) have strict message format validation — currently handled by normalizing `type: "function"` and `tool_call_id` in the executor
- Ollama with small models (1.5B) may write tool calls as text JSON instead of native `tool_calls` — mitigated by strict system prompt

### 5.3 Configuration Required

- Add `api_key` to `config/providers.toml` under `[openrouter]` or `[openai]` before using cloud providers

---

## 6. Recent Milestones

### Refactor Session (July 16, 2026)

1. **Dead code removed** — Deleted `core/prompt.py` (unused), 6 `tools/` files covered by plugins, and stripped unused `ToolPlugin` base fields (`version`, `timeout`, `requires`, `permissions`, `health_check`)
2. **Global state eliminated** — Removed import-time `discover_plugins()` side effect (now called explicitly from `main.py`). Removed `TOOL_DEFINITIONS_CACHE` from planner. Tools and definitions injected via constructor, not module globals
3. **Verifier removed** — Replaced unreliable LLM-based verification with deterministic retry (retry only on transient errors: timeout/not found/connection/rate limit)
4. **Error boundaries added** — `_react_loop` wrapped in try/except; `json.loads(raw_args)` wrapped for malformed LLM args
5. **Tool call normalization moved to providers** — Both Ollama and OpenAI providers produce consistent `{id, type: "function", function: {name, arguments}}` output
6. **4 subsystems removed** — Deleted scheduler (cron), task manager (background tasks), workflow recorder, semantic memory (removed sentence-transformers dependency). Removed 12 associated plugins
7. **Planner prompt fixed** — Regex `\[.*?\]` changed to greedy `\[.*\]` to handle nested `[]` in tool arguments. Prompt reworded with examples for multi-step decomposition
8. **End-to-end verified** — "open notepad create a file and save it to E drive" works: planner creates 2 tasks → write_file creates file → run_command opens Notepad

---

## 7. Test Coverage

| Module | Tests | Areas Covered |
|---|---|---|
| Configuration | 7 | Defaults, prompts (EN/HI), provider config |
| Logger | 10 | Log levels, metrics (tool/llm/retry/reset), timeline |
| Memory | 15 | Working, long-term, conversation, memory entry scoring |
| Planner | 7 | Task defaults, JSON parsing (valid/invalid/empty/fallback) |
| Registry | 4 | Plugin discovery, essential tools, duplicates |
| Security | 10 | Sandbox, rate limiter, permission manager, command blacklist |
| **Total** | **59** | |

---

## 8. Dependencies (from imports)

- `ollama` — Local LLM
- `openai` — OpenAI/OpenRouter API
- `playwright` — Browser automation
- `pyttsx3` — Windows TTS
- `speech_recognition` + `sounddevice` — Speech-to-text
- `sentence-transformers` — Semantic memory embeddings
- `tomllib` (stdlib 3.11+) — TOML config parsing
- `pytest` — Testing
- `ruff` — Linting/formatting
