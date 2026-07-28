<div align="center">
  <a name="readme-top"></a>

  <img src="og-image.svg" alt="Friday AI — Open-Source JARVIS for Your Desktop" width="100%">

  <br><br>

  <!-- SHIELD GROUP -->
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

  - [⚡ Quick Start](#-quick-start)
  - [🚀 Features](#-features)
  - [🏗 Architecture](#-architecture)
  - [🛣 Roadmap](#-roadmap)
  - [🤝 Contributing](#-contributing)
  - [⭐ Star History](#-star-history)
  - [💖 Support](#-support)
  - [📄 License](#-license)

</details>

<br>

---

## 🔥 Speak. Gesture. Type.

**Friday** turns your desktop into an AI command center — inspired by the JARVIS interface from Iron Man. The 3D orb reacts to you, the panel streams live data from 10 sources, and the LLM speaks back. Everything runs locally. Your API key, your LLM, your rules.

No cloud lock-in. No subscriptions. One command to start:

```bash
docker compose up -d
# → Frontend: http://localhost:5173 · Backend: http://localhost:8080
```

<br>

---

## ⚡ Quick Start

### 🐳 Docker (recommended)

```bash
git clone https://github.com/alimaandev/Friday.git
cd Friday
cp config/providers.toml.example config/providers.toml
# Edit config/providers.toml — paste your OpenRouter (or other) API key
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
          <strong>🎨 3D Reactive Orb</strong>
        </p>
        <p align="center">
          Procedural Three.js orb at the heart of the interface. 10 state-driven animation profiles — idle, listening, thinking, speaking, and more. Hand-tracking follow, noise-based energy core, Fresnel glow, holographic hex shell, drifting particles.
        </p>
      </td>
      <td width="50%" valign="top">
        <p align="center">
          <img src="desktop/public/feature-panel.png" alt="Live Intelligence Panel" width="170">
          <br>
          <strong>🌍 Live Intelligence Panel</strong>
        </p>
        <p align="center">
          10 real-time data modules: News, Weather, Stocks, Crypto, GitHub Trending, Earthquakes, Space (ISS), World Clocks, CVE, Screen Capture. All pushed via a single SSE connection — replaced 18 polling loops.
        </p>
      </td>
    </tr>
    <tr>
      <td width="50%" valign="top">
        <p align="center">
          <img src="desktop/public/feature-chat.png" alt="Streaming Chat" width="400">
          <br>
          <strong>💬 Streaming Chat</strong>
        </p>
        <p align="center">
          Token-by-token responses with plan visualization and tool-call tracking. Multi-session with independent memory. Command palette (⌘K). Context-aware suggestion chips.
        </p>
      </td>
      <td width="50%" valign="top">
        <p align="center">
          <img src="desktop/public/feature-ribbon.png" alt="Voice & Gesture" width="400">
          <br>
          <strong>🎤 Voice & Gesture</strong>
        </p>
        <p align="center">
          Voice input/output with "Hey Friday" wake word (offline, in-browser). Webcam hand-gesture control — open palm to speak, fist to send. Multi-language support (English, Hindi, Urdu).
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
| **Proactive Alerts** | SSE | System anomalies, reminders, notifications |
| **LLM Providers** | Pluggable | OpenRouter, OpenAI, Ollama, custom |

<div align="right">
  <a href="#readme-top">▲ back to top</a>
</div>

<br>

---

## 🏗 Architecture

<p align="center">
  <img src="architecture.svg" alt="Friday System Architecture" width="90%">
</p>

A single-page React frontend communicates with a Python Quart backend via SSE and REST. The backend pools connections to any OpenAI-compatible LLM provider. Three parallel memory engines (TF-IDF, Jaccard, Vector) enable cross-session semantic recall.

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
| **v3** | 🔨 In progress | Plugin marketplace, custom tool builder, local RAG pipeline |
| **v4** | 📋 Planned | Mobile companion app, multi-user mode, proactive automation engine |
| **v5** | 📋 Planned | Native desktop app (Tauri), offline-first, local LLM integration |

Track progress on the [open issues](https://github.com/alimaandev/Friday/issues).

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