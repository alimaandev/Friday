# v4 — "The Orb" — Final Plan

**Theme:** A JARVIS-class desktop AI with a radical minimal UI (one monochrome orb + chat) hiding a full control room — plus hands-free voice, shareable moments, computer control, and a personal knowledge graph. The "break the internet" feature set.

## Decisions (locked)
- **UI mode:** Zen Mode (orb + chat) is the DEFAULT; full dashboard reachable via `⌘B`.
- **Headline:** All candidate features, in sequence (zen UI → voice-native → moments → knowledge graph → computer control).
- **WIP:** Commit existing uncommitted work (Autopilot, Diary, agent/API changes) to branch `feat/v4` before building.

---

## Phase 0 — Branch hygiene
1. Create branch `feat/v4` off current state.
2. Commit existing WIP (Autopilot, Diary, agent/API/App changes + tests) as one `feat:` commit. Leave the `*.md` drafts untracked.
3. Verify: `ruff check .`, `python -m pytest tests/ -v`, `npx tsc --noEmit`, `npm run lint`.

## Phase 1 — Zen Mode UI (the headline visual)
Minimal stage by default: **monochrome orb centered + chat below + minimal input**. Everything else hidden.
- Zen state persisted (`friday_ui_zen`, default on); `⌘B` toggles to the full dashboard.
- `App.tsx`: wrap `StatusRibbon`, `LeftSidebar`, `IntelligencePanel` in `{!zen && ...}`; `AiCore` always full-size (drop shrink-to-thumb branch), title/command cards gone in zen.
- Monochrome pass: neutralize blue/gold (ONLINE dot, send button, suggestion pills) to white/gray; state conveyed by motion only.
- New components: `zen/ZenStage.tsx`, `zen/OrbCore.tsx` (extracted `JarvisOrb`), `zen/ZenInput.tsx`, `CommandPalette` "Toggle zen mode" action.
- **P1 — Orb ambient widgets:** tiny monochrome floating cards (time, weather, memory, active tool) orbiting the orb; hover/drag to expand. Preview of Holodeck-v2 gestures.
- Tests: `ZenMode.test.tsx`.

## Phase 2 — Voice-native OS
- Pack wake word → ambient listen → command → orb "executing" → TTS into a hands-free loop, persisted "listen now" toggle.
- Zen stage shows persistent mic + interim transcript; auto-send on idle already exists (`App.tsx:176-201`).

## Phase 3 — Shareable "Friday moments"
- Zen photo button: capture canvas + message snapshot → share card → download/Web Share, with repo link overlay (viral loop).

## Phase 4 — Personal knowledge graph
- `core/knowledge.py`: entity/relation extraction (async LLM) → `memory_store/entities.json`; proactive connections via SSE alerts.
- API: `GET/POST /api/knowledge`, `POST /api/entity-resolve`.
- **P4 — Session continuity:** every new chat seeds context from knowledge graph + diary ("Last time you were working on…").

## Phase 5 — Computer Control ("JARVIS is real")
- `tools/computer_control` + `core/computer.py`: open apps, type, click, read screen (reuse vision). Confirmation via existing `ApprovalDialog`.
- Bind to autopilot: "organize my desktop and summarize" = one goal. Frontend streams status to `BrainView`/zen orb + Control tab in `ScreenPanel`.

## Phase 6 — Roadmap pillars (discrete follow-up issues)
- **#52 Plugin marketplace** — manifest registry, install/remove UI in settings.
- **#54 Custom tool builder** — natural-language → tool def, persisted.
- **#53 Local RAG pipeline** — chunking/reranking on memory engines.
- **#55 Holodeck v2** — floating cards + gesture interactions (dashboard, not zen).

## Phase 7 — Launch polish
- **P3 — Onboarding "Hello, I'm Friday":** first-launch orb greeting + flagship suggestions.
- **P6 — Single-command start:** `python main.py --ui` (or `npm run friday`) boots API + frontend together; strengthens the Show HN moment.
- **P2 — System-level global hotkey** to summon/focus Friday from anywhere.
- **P5 — Blackout mode:** one-toggle local-only privacy (Ollama, no outbound), privacy seal on orb.

---

## Phase 6 — Roadmap pillars ✅ (scoped issues shipped)
- **#52 Plugin marketplace** — `core/plugin_store.py` manifest registry + Settings install/remove UI; community plugins in `plugins/community/`.
- **#54 Custom tool builder** — `core/custom_tools.py` natural-language → persisted tool def, Settings UI.
- **#53 Local RAG pipeline** — `core/rag.py` chunking + reranking over the memory engines (`ingest_document`, `rag_search`).
- **#55 Holodeck v2** — floating draggable cards + gesture-openness interactions in `HolodeckCards.tsx`.

## Phase 7 — Launch polish ✅
- **P3 — Onboarding "Hello, I'm Friday":** first-launch orb greeting + flagship suggestions (`zen/Onboarding.tsx`).
- **P6 — Single-command start:** `python main.py --ui` (or `npm run friday`) boots API + frontend together.
- **P2 — System-level global hotkey:** `Ctrl+Alt+F` summons/focuses the frontend (`core/hotkey.py`, needs `pip install keyboard`).
- **P5 — Blackout mode:** one-toggle local-only privacy (`core/blackout.py`), network tools blocked, Ollama provider forced, PRIVATE seal on orb.

---

**Execution order:** 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 — **all shipped.** Deferred to v5: Tauri desktop packaging, PWA/multi-user, light theme, persona auction.