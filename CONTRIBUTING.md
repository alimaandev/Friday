# Contributing to Friday

Thanks for your interest in contributing! Friday is an open-source AI command center, and every contribution — whether code, docs, design, or ideas — helps make it better.

**Table of Contents**

- [Code of Conduct](#code-of-conduct)
- [Quick Start for Contributors](#quick-start-for-contributors)
- [Development Setup](#development-setup)
- [Project Architecture](#project-architecture)
- [Coding Guidelines](#coding-guidelines)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Issue Reporting](#issue-reporting)
- [Tips for First-Time Contributors](#tips-for-first-time-contributors)

---

## Code of Conduct

This project and everyone participating in it is governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the maintainers.

---

## Quick Start for Contributors

```bash
# 1. Fork the repo on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/Friday.git
cd Friday

# 3. Add upstream remote
git remote add upstream https://github.com/alimaandev/Friday.git

# 4. Create a branch
git checkout -b feat/your-feature-name

# 5. Set up the backend
pip install -r requirements.txt
cp config/providers.toml.example config/providers.toml
# Edit config/providers.toml with your OpenRouter API key
cd desktop && python api_server.py &

# 6. Set up the frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser. The backend runs on `http://localhost:8080`.

---

## Development Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| **Node.js** | 20+ | Frontend build & dev server |
| **npm** | 10+ | Package manager |
| **Python** | 3.11+ | Backend API server |
| **pip** | 23+ | Python package manager |
| **Git** | 2.40+ | Version control |
| **Docker** (optional) | 24+ | One-command setup via compose |

### Docker Setup (easiest)

```bash
cp config/providers.toml.example config/providers.toml
# Edit providers.toml with your API key
docker compose up -d
```

Frontend → `localhost:5173` · Backend → `localhost:8080`

### Manual Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure LLM provider
cp config/providers.toml.example config/providers.toml
```

Edit `config/providers.toml` with your preferred LLM provider:

```toml
[openrouter]
api_key = "sk-or-v1-..."   # Get one free at https://openrouter.ai/keys

# Or use local Ollama (no key required):
# [ollama]
# base_url = "http://localhost:11434"
```

Start the backend:

```bash
cd desktop
python api_server.py
```

The backend serves on `http://localhost:8080`.

> **Troubleshooting:** If you get import errors, ensure you're using Python 3.11+ and all deps are installed: `pip install -r requirements.txt --upgrade`. If port 8080 is in use, change the bind address in `desktop/api_server.py`.

### Manual Frontend Setup

```bash
cd desktop
npm install
npm run dev
```

Opens at `http://localhost:5173`. The frontend expects the backend at `http://localhost:8080` — change this in `desktop/src/core/api.ts` if needed.

> **Troubleshooting:** If `npm install` fails, try `npm cache clean --force && npm install`. If TypeScript errors appear in the editor but not in the build, run `npx tsc --noEmit` to verify.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| None required | — | Everything is configured via `config/providers.toml` |

---

## Project Architecture

```
Friday/
├── desktop/
│   ├── api_server.py           # Python backend (Quart) — routes, SSE, auth
│   ├── package.json
│   └── src/
│       ├── App.tsx             # Root component — SSE subscription, layout
│       ├── main.tsx            # Vite entry point
│       ├── index.css           # Tailwind v4 + animations
│       ├── core/               # Shared state, API client, event bus
│       ├── components/
│       │   ├── center/         # AiCore — Three.js 3D orb
│       │   ├── chat/           # InputBar, MessageBubble, QuickActions
│       │   ├── sidebar/        # IntelligencePanel, MemoryPanel
│       │   ├── topbar/         # Status ribbon
│       │   ├── command/        # ⌘K command palette
│       │   ├── settings/       # Settings panel
│       │   └── common/         # Skeleton loaders, CameraIndicator
│       └── hooks/              # useCamera, useHandGesture, useVoiceInput, etc.
├── core/
│   ├── memory/                 # Vector, TF-IDF, keyword memory engines
│   ├── auth/google.py          # Google OAuth 2.0
│   ├── proactive.py            # Alert engine
│   └── registry.py             # Plugin loader
├── config/
│   ├── providers.toml.example  # LLM config template
│   └── providers.py            # Config reader
├── plugins/builtins/           # Calendar, Email, Screen plugins
└── tests/                      # 59+ pytest tests
```

**Data Flow:** Browser → fetch/SSE → Python backend → httpx.AsyncClient → LLM API → streamed response → React renders tokens in real-time.

---

## Coding Guidelines

### General Principles

- Write code for the next person reading it — clarity over cleverness
- One function, one responsibility
- Name things by what they *mean*, not how they're *implemented*
- Comments explain *why*, not *what* (the code shows what)

### Python

| Rule | Standard |
|------|----------|
| Version | **3.11+** |
| Style | [PEP 8](https://peps.python.org/pep-0008/) |
| Type hints | **Required** for all function signatures |
| Async | Prefer `async/await` for I/O; use `asyncio.to_thread` for blocking calls |
| Imports | Standard library → third-party → local (grouped, alphabetized) |

### TypeScript / React

| Rule | Standard |
|------|----------|
| Version | **TypeScript 6** with strict mode |
| State | Zustand for global, `useState` for local |
| Performance | Use `memo` + `useCallback`; lazy-load panels not immediately visible |
| Styling | CSS variables + utility classes over inline styles |
| Imports | Named exports preferred; group: React → third-party → local |

### Commits

Use [conventional commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation |
| `refactor:` | Code restructuring (no behavior change) |
| `perf:` | Performance improvement |
| `chore:` | Tooling, dependencies, CI |
| `test:` | Adding or fixing tests |

Write commit messages in the imperative: `feat: add voice output toggle` not `feat: added voice output toggle`.

### Branch Naming

- `feat/your-feature-name`
- `fix/your-bug-fix`
- `docs/your-docs-change`

---

## Pull Request Process

1. **Sync your fork** before starting:
   ```bash
   git checkout main
   git fetch upstream
   git merge upstream/main
   git push origin main
   ```

2. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Make changes** in small, atomic commits.

4. **Verify your changes** pass all checks:

   ```bash
   # Backend tests
   python -m pytest tests/ -v

   # TypeScript check
   cd desktop && npx tsc --noEmit

   # Production build
   cd desktop && npm run build
   ```

5. **Push and open a PR**:
   ```bash
   git push origin feat/your-feature-name
   ```
   Then open a pull request on GitHub against `main`.

6. **PR description** should include:
   - What changed and why
   - Screenshots for UI changes
   - Link to any related issues (`Closes #123`)

7. **Address review feedback** — push additional commits to the same branch.

### PR Checklist

- [ ] Code follows the coding guidelines
- [ ] `python -m pytest tests/ -v` passes
- [ ] `npx tsc --noEmit` passes
- [ ] `npm run build` succeeds
- [ ] Docs updated if needed
- [ ] No new warnings or lint errors

---

## Testing

```bash
# Run all Python tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_memory.py -v

# TypeScript check
cd desktop && npx tsc --noEmit

# Full build
cd desktop && npm run build
```

The CI pipeline runs all of these automatically on every PR. Keep them green.

---

## Issue Reporting

When opening an issue:

- **Use a template** (bug report or feature request) if available
- **Be specific** — "The orb doesn't animate when speaking" is better than "UI is broken"
- **Include reproduction steps** for bugs
- **Add environment details** — OS, Python version, browser, LLM provider
- **Attach screenshots** for UI issues

Labels you might see on issues:

| Label | Meaning |
|-------|---------|
| `good first issue` | Great for new contributors — limited scope, clear task |
| `bug` | Something isn't working |
| `enhancement` | New feature or improvement |
| `chore` | Tooling, CI, documentation |
| `help wanted` | Maintainers would appreciate community help |

---

## Tips for First-Time Contributors

- **Look for [`good first issue`](https://github.com/alimaandev/Friday/labels/good%20first%20issue) labels** — these are tasks curated for newcomers
- **Comment on the issue** before starting work so others know you're taking it
- **Run the app locally first** — seeing it work helps you understand the codebase
- **Start small** — a typo fix, a test improvement, or a CSS tweak is a great first PR
- **Don't hesitate to ask questions** — open a discussion or comment on the issue

---

Thanks for contributing! Every PR, issue, and discussion makes Friday better.