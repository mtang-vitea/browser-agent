# Browser Agent

AI-powered browser automation using Claude's vision and Playwright.

> **Dual-agent repo**: This project uses both `CLAUDE.md` (Claude Code) and `AGENTS.md` (Codex). They share documentation via `docs/`. **When updating either file, update the other to match.** When updating shared docs in `docs/`, no sync is needed — both files reference them.

## Package Manager

This project uses **uv** — not pip, not poetry, not conda.

- Install deps: `uv sync`
- Run anything: `uv run python -m src.cli ...` or `uv run browser-agent ...`
- Add a dependency: `uv add <package>`
- Never use bare `python` or `pip install` — always go through `uv run` / `uv add`

## Docs

- [docs/setup.md](docs/setup.md) — installation and environment setup
- [docs/architecture.md](docs/architecture.md) — codebase structure, components, design decisions
- [docs/fix-vulns-task.md](docs/fix-vulns-task.md) — the fix-vulns Slack→code→PR pipeline

## Quick Reference

```bash
# Setup
uv sync && uv run playwright install chromium

# Free-form browser task
uv run python -m src.cli run "Go to github.com and check my notifications"

# Fix vulns from Slack
uv run python -m src.cli fix-vulns --repos-dir ~/Code
```

## Conventions

- Browser agent and coder agent are separate loops — tasks in `src/tasks/` orchestrate them
- Repos are always local (resolved via `--repos-dir`), never cloned
- `extract_data` tool captures structured JSON from browser sessions for downstream use
- Browser runs headed by default so the user can watch; pass `--headless` to disable
