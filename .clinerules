You are working on Friday, an open-source JARVIS-class desktop AI command center.

## Tech Stack
- **Backend:** Python 3.11+, Quart (async Flask), Hypercorn, pytest, Ruff
- **Frontend:** React 19, TypeScript 6, Vite 8, Three.js 0.185, Tailwind v4, Zustand, Vitest, oxlint

## Rules

### Before writing code
- Check AGENTS.md for detailed project conventions
- Read existing files to understand patterns before adding new ones
- Check pyproject.toml for pytest/ruff config before running tools

### Code style
- Python: PEP 8, line length 120, double quotes, async/await for I/O
- TypeScript: strict mode, named exports, grouped imports
- No ESLint or Prettier — use `ruff` for Python, `oxlint` for TS
- No SQLAlchemy — project uses JSON files for persistence

### Testing
- Always run tests after making changes: `python -m pytest tests/ -v --tb=short` and `cd desktop && npm run test`
- Python tests must be async (module-level `pytestmark = pytest.mark.asyncio`)
- API server tests must patch `discover_plugins` and `_proactive` before import

### Commits
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `chore:`, `test:`
- Imperative mood, no emoji prefixes

### API Server (critical)
- Module-level side effects at import time (discover_plugins, EventBroadcaster)
- Tests that import `desktop.api_server` MUST mock `core.registry.discover_plugins` first
- Use Quart test client: `async with app.test_client() as client:`
