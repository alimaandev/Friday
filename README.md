<div align="center">
  <img src="og-image.png" alt="Friday AI — Open-Source JARVIS for Your Desktop" width="100%">
  
  <h1 align="center">Friday — The Open-Source JARVIS for Your Desktop</h1>

  <p align="center">
    <strong>Your open‑source desktop intelligence hub.</strong><br>
   Your personal AI command center for live intelligence and automation.
  </p>

  <p align="center">
    <a href="https://github.com/alimaandev/Friday/stargazers"><img src="https://img.shields.io/github/stars/alimaandev/Friday?style=for-the-badge&logo=github&color=gold" alt="Stars"></a>
    <a href="https://github.com/alimaandev/Friday/issues"><img src="https://img.shields.io/github/issues/alimaandev/Friday?style=for-the-badge&logo=github" alt="Issues"></a>
    <a href="https://github.com/alimaandev/Friday/actions"><img src="https://img.shields.io/github/actions/workflow/status/alimaandev/Friday/ci.yml?style=for-the-badge&logo=githubactions" alt="CI"></a>
    <a href="https://github.com/alimaandev/Friday/blob/main/LICENSE"><img src="https://img.shields.io/github/license/alimaandev/Friday?style=for-the-badge&color=green" alt="License"></a>
    <br>
    <a href="https://react.dev"><img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" alt="React 19"></a>
    <a href="https://threejs.org"><img src="https://img.shields.io/badge/Three.js-0.185-000000?style=for-the-badge&logo=threedotjs" alt="Three.js"></a>
    <a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python" alt="Python 3.11+"></a>
    <a href="https://vite.dev"><img src="https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite" alt="Vite 8"></a>
    <a href="https://tailwindcss.com"><img src="https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=for-the-badge&logo=tailwindcss" alt="Tailwind CSS v4"></a>
    <a href="https://www.typescriptlang.org"><img src="https://img.shields.io/badge/TypeScript-6-3178C6?style=for-the-badge&logo=typescript" alt="TypeScript 6"></a>
    <a href="https://github.com/sponsors/alimaandev"><img src="https://img.shields.io/badge/Sponsor-30363D?style=for-the-badge&logo=githubsponsors" alt="Sponsor"></a>
  </p>
</div>

<br>

<p align="center">
  <img src="desktop/public/dashboard.png" alt="Friday AI Dashboard — live intelligence panel with 3D orb, weather, news, stocks, crypto, space, and chat interface" width="900">
</p>

<br>

---

## ✨ What is Friday?

**Friday** is a fully open‑source AI command center that runs on your **desktop**. It combines a real‑time **3D reactive orb** (Three.js), a **live intelligence panel** (news, weather, stocks, crypto, earthquakes, space, CVE, GitHub trending, world clocks), **voice input/output**, **wake‑word activation**, **webcam hand‑gesture control**, **Google Calendar & Gmail integration**, and a **streaming chat** backed by any OpenAI‑compatible LLM — all in one polished dark‑mode interface.

No cloud lock‑in. No subscriptions. Your data, your machine, your AI.

<br>

---

## 🚀 Features

### 🧠 AI Core
- **Streaming chat** — real‑time token‑by‑token responses with plan visualization and tool‑call tracking
- **Multi‑session** — create, switch, and delete conversations; each session keeps its own memory
- **Command palette** — `⌘K` (or `Ctrl+K`) for instant actions: new session, toggle voice, camera, wake word
- **Context‑aware suggestions** — one‑click prompt chips: *Explain*, *Search*, *Code*, *Summarize*

### 🎨 3D Reactive Orb (Three.js)
- **State‑driven animations** — the orb shifts form for *idle*, *listening*, *thinking*, *reasoning*, *executing*, *searching*, *coding*, *speaking*, *error*, and *offline* states
- **Hand‑tracking follow** — orb gently follows your hand when camera is active
- **Auto‑pause** — rAF loop pauses when the browser tab is hidden (zero CPU when you're not looking)
- **Procedural shaders** — noise‑based energy core, Fresnel glow, holographic hex shell, orbital rings, drifting particles, orbiting nodes

### 🌍 Live Intelligence Panel
| Module | Data Source | Refresh |
|--------|-------------|---------|
| 📰 World News | Hacker News + RSS feeds | 5 min |
| 🌤 Weather | Open‑Meteo (default: Islamabad) | 5 min |
| 📈 Markets | Yahoo Finance (AAPL, GOOG, MSFT, NVDA, BTC‑USD) | 60 s |
| 💻 GitHub Trending | GitHub trending scraper | 5 min |
| 🌋 Earthquakes | USGS Earthquake API | 2 min |
| ₿ Crypto | CoinGecko | 2 min |
| 🛰 Space | Open Notify (ISS location + astronauts) | 60 s |
| 🕐 World Clocks | London, New York, Tokyo, Dubai, Sydney | 30 s |
| 🔐 Security | NVD CVE feed | 10 min |

### 🎤 Voice & Gesture
- **Voice input** — hold mic button, speak, release to send (browser SpeechRecognition)
- **Voice output** — TTS reads assistant responses aloud
- **Wake word** — "Hey Friday" activates listening (runs offline in-browser)
- **Hand gestures** — open palm starts listening, closed fist sends, hand position controls orb parallax
- **Multi‑language** — cycle between English, Hindi, Urdu

### 🔌 Integrations
- **Google Calendar** — OAuth 2.0, view upcoming events inline
- **Gmail** — OAuth 2.0, unread count + inbox preview
- **Screen capture** — periodic desktop screenshots viewed inside the panel
- **Memory** — TF‑IDF + Jaccard + vector semantic search across past conversations
- **Proactive alerts** — system anomalies, reminders, and notifications pushed via SSE

### ⚡ Performance (v2)
- All external API calls use **async HTTP** (httpx.AsyncClient with connection pooling)
- **SSE push** replaces 18 polling loops — single EventSource connection for all live data
- **Fine‑grained React state** (Zustand) — metrics updates re‑render only the StatusRibbon, not the whole tree
- **Batched memory persistence** — dirty‑flag batching avoids synchronous I/O on every store()
- **Bounded cache** — `cachetools.TTLCache` (max 500 entries) replaces unbounded dict
- **Concurrent search** — memory search runs all 3 engines in parallel via ThreadPoolExecutor
- **Lazy loading** — IntelligencePanel, SettingsPanel, CommandPalette loaded on demand

<br>

---

## 🖥 Demo

<p align="center">
  <img src="desktop/public/dashboard.png" width="800" alt="Friday AI in action — dashboard showing live orb, intelligence panel, and chat">
  <br>
  <em>Friday dashboard — real‑time intelligence panel + 3D orb + streaming chat</em>
</p>

<br>

---

## ⚡ Quick Start

### Prerequisites
- **Node.js** 20+ and **npm**
- **Python** 3.11+
- An **OpenRouter API key** (free at [openrouter.ai/keys](https://openrouter.ai/keys))

### 1. Clone

```bash
git clone https://github.com/alimaandev/Friday.git
cd Friday
```

### 2. Backend

```bash
pip install quart quart-cors hypercorn yfinance cachetools
cp config/providers.toml.example config/providers.toml
```

Edit `config/providers.toml` and paste your API key.

```bash
cd desktop
python api_server.py
```

Backend runs on **`http://localhost:8080`**.

### 3. Frontend

In a second terminal:

```bash
cd desktop
npm install
npm run dev
```

Opens at **`http://localhost:5173`**.

### 4. Done

Start chatting. The orb pulses, the intelligence panel fills, and Friday is online.

### Production build

```bash
npm run build        # outputs to desktop/dist/
```

<br>

---

## 🧰 Configuration

### LLM Providers

| Provider | Config | Key required |
|----------|--------|-------------|
| **OpenRouter** (default) | `[openrouter]` | `api_key` |
| **OpenAI** | `[openai]` | `api_key` |
| **Ollama** (local) | `[ollama]` | — (runs on `localhost:11434`) |
| **Custom** | `[openai_compat]` | `api_key` + `base_url` |

### Environment

| Variable | Default | Description |
|----------|---------|-------------|
| Backend bind | `127.0.0.1:8080` | Edit in `desktop/api_server.py` |
| Frontend API URL | `http://localhost:8080` | Edit in `desktop/src/core/api.ts` |

### Voice Languages

| Code | Language |
|------|----------|
| `en-US` | English (US) |
| `hi-IN` | Hindi |
| `ur-PK` | Urdu |

Cycle with the mic‑lang button in the input bar.

<br>

---

## 🖐 Gesture Controls

Enable camera from the command palette (`⌘K` → *Gesture control*) or the camera button in the StatusRibbon.

| Gesture | Action |
|---------|--------|
| ✋ Open palm | Start voice listening |
| ✊ Closed fist | Send voice transcript |
| 👆 Move left/right | Orb horizontal follow |
| 👆 Move up/down | Orb vertical follow |

The orb uses webcam‑based skin‑detection hand tracking — no external sensors needed.

<br>

---

## 🏗 Project Structure

```
Friday/
├── desktop/
│   ├── api_server.py              # Python backend (Quart + Hypercorn)
│   ├── src/
│   │   ├── App.tsx                # Root orchestrator — SSE, data, layout
│   │   ├── main.tsx               # Vite entry point
│   │   ├── index.css              # Tailwind v4 + custom animations
│   │   ├── core/
│   │   │   ├── StateManager.ts    # Zustand fine‑grained state
│   │   │   ├── api.ts             # HTTP client + SSE EventSource
│   │   │   ├── ThemeEngine.ts     # Dark‑mode CSS variable manager
│   │   │   └── EventBus.ts        # Lightweight pub/sub
│   │   ├── components/
│   │   │   ├── center/AiCore.tsx  # Three.js 3D orb + FRIDAY branding
│   │   │   ├── chat/              # InputBar, MessageBubble, QuickActions, …
│   │   │   ├── sidebar/           # IntelligencePanel, LeftSidebar, MemoryPanel, …
│   │   │   ├── topbar/TopBar.tsx  # Status ribbon
│   │   │   ├── command/           # ⌘K command palette
│   │   │   ├── settings/          # Settings panel
│   │   │   └── common/            # Skeleton, CameraIndicator
│   │   ├── hooks/
│   │   │   ├── useCamera.ts       # getUserMedia wrapper
│   │   │   ├── useHandGesture.ts  # Skin‑detection hand tracker
│   │   │   ├── useVoiceInput.ts   # SpeechRecognition
│   │   │   ├── useVoiceOutput.ts  # SpeechSynthesis
│   │   │   └── useWakeWord.ts     # Offline wake‑word detection
│   │   └── types/index.ts         # All TypeScript interfaces
│   └── package.json
├── core/
│   ├── memory/                    # Vector + TF‑IDF + keyword memory engines
│   ├── auth/google.py             # Google OAuth 2.0
│   ├── proactive.py               # Proactive alert engine
│   └── system1.py                 # Fast‑path reflex system
├── config/
│   ├── providers.toml.example     # LLM config template
│   └── providers.py               # Config loader
├── plugins/builtins/              # Calendar, Email, Screen, Memory plugins
└── tests/                         # 59 pytest tests
```

<br>

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

59 tests cover memory, security sandbox, rate limiter, planner, registry, logger, and long‑term memory decay.

<br>

---

## 🛣 Roadmap

- [x] **v1** — Core chat, 3D orb, intelligence dashboard
- [x] **v2** — Async backend, SSE push, voice/gesture, Google integration, performance overhaul
- [ ] **v3** — Plugin marketplace, custom tool creation, local RAG pipeline
- [ ] **v4** — Mobile companion app, multi‑user mode, proactive automation engine
- [ ] **v5** — Native desktop app (Tauri), offline‑first, local LLM integration

<br>

---

## 🎬 Demo

> 🎥 *Capture a short screen recording of Friday in action (orb, voice command, intelligence panel), convert to GIF via [ScreenToGif](https://www.screentogif.com/) or [OBS](https://obsproject.com/) + [FFmpeg](https://ffmpeg.org/), and drop it here. A 15‑second looping GIF at the top of the README is the #1 driver of interest.*

<br>

---

## 🤝 Contributing

Contributions are welcome! Open an [issue](https://github.com/alimaandev/Friday/issues) or submit a PR.

1. Fork the repo
2. Create your feature branch (`git checkout -b feat/amazing`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push (`git push origin feat/amazing`)
5. Open a Pull Request

See the [open issues](https://github.com/alimaandev/Friday/issues) for things to work on.

<br>

---

## 💖 Support

If Friday is useful to you, consider supporting the project:

- ⭐ Star the repo on [GitHub](https://github.com/alimaandev/Friday)
- [Sponsor](https://github.com/sponsors/alimaandev) via GitHub Sponsors

<br>

---

## 📄 License

MIT — use it, modify it, ship it. See [LICENSE](LICENSE) for details.

<br>

---

<p align="center">
  <sub>Made with ❤️ by <a href="https://github.com/alimaandev">alimaandev</a></sub>
</p>
