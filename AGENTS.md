# AI Agent Guide for Friday

This file instructs AI coding agents (opencode, Claude Code, Cline, Cursor, etc.) how to work effectively with this project.

## Project Overview

Friday is an open-source JARVIS-class desktop AI command center with a Python/Quart backend and React/TypeScript frontend backed by Three.js. It supports streaming chat, tool calling, voice, vision, proactive alerts, automations, and a rich 3D interface.

## Quick Start for Agents

### Backend (Python)

```bash
# Install deps
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v
python -m pytest tests/ -v --cov

# CI enforces a coverage gate: the main suite must stay above 50%
# (tests/test_api_server.py is run separately against desktop/ and gated at 40%).
python -m pytest tests/ --cov --cov-fail-under=50 --ignore=tests/test_api_server.py
python -m pytest tests/test_api_server.py --cov=desktop --cov-fail-under=40

# Lint
ruff check .
ruff format --check .

# Run backend
python main.py                   # terminal REPL
python desktop/api_server.py     # Quart web server (port 8080)
```

### Frontend (TypeScript/React)

```bash
cd desktop

# Install deps
npm install

# Test
npm run test
npm run test:watch

# Lint
npm run lint             # oxlint

# Type check
npx tsc --noEmit

# Dev server
npm run dev              # port 5173

# Build
npm run build
```

## Key Conventions

### Commits
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `chore:`, `test:`
- Imperative mood: "add feature" not "added feature"
- Branch naming: `feat/your-feature-name`, `fix/`, `docs/`

### Code Style
- **Python:** PEP 8, line length 120, double quotes, Ruff formatter
- **TypeScript:** Strict mode, named exports, grouped imports (React -> third-party -> local)
- Use `async/await` for I/O, `asyncio.to_thread` for blocking calls
- Type hints required on all Python function signatures

### Project Structure
- `core/` — Business logic (executor, memory, proactive, automations, etc.)
- `desktop/api_server.py` — Quart REST API (~1200 lines)
- `desktop/src/` — React frontend
- `tests/` — Python tests (pytest)
- `desktop/src/test/` — TypeScript tests (Vitest)
- `plugins/` — Tool plugins (discovered automatically)
- `providers/` — LLM provider abstraction (OpenAI, Ollama, etc.)

## Important Architecture Notes

### API Server (`desktop/api_server.py`)
- Uses Quart (async Flask-compatible framework)
- Module-level code runs at import time: `discover_plugins()`, `_broadcaster = EventBroadcaster()`
- Tests must patch `core.registry.discover_plugins` and `desktop.api_server._proactive` BEFORE import
- All SQLAlchemy/ORM is irrelevant; the project uses JSON files for persistence

### Testing
- **Backend:** pytest with `pytest-asyncio` (strict mode), `--tb=short` default
- **Frontend:** Vitest with jsdom environment, Testing Library
- All test methods must be `@pytest.mark.asyncio` or use module-level `pytestmark = pytest.mark.asyncio`
- Test files go in `tests/` (Python) or `desktop/src/test/` (TypeScript)

### Linting
- Python: Ruff 0.9+ (no ESLint or Prettier)
- TypeScript: oxlint 1.71+ (no ESLint or Prettier)

### Memory System
- Three parallel engines: keyword (TF-IDF), vector (cosine similarity), embeddings (sentence-transformers)
- `core/memory/` contains all memory components

### LLM Providers
- Registered via `providers/registry.py`
- Default: OpenRouter. Also supports OpenAI, Ollama, and any OpenAI-compatible API
- Config via `config/providers.toml`

## Common Tasks

### Adding an API endpoint
1. Define route in `desktop/api_server.py`
2. Add `@require_auth` decorator for authenticated endpoints
3. Add validation helpers if needed
4. Write test in `tests/test_api_server.py`

### Adding a tool
1. Create a plugin class in `plugins/builtins/` extending `ToolPlugin`
2. Or add a standalone function in `tools/`
3. It's auto-discovered by `core.registry.discover_plugins()`
4. Write tests in a new or existing test file

### Adding a frontend component
1. Create component in `desktop/src/components/<category>/`
2. Add types in `desktop/src/types/index.ts`
3. Write tests in `desktop/src/test/`
4. Use Zustand store from `desktop/src/core/` for global state
