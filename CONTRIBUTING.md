# Contributing to Friday

Thanks for your interest in contributing! Friday is an open-source AI command center, and every contribution — whether code, docs, design, or ideas — helps make it better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Guidelines](#coding-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project and everyone participating in it is governed by the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/Friday.git
   cd Friday
   ```
3. Add the upstream remote:
   ```bash
   git remote add upstream https://github.com/alimaandev/Friday.git
   ```
4. Follow the [Development Setup](#development-setup) below

## How to Contribute

### 🐛 Bug Reports
Open an [issue](https://github.com/alimaandev/Friday/issues/new) with:
- A clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, browser)

### ✨ Feature Requests
Open an [issue](https://github.com/alimaandev/Friday/issues/new) with:
- A clear description of the feature
- Why it's useful for Friday
- Any implementation ideas you have

### 📝 Documentation
Docs improvements are always welcome — typos, clarifications, new guides. Submit a PR.

### 💻 Code
See the issue tracker for open issues. Good first issues are tagged `good first issue`.

## Development Setup

### Prerequisites
- **Node.js** 20+ and npm
- **Python** 3.11+
- An OpenRouter API key (free at [openrouter.ai/keys](https://openrouter.ai/keys))

### Backend
```bash
pip install quart quart-cors hypercorn yfinance cachetools
cp config/providers.toml.example config/providers.toml
# Edit config/providers.toml with your API key
cd desktop
python api_server.py
```

### Frontend
```bash
cd desktop
npm install
npm run dev
```

Opens at `http://localhost:5173`. Backend must be running on `http://localhost:8080`.

### Running Tests
```bash
python -m pytest tests/ -v
```

### TypeScript Check
```bash
cd desktop
npx tsc --noEmit
```

### Production Build
```bash
cd desktop
npm run build
```

## Coding Guidelines

### General
- Write clean, readable code — optimize for the next person reading it
- Keep functions small and focused on a single responsibility
- Use meaningful variable and function names
- Add comments only when the code's intent isn't obvious from reading it

### Python
- Target Python 3.11+
- Follow [PEP 8](https://peps.python.org/pep-0008/) style
- Use type hints for all function signatures
- Prefer `async/await` for I/O-bound operations
- Use `asyncio.to_thread` for blocking operations

### TypeScript / React
- Target TypeScript 6 with strict mode
- Prefer `const` over `let`, avoid `var`
- Use Zustand for global state, local `useState` for component state
- Memoize components with `memo` and callbacks with `useCallback`
- Use CSS variables + utility classes over inline styles where practical
- Lazy-load panels that aren't immediately visible

### Commits
Use [conventional commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `refactor:` — code restructuring
- `perf:` — performance improvement
- `chore:` — tooling, deps, CI

### Branch Naming
- `feat/your-feature-name`
- `fix/your-bug-fix`
- `docs/your-docs-change`

## Pull Request Process

1. Create a branch from `main` following the naming convention above
2. Make your changes, keeping commits clean and atomic
3. Run the test suite and ensure all tests pass
4. Run the TypeScript check and Vite build
5. Push your branch and open a PR against `main`
6. In the PR description, link any related issues and describe your changes
7. Wait for review — address any feedback

### PR Checklist
- [ ] Code follows the coding guidelines
- [ ] Tests pass (`python -m pytest tests/ -v`)
- [ ] TypeScript check passes (`npx tsc --noEmit`)
- [ ] Vite build succeeds (`npm run build`)
- [ ] Docs updated if needed
- [ ] No new warnings or lint errors

## Issue Reporting

When opening an issue, please use one of the templates if available, or provide:
- A clear, descriptive title
- Steps to reproduce (for bugs)
- Expected behavior
- Actual behavior
- Screenshots (if relevant)
- Environment information

---

Thanks for contributing! Every PR, issue, and discussion makes Friday better.
