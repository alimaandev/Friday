## Show HN: Friday – Open-Source JARVIS for Your Desktop (React + Python)

https://github.com/alimaandev/Friday

A desktop AI command center inspired by Iron Man's JARVIS — runs entirely on your machine, no cloud lock-in.

Features:
- 3D reactive Three.js orb with 10 state-driven animation profiles (idle, listening, thinking, reasoning, speaking, etc.)
- Voice input/output with "Hey Friday" wake word + hand gesture control via webcam
- Live intelligence panel: news, weather, stocks, crypto, space, earthquakes, CVE, GitHub trending, world clocks — all pushed via SSE
- Google Calendar & Gmail OAuth integration
- Streaming chat with any OpenAI-compatible LLM (OpenRouter, OpenAI, Ollama, or custom)
- Docker compose up — runs in under 2 minutes
- Backend: Python/Quart + async httpx.  Frontend: React 19 + Three.js + TypeScript + Tailwind v4.

We just shipped v2 with async performance (SSE replaces 18 polling loops, lazy loading, batched memory persistence) and are working on v3 (plugin marketplace, local RAG, custom tool builder).

Looking for feedback on the UX, architecture, and what features you'd want in a desktop AI hub.