# Product Hunt first comment draft

Hey Product Hunt! 👋

I built Friday because I wanted a JARVIS-like desktop AI — something that runs entirely on my machine, no subscriptions, no cloud lock-in. Just me, my LLM, and a beautiful real-time dashboard.

**What makes Friday different:**

🔄 **3D reactive orb** — a procedural Three.js scene that shifts form based on what Friday is doing (idle, listening, thinking, speaking, searching, coding...). It's the heart of the interface.

🗣 **Voice + gesture control** — speak commands, use "Hey Friday" wake word, or control with webcam hand gestures. Open palm to talk, fist to send.

📊 **Live intelligence panel** — 10 data modules (news, weather, stocks, crypto, space, earthquakes, CVE, GitHub trending, world clocks) all pushed via SSE — no polling.

🔌 **Google Calendar & Gmail** — OAuth 2.0 integration, view your events and inbox inline.

🧠 **Any LLM you want** — OpenRouter, OpenAI, Ollama, or custom. Your API key, your choice.

⚡ **Performance-first** — SSE replaced 18 polling loops, lazy loading, batched memory, bounded caching. It's fast.

**Tech stack:** React 19 + Three.js + TypeScript + Tailwind v4 (frontend) · Python/Quart + async httpx (backend)

Everything is open-source (MIT). I'd love your feedback — what features would you want in a desktop AI hub?

🚀 https://github.com/alimaandev/Friday