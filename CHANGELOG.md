# Changelog

## v4 — "The Orb" (2026-08-11)

### 🚀 Features

- **Zen Mode** — radical minimal UI: one monochrome orb + chat by default; ⌘B toggles the full dashboard
- **Orb Ambient Widgets** — floating monochrome cards (time, memory, active tool, CPU) orbiting the orb, hover/drag to expand
- **Computer Control** — open apps, focus/list/close windows, type, press keys, click, cursor, screen size, desktop summary
- **Autopilot Desktop Organization** — "organize my desktop and summarize" is one goal; status streams to the orb + Control tab
- **Plugin Marketplace** — manifest registry, one-click install/remove from Settings, community plugin registry
- **Custom Tool Builder** — natural-language → persisted tool definition, zero code required
- **Local RAG Pipeline** — sentence-aligned chunking + lexical reranking over the three memory engines
- **Knowledge Graph** — entity/relation extraction, proactive connections, session continuity ("Last time you were working on…")
- **Blackout Mode** — one toggle: network tools blocked, Ollama forced, PRIVATE seal on the orb
- **Onboarding** — first-launch "Hello, I'm Friday" orb greeting with flagship suggestions
- **Single-command start** — `python main.py --ui` (or `npm run friday`) boots API + frontend and opens the browser
- **Global hotkey** — `Ctrl+Alt+F` summons/focuses Friday from anywhere
- **Shareable Moments** — capture canvas + message snapshots as share cards (download/Web Share)

### 🔧 Improvements

- 278 Python tests + 107 TypeScript tests; ruff + oxlint + tsc clean
- Lazy browser import + graceful computer-control degradation on headless systems

## v3 (2026-07-28)

### 🚀 Features

- **Voice Personality** — 3 personas (JARVIS, FRIDAY, Cortana) with unique system prompts, TTS rate/pitch
- **Automations** — cron-based engine with natural-language creation ("every weekday at 9am")
- **Screen & Camera Vision** — LLM-powered screen analysis + webcam capture, auto-SSE on screen change
- **Holodeck** — Three.js 3D data visualization with gesture-driven camera
- **Ambient Voice** — natural conversation mode with auto-send on pause, 5s silence timeout
- **Morning Pulse Briefing** — weather, news, crypto, calendar, email — template-based, zero LLM cost
- **SSE reconnection** — exponential backoff with status indicator

### 🔧 Improvements

- Wake word auto-renew every 40s, voice input auto-recovery on `no-speech`/`aborted`
- TTS queue + URI persistence + enabled persistence to localStorage
- All voice settings persisted (output enabled, language, wake word, TTS voice)

## v2 (2026-07-22)

### 🚀 Features

- **Async Quart backend** — full async rewrite, single SSE connection replaces 18 polling loops
- **Voice input/output** — browser-based STT/TTS with "Hey Friday" wake word
- **Webcam hand gestures** — open palm to speak, fist to send
- **Google Calendar & Gmail** — OAuth 2.0 integration
- **10 intelligence modules** — News, Weather, Stocks, Crypto, GitHub, Earthquakes, Space, Clocks, CVE, Screen
- **Proactive alerts** — system anomalies, screen change detection
- **Multi-language chat** — English, Hindi, Urdu
- **Command palette** — ⌘K quick actions

### 🔧 Improvements

- Performance overhaul — SSE replaces polling, caching layer, lazy-loaded panels
- API route versioning (`/api/v1`)
- 59 Python tests, TypeScript strict-mode passes

## v1 (2026-06-xx)

### 🚀 Features

- Core chat interface with streaming responses
- 3D reactive orb (Three.js) with 10 state-driven animations
- Intelligence dashboard with live data modules
- Multi-session chat with independent memory
- Plugin architecture with tool registry
- Docker Compose setup