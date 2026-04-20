# Browser Agent

AI-powered browser automation using Claude's vision and Playwright.

> **Dual-agent repo**: This project uses both `AGENTS.md` (Codex) and `CLAUDE.md` (Claude Code). They share documentation via `docs/`. **When updating either file, update the other to match.** When updating shared docs in `docs/`, no sync is needed — both files reference them.

## Docs

- [docs/setup.md](docs/setup.md) — installation and environment setup
- [docs/architecture.md](docs/architecture.md) — codebase structure, components, design decisions
- [docs/fix-vulns-task.md](docs/fix-vulns-task.md) — the fix-vulns Slack→code→PR pipeline

## Quick Reference

```bash
# Setup
pip install -e . && playwright install chromium

# Free-form browser task
python -m src.cli run "Go to github.com and check my notifications"

# Fix vulns from Slack
python -m src.cli fix-vulns --repos-dir ~/Code
```

## Conventions

- Browser agent and coder agent are separate loops — tasks in `src/tasks/` orchestrate them
- Repos are always local (resolved via `--repos-dir`), never cloned
- `extract_data` tool captures structured JSON from browser sessions for downstream use
- Browser runs headed by default so the user can watch; pass `--headless` to disable
