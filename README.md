<div align="center">
  <a name="readme-top"></a>

  <img src="og-image.svg" alt="Friday AI — Open-Source JARVIS for Your Desktop" width="100%">

  <br>

  <h1 align="center"><code>Friday</code> — Your Desktop AI Command Center</h1>

  <p align="center">
    <b>Open-source JARVIS-class AI that runs entirely on your hardware.</b><br>
    Speak · Gesture · Type — it sees your screen, controls your computer, runs automations,<br>
    visualizes data in 3D, and talks back with personality. No cloud lock-in. No subscriptions.
  </p>

  <!-- Hero badges -->
  <p align="center">
    <a href="https://github.com/alimaandev/Friday/releases"><img src="https://img.shields.io/github/v/release/alimaandev/Friday?style=for-the-badge&logo=github&color=8b5cf6" alt="Release"></a>
    <a href="https://github.com/alimaandev/Friday/stargazers"><img src="https://img.shields.io/github/stars/alimaandev/Friday?style=for-the-badge&logo=github&color=f59e0b" alt="Stars"></a>
    <a href="https://github.com/alimaandev/Friday/issues"><img src="https://img.shields.io/github/issues/alimaandev/Friday?style=for-the-badge&logo=github&color=3b82f6" alt="Issues"></a>
    <a href="https://github.com/alimaandev/Friday/actions"><img src="https://img.shields.io/github/actions/workflow/status/alimaandev/Friday/ci.yml?style=for-the-badge&logo=githubactions&color=22c55e" alt="CI"></a>
    <a href="https://github.com/alimaandev/Friday/blob/main/LICENSE"><img src="https://img.shields.io/github/license/alimaandev/Friday?style=for-the-badge&color=10b981" alt="License"></a>
    <br>
    <a href="https://react.dev"><img src="https://img.shields.io/badge/React_19-61DAFB?style=for-the-badge&logo=react&logoColor=000" alt="React 19"></a>
    <a href="https://threejs.org"><img src="https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=threedotjs&logoColor=fff" alt="Three.js"></a>
    <a href="https://www.python.org"><img src="https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=fff" alt="Python 3.11+"></a>
    <a href="https://vite.dev"><img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=fff" alt="Vite"></a>
    <a href="https://tailwindcss.com"><img src="https://img.shields.io/badge/Tailwind_v4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=000" alt="Tailwind CSS v4"></a>
    <a href="https://www.typescriptlang.org"><img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=fff" alt="TypeScript"></a>
  </p>

  <p align="center">
    <a href="https://github.com/sponsors/alimaandev"><img src="https://img.shields.io/badge/Sponsor-30363D?style=for-the-badge&logo=githubsponsors&logoColor=fff" alt="Sponsor"></a>
    <a href="#"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=fff" alt="Discord"></a>
    <a href="https://twitter.com/intent/tweet?text=Check%20out%20Friday%20-%20The%20Open-Source%20JARVIS%20for%20Your%20Desktop&url=https://github.com/alimaandev/Friday"><img src="https://img.shields.io/badge/Tweet-000000?style=for-the-badge&logo=x&logoColor=fff" alt="X / Twitter"></a>
    <a href="https://www.youtube.com/@alimaandev"><img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=fff" alt="YouTube"></a>
  </p>

  <p align="center">
    <b>English</b>
    ·
    <b><a href="README.ur.md">اردو</a></b>
    ·
    <b><a href="README.hi.md">हिन्दी</a></b>
  </p>
</div>

<br>

<details>
  <summary><kbd>📖 Table of Contents</kbd></summary>

  - [🤔 Why Friday?](#-why-friday)
  - [🎬 Demo](#-demo)
  - [⚡ Quick Start](#-quick-start)
  - [🚀 Features](#-features)
  - [🔒 Privacy & Security](#-privacy--security)
  - [📁 Project Structure](#-project-structure)
  - [⚙️ Configuration](#configuration)
  - [🏗 Architecture](#-architecture)
  - [🛠 Development](#-development)
  - [❓ FAQ](#-faq)
  - [🛣 Roadmap](#-roadmap)
  - [🤝 Contributing](#-contributing)
  - [⭐ Star History](#-star-history)
  - [💖 Support](#-support)
  - [📄 License](#-license)

</details>

<br>

---

## 🎯 Your Desktop AI Command Center

**Friday** is an open-source JARVIS-class AI that lives on your desktop. Speak to it, gesture at it, or type — it sees your screen, controls your computer, runs automations, visualizes data in 3D, and talks back with personality. Everything runs locally. Your API key, your LLM, your rules.

> The 3D orb reacts to your voice. The Intelligence panel streams 10 live data sources. The Holodeck renders your metrics as animated 3D bars. Zen mode turns everything into a monochrome orb + chat. And it all starts with one command.

```bash
npm run friday        # → boots API server + frontend together (Windows)
# or
docker compose up -d  # → Frontend: http://localhost:5173 · Backend: http://localhost:8080
```

<br>

---

## ✨ What's New in v4 — "The Orb"

<table>
  <tr>
    <td width="50%" valign="top">
      <p align="center"><strong>🧘 Zen Mode</strong></p>
      <p align="center">
        A radical minimal UI — one monochrome orb + chat by default. ⌘B toggles to the full dashboard.
        Ambient floating widgets orbit the orb; hover/drag to expand.
      </p>
    </td>
    <td width="50%" valign="top">
      <p align="center"><strong>🖥️ Computer Control</strong></p>
      <p align="center">
        Open apps, focus windows, type, click, and summarize your desktop. "Organize my desktop" is one
        goal for the autopilot — every action asks for your confirmation first.
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <p align="center"><strong>🧩 Plugin Marketplace</strong></p>
      <p align="center">
        Install & remove community plugins from Settings. Ships with built-ins for screen, email,
        calendar, web, and system — plus a community plugin registry.
      </p>
    </td>
    <td width="50%" valign="top">
      <p align="center"><strong>🛠 Custom Tool Builder</strong></p>
      <p align="center">
        Describe a tool in natural language and Friday generates, registers, and persists it —
        no code required.
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <p align="center"><strong>📚 Local RAG Pipeline</strong></p>
      <p align="center">
        Ingest documents and search them with sentence-aligned chunking + lexical reranking on top of
        your three parallel memory engines.
      </p>
    </td>
    <td width="50%" valign="top">
      <p align="center"><strong>🧠 Knowledge Graph</strong></p>
      <p align="center">
        Entities & relations extracted from your chats. Every new session seeds context from the graph
        + diary — "Last time you were working on…"
      </p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <p align="center"><strong>🚫 Blackout Mode</strong></p>
      <p align="center">
        One toggle for total privacy: network tools blocked, local Ollama forced, PRIVATE seal on the orb.
      </p>
    </td>
    <td width="50%" valign="top">
      <p align="center"><strong>⚡ Single-Command Start</strong></p>
      <p align="center">
        <code>python main.py --ui</code> or <code>npm run friday</code> boots API + frontend together and
        opens your browser. Global <code>Ctrl+Alt+F</code> summons Friday from anywhere.
      </p>
    </td>
  </tr>
</table>

<br>

---

## 🤔 Why Friday?

**Cloud assistants are convenient — and that's the problem.** They live behind a website, own your conversation history, upload your screen on request to a vendor you didn't choose, and charge a subscription for features you could run yourself.

**Friday is the alternative that puts you back in control:**

- 🖥️ **Desktop-first** — it runs where you work. No tab required, no "sorry, I can only do that in the cloud" moments.
- 🔑 **Bring your own LLM** — plug in OpenRouter, OpenAI, Ollama, or any OpenAI-compatible endpoint. Your key, your provider, your billing, your rules. No Friday servers exist — there is nothing to charge you for.
- 🔒 **Local by design** — memory, automation definitions, and Google tokens live in a `memory_store/` folder on *your* machine, not in someone else's database. See [Privacy & Security](#-privacy--security).
- 🎭 **A personality, not a chatbot** — three voice personas, ambient conversation, and a 3D orb that reacts to you. It *feels* like a companion, because that's the whole point.
- 🧩 **Extensible** — plugins, custom tools, and a planner that breaks big goals into executed steps. If you can script it, Friday can run it.

> **The pitch in one sentence:** Friday is a JARVIS-class AI assistant you actually own — free, open source (MIT), and running entirely on your hardware.

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 🎬 Demo

<img src="desktop/public/dashboard.png" alt="Friday dashboard — 3D orb, intelligence panel, and chat" width="100%">

> 🎥 *A short GIF/video walkthrough of the orb, voice, and Holodeck is coming soon. In the meantime, the dashboard above shows the full interface — and the best demo is running it yourself (30 seconds, below).*

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## ⚡ Quick Start

### 🚀 Single command (recommended)

```bash
git clone https://github.com/alimaandev/Friday.git
cd Friday
cp config/providers.toml.example config/providers.toml
# Edit config/providers.toml — paste your OpenRouter (or other) API key
npm run friday        # boots API server + frontend, opens your browser
```

### 🐳 Docker

```bash
git clone https://github.com/alimaandev/Friday.git
cd Friday
cp config/providers.toml.example config/providers.toml
# Edit config/providers.toml — paste your API key
docker compose up -d
```

### 🔧 Manual setup

```bash
git clone https://github.com/alimaandev/Friday.git
cd Friday
pip install -r requirements.txt
cp config/providers.toml.example config/providers.toml
# Edit config/providers.toml — paste your API key
cd desktop && python api_server.py &
cd .. && npm install && npm run dev
```

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 🚀 Features

<div align="center">
  <table>
    <tr>
      <td width="50%" valign="top">
        <p align="center">
          <img src="desktop/public/feature-orb.png" alt="3D Reactive Orb" width="400">
          <br>
          <strong>🎨 3D Reactive Orb + Holodeck</strong>
        </p>
        <p align="center">
          Procedural Three.js orb with 10 state-driven animation profiles. Plus a full 3D data visualization canvas — animated metric bars, ambient particle fields, orbital rings. Camera follows hand gestures in real time.
        </p>
      </td>
      <td width="50%" valign="top">
        <p align="center">
          <img src="desktop/public/feature-panel.png" alt="Live Intelligence Panel" width="170">
          <br>
          <strong>🌍 Live Intelligence Panel</strong>
        </p>
        <p align="center">
          10 real-time data modules: News, Weather, Stocks, Crypto, GitHub, Earthquakes, Space, World Clocks, CVE, Screen. All pushed via a single SSE connection — replaced 18 polling loops.
        </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top">
        <p align="center">
          <img src="desktop/public/feature-chat.png" alt="Streaming Chat" width="400">
          <br>
          <strong>💬 Streaming Chat + Voice Personality</strong>
        </p>
        <p align="center">
          Token-by-token responses with plan visualization and tool-call tracking. Three voice personas (JARVIS, FRIDAY, Cortana) with unique TTS rate/pitch and custom system prompts. Switch anytime via settings or ⌘K.
        </p>
      </td>
      <td width="50%" valign="top">
        <p align="center">
          <img src="desktop/public/feature-ribbon.png" alt="Voice & Gesture" width="400">
          <br>
          <strong>🎤 Voice, Gesture & Ambient Mode</strong>
        </p>
        <p align="center">
          Voice input/output with "Hey Friday" wake word (offline, in-browser). Ambient conversation mode — natural back-and-forth with auto-send on pause. Webcam hand-gesture control — open palm to speak, fist to send. Multi-language (English, Hindi, Urdu).
        </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top">
        <p align="center">
          <br>
          <strong>⏰ Automations</strong>
        </p>
        <p align="center">
          Schedule recurring actions with cron expressions ("every weekday at 9am"). Natural language creation — say "create automation for daily briefing at 8am". Background engine checks every 30s and fires via SSE. Toggle, trigger manually, or delete from the Intelligence panel.
        </p>
      </td>
      <td width="50%" valign="top">
        <p align="center">
          <br>
          <strong>👁 Screen & Camera Vision</strong>
        </p>
        <p align="center">
          Analyze your screen or webcam feed via LLM vision. Ask "what's on my screen" for instant description. Background SSE push auto-describes screen changes. Optional OCR via pytesseract. Capture camera frames from the Intelligence panel buttons.
        </p>
      </td>
    </tr>
  </table>
</div>

### 🔌 Integrations

| Integration | Type | Details |
|-------------|------|---------|
| **Google Calendar** | OAuth 2.0 | View upcoming events inline |
| **Gmail** | OAuth 2.0 | Unread count + inbox preview |
| **Memory** | TF-IDF + Jaccard + Vector | Cross-session semantic search |
| **Knowledge Graph** | Entity/relation extraction | Session continuity + proactive connections |
| **Local RAG** | Chunking + reranking | Document ingest + semantic retrieval |
| **Computer Control** | pyautogui + pywin32 | Open apps, type, click, windows, desktop summary |
| **Plugin Marketplace** | Manifest registry | Install/remove community plugins |
| **Custom Tools** | Natural-language builder | Persisted, code-free tool definitions |
| **Proactive Alerts** | SSE | System anomalies, reminders, notifications |
| **LLM Providers** | Pluggable | OpenRouter, OpenAI, Ollama, Anthropic, custom |
| **Morning Pulse Briefing** | Template | Daily weather, news, crypto, calendar, email summary |
| **Automations Engine** | Cron + SSE | Conditional triggers with background scheduler |
| **Vision** | LLM + PIL | Screen capture, camera frames, optional OCR |

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 🔒 Privacy & Security

Friday is designed so that *your data stays yours*. Here is exactly what happens with it — no fine print.

### Where your data lives

| Data | Location | Notes |
|------|----------|-------|
| **API keys** | `config/providers.toml` | Only read by Friday to call the provider *you* configured. Never uploaded anywhere. |
| **Conversation memory** | `memory_store/long_term.json` | Plain JSON on your disk — easy to inspect, back up, or delete. |
| **Vector/embedding index** | `memory_store/vector_store.pkl`, `embeddings.pkl` | Local search indexes for semantic recall. |
| **Google OAuth tokens** | `memory_store/` | Stored locally after you authorize Calendar/Gmail. |
| **Custom tools** | `memory_store/custom_tools.json` | Tool definitions you build stay on your machine. |
| **Blackout state** | `memory_store/blackout.json` | Privacy toggle state is persisted locally. |

### What leaves your machine

- **Only calls to your configured LLM provider** (OpenRouter, OpenAI, Ollama, etc.) — and only the content you ask Friday to process. If you run Ollama locally, **nothing** related to AI leaves your machine at all.
- **Live data modules** (news, weather, stocks, crypto, CVE, etc.) fetch public APIs — standard HTTP requests, same as any dashboard.
- **Google Calendar/Gmail** are only contacted when *you* use those features, under your own OAuth consent.

### What never leaves your machine

- **Screen & camera analysis** — your screen is captured only when *you* ask for it, and only the frames you request are sent to your provider for vision analysis. The background screen-change monitor runs entirely locally (it only compares image hashes — it never uploads pixels).
- **Voice & wake word** — "Hey Friday" detection and speech-to-text run **offline in your browser**. No audio is uploaded.
- **Computer control** — click, type, and window actions run locally. Control tools always require your confirmation first.

### 🚫 Blackout Mode

Flip one toggle in Settings and Friday goes fully local: **all network tool calls are blocked**, the provider is forced to **Ollama**, and a **PRIVATE seal** appears on the orb. Zero outbound AI traffic. [Learn more →](docs/v4-plan.md)

### Your controls

- 🗑️ **Wipe it all**: delete the `memory_store/` directory and your `config/providers.toml`.
- 🔄 **Go fully local**: switch the provider to Ollama — AI processing stops leaving your machine entirely.
- 👀 **Audit it**: memory is plain JSON. Open it and see exactly what Friday remembers about you.
- 🚫 **No telemetry** — Friday has no analytics, no crash reporters, and no phone-home code.

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 📁 Project Structure

```text
Friday/
├── core/                  # Business logic
│   ├── executor.py        #   Tool-call execution & streaming
│   ├── computer.py        #   Desktop control (apps, windows, input)
│   ├── rag.py             #   Local document chunking + reranking
│   ├── knowledge.py       #   Entity/relation knowledge graph
│   ├── plugin_store.py    #   Plugin marketplace manifest registry
│   ├── custom_tools.py    #   Natural-language tool builder
│   ├── blackout.py        #   Local-only privacy mode
│   ├── hotkey.py          #   System-level global hotkey
│   ├── autopilot.py       #   Goal decomposition → executed steps
│   ├── memory/            #   Three parallel memory engines (TF-IDF, vector, embeddings)
│   ├── proactive.py       #   Background monitors → SSE alerts
│   ├── automations.py     #   Cron-triggered automations engine
│   ├── vision.py          #   Screen/camera capture + analysis
│   └── auth/              #   Google OAuth (Calendar, Gmail)
├── providers/             # LLM provider abstraction (pluggable)
│   ├── registry.py        #   Auto-registration
│   ├── openai_compat.py   #   OpenRouter/OpenAI/any OpenAI-compatible API
│   └── ollama.py          #   Local models
├── plugins/               # Tool plugins (auto-discovered at startup)
│   ├── builtins/          #   Screen, email, calendar, web, system, computer…
│   ├── community/         #   Community plugin registry (marketplace)
│   └── manifest.json      #   Plugin manifests
├── agent/                 # Agent core (goals, planning, desktop context)
├── voice/                 # Voice I/O & wake word (offline, in-browser)
├── browser/               # Headless browser automation
├── desktop/               # Frontend (React 19 + Three.js + Vite + Tailwind)
│   ├── src/               #   Components, stores, hooks
│   ├── public/            #   Assets & feature images
│   └── api_server.py      #   Quart backend (REST + SSE, port 8080)
├── config/                # providers.toml — your API keys & providers
├── memory_store/          # Local memory (JSON + pickle) — created at runtime
├── docs/                  # API reference & v4 plan
└── tests/                 # 270+ pytest tests · desktop/src/test/ (107 vitest)
```

### ⚙️ Configuration

All configuration lives in a single file: `config/providers.toml` (copy from `config/providers.toml.example`).

| Setting | Default | Description |
|---------|---------|-------------|
| `[default] provider` | `"openrouter"` | Active provider — `openrouter`, `openai`, `ollama`, or any OpenAI-compatible API |
| `[openrouter] api_key` | — | Your OpenRouter key |
| `[openrouter] model` | `"openrouter/free"` | Model to use (free tier by default) |
| `[openrouter] fallback_model` | `"meta-llama/llama-3.2-3b-instruct:free"` | Used when the primary model is unavailable |
| `[openai] base_url` | `"https://api.openai.com/v1"` | Any OpenAI-compatible endpoint |
| `[ollama] base_url` | `"http://localhost:11434"` | Local Ollama server |
| `temperature` | `0.7` | Response randomness (per provider) |
| `max_tokens` | `4096` | Max response length (per provider) |
| `[embeddings] engine` | `"sentence"` | Memory embedding engine |

**Switch providers in three steps:**
1. Paste the API key in the provider's section
2. Change `[default] provider` to that provider's name
3. Restart the backend — done

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 🏗 Architecture

<p align="center">
  <img src="architecture.svg" alt="Friday System Architecture" width="90%">
</p>

A single-page React frontend communicates with a Python Quart backend via SSE and REST. The backend pools connections to any OpenAI-compatible LLM provider. Three parallel memory engines (TF-IDF, Jaccard, Vector) enable cross-session semantic recall, now augmented with a local RAG pipeline and a knowledge graph.

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 🛠 Development

Everything is tested and linted — CI runs both suites on every pull request.

### Backend (Python)

```bash
pip install -r requirements.txt
python -m pytest tests/ -v          # 270+ tests
python -m pytest tests/ --cov       # with coverage report (CI enforces a 50% gate)
ruff check .                        # lint
ruff format --check .               # format check
```

### Frontend (TypeScript)

```bash
cd desktop
npm install
npm run test                        # 107 vitest tests
npm run lint                        # oxlint
npx tsc --noEmit                    # type check
npm run build
```

### Architecture notes for contributors

- **API server** — `desktop/api_server.py` (Quart, port 8080); module-level code runs at import time, so tests patch `core.registry.discover_plugins` and `desktop.api_server._proactive` before import
- **Adding a tool** — create a plugin class in `plugins/builtins/` extending `ToolPlugin`; it's auto-discovered at startup
- **Adding a plugin to the marketplace** — add a manifest to `plugins/manifest.json` and a package under `plugins/community/`
- **Adding an endpoint** — define the route in `desktop/api_server.py`, use `@require_auth` for authenticated endpoints
- **Memory** — three engines run in parallel: keyword (TF-IDF), vector (cosine), embeddings (sentence-transformers)
- **Conventions** — PEP 8, line length 120, `async/await` for I/O, `asyncio.to_thread` for blocking calls; conventional commits (`feat:`, `fix:`, `test:`…)

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## ❓ FAQ

**Does Friday work offline?**
Partially. The frontend, voice, wake word, memory, automations, and computer control run locally. LLM responses need an LLM provider — use [Ollama](https://ollama.com) and everything runs 100% offline.

**Which LLMs can I use?**
Any OpenAI-compatible API: OpenRouter (default), OpenAI, Anthropic, Ollama, or a custom `base_url`. Bring your own key.

**Is my screen data sent to an AI company?**
Only when *you* ask Friday to analyze the screen, and only to the provider *you* configured. The background screen-change monitor compares hashes locally and never uploads pixels. Computer control actions always ask for your confirmation first.

**What is Blackout mode?**
One toggle that blocks all network tools, forces the Ollama provider, and shows a PRIVATE seal on the orb — total local-only privacy. Perfect for sensitive work.

**How do I make Friday fully local?**
Set `[default] provider = "ollama"` in `config/providers.toml`, or just enable **Blackout mode** from Settings.

**Can I customize Friday's personality?**
Yes — three voice personas (JARVIS, FRIDAY, Cortana) ship built-in, each with its own TTS voice and system prompt. Switch anytime via settings or ⌘K.

**Can I build my own tools?**
Yes — the Custom Tool Builder turns plain-English descriptions into working, persisted tools. And the Plugin Marketplace lets you install community plugins in one click.

**What are automations?**
Cron-scheduled actions you create in natural language ("create automation for daily briefing at 8am"). The background engine checks every 30s and fires results via SSE.

**Is Friday free?**
Yes — MIT licensed and free forever. You only pay your LLM provider if you use a paid one (Ollama is free).

**How do I uninstall / wipe my data?**
Delete `memory_store/` and `config/providers.toml`, then stop the containers (`docker compose down`).

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 🛣 Roadmap

| Release | Status | Highlights |
|---------|--------|------------|
| **v1** | ✅ Shipped | Core chat, 3D orb, intelligence dashboard |
| **v2** | ✅ Shipped | Async backend, SSE push, voice/gesture, Google integration, performance overhaul |
| **v3** | ✅ Shipped | Voice personality, cron automations, screen/camera vision, Holodeck 3D viz, ambient conversation |
| **v4** | ✅ Shipped | Zen mode, computer control, plugin marketplace, custom tools, local RAG, knowledge graph, blackout mode |
| **v5** | 📋 Backlog | Desktop app (Tauri), offline-first, multi-user mode |

Track progress on the [project board](https://github.com/users/alimaandev/projects/2) and [open issues](https://github.com/alimaandev/Friday/issues).

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 🤝 Contributing

We welcome contributions of all sizes — from typo fixes to new features.

1. Fork the repo
2. Create your feature branch (`git checkout -b feat/amazing`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push (`git push origin feat/amazing`)
5. Open a Pull Request

Check out [open issues](https://github.com/alimaandev/Friday/issues) — especially ones labelled [`good first issue`](https://github.com/alimaandev/Friday/labels/good%20first%20issue).

### Recent contributions

| Contributor | Contribution |
|-------------|-------------|
| [@surajthedev](https://github.com/surajthedev) | Async persistence for long-term memory |
| [@NikhilVedak](https://github.com/NikhilVedak) | API route versioning with `/api/v1` prefix |
| [@MasRama](https://github.com/MasRama) | Cleaned up unused CSS and animation classes |

<a href="https://github.com/alimaandev/Friday/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=alimaandev/Friday" alt="Contributors" width="600">
</a>

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## ⭐ Star History

<a href="https://star-history.com/#alimaandev/Friday&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://www.star-history.com/svg?repos=alimaandev/Friday&type=Date&theme=dark">
    <img width="600" src="https://www.star-history.com/svg?repos=alimaandev/Friday&type=Date" alt="Star History Chart">
  </picture>
</a>

<br>

### Share Friday

<p align="center">
  <a href="https://twitter.com/intent/tweet?text=Check%20out%20Friday%20-%20The%20Open-Source%20JARVIS%20for%20Your%20Desktop%20%F0%9F%9A%80&url=https://github.com/alimaandev/Friday&hashtags=ai,opensource,react,python">
    <img src="https://img.shields.io/badge/Share_on_X-000000?style=for-the-badge&logo=x&logoColor=white" alt="Share on X">
  </a>
  <a href="https://www.reddit.com/submit?title=Friday%20%E2%80%94%20The%20Open-Source%20JARVIS%20for%20Your%20Desktop&url=https://github.com/alimaandev/Friday">
    <img src="https://img.shields.io/badge/Share_on_Reddit-FF4500?style=for-the-badge&logo=reddit&logoColor=white" alt="Share on Reddit">
  </a>
  <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://github.com/alimaandev/Friday">
    <img src="https://img.shields.io/badge/Share_on_LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="Share on LinkedIn">
  </a>
  <a href="https://t.me/share/url?text=Check%20out%20Friday%20-%20The%20Open-Source%20JARVIS%20for%20Your%20Desktop&url=https://github.com/alimaandev/Friday">
    <img src="https://img.shields.io/badge/Share_on_Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Share on Telegram">
  </a>
</p>

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 💖 Support

If Friday is useful to you, consider supporting the project:

- ⭐ **Star** the repo — it helps others discover it
- 🐛 **Report bugs** or request features via [issues](https://github.com/alimaandev/Friday/issues)
- 🤝 **Contribute** code via [pull requests](https://github.com/alimaandev/Friday/pulls)
- 💰 **Sponsor** via [GitHub Sponsors](https://github.com/sponsors/alimaandev)

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 📄 License

MIT — use it, modify it, ship it. See [LICENSE](LICENSE) for details.

<br>

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/alimaandev">alimaandev</a> ·
  <a href="https://github.com/alimaandev/Friday/discussions">Discussions</a> ·
  <a href="https://github.com/alimaandev/Friday/issues">Issues</a></sub>
</p>

<p align="center">
  <a href="#readme-top">▲ Back to Top ▲</a>
</p>
