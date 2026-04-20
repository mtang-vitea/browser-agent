# Browser Agent

Browser automation server for coding agents. You drive the browser via CLI commands and read screenshots with your vision to decide what to do.

> **Dual-agent repo**: This project uses both `AGENTS.md` (Codex) and `CLAUDE.md` (Claude Code). They share documentation via `docs/`. **When updating either file, update the other to match.** When updating shared docs in `docs/`, no sync is needed — both files reference them.

## Package Manager

This project uses **uv** — not pip, not poetry, not conda.

- Install deps: `uv sync`
- Run anything: `uv run python -m src.cli ...`
- Add a dependency: `uv add <package>`
- Never use bare `python` or `pip install` — always go through `uv run` / `uv add`

## Browser Commands

All commands: `uv run python -m src.cli <command>`

```bash
start [--headless]      # Launch browser server
navigate <url>          # Go to URL
click <x> <y>           # Click at coordinates
type <text> [--enter]   # Type text
key <key>               # Press key (Enter, Tab, Meta+k, etc.)
scroll <up|down>        # Scroll page
screenshot              # Take screenshot — read the printed path with your vision
wait <seconds>          # Wait for page load
url                     # Print current URL
title                   # Print current page title
status                  # Check if server is running
stop                    # Shut down browser
```

## Workflow

1. `uv run python -m src.cli start` — launch the browser
2. `uv run python -m src.cli navigate "https://..."` — go somewhere
3. `uv run python -m src.cli screenshot` — take a screenshot, then **read the file** to see the page
4. Decide what to click/type based on the screenshot
5. Repeat 2–4 until the task is done
6. `uv run python -m src.cli stop` — shut down

## Docs

- [docs/setup.md](docs/setup.md) — installation and environment setup
- [docs/architecture.md](docs/architecture.md) — how the server and CLI work
- [docs/fix-vulns-task.md](docs/fix-vulns-task.md) — task: read Slack vulns, fix repos, open PRs
- [docs/adding-a-task.md](docs/adding-a-task.md) — how to add a new task

## Conventions

- **No AI APIs** — you are the AI. This project is pure browser automation tooling.
- Repos are always local — never clone, work on existing checkouts
- Screenshot at every decision point so you can see the page
- Browser runs headed by default so the user can watch; pass `--headless` to `start` to disable
