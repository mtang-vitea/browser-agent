# Setup

## Install

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
cd browser-agent
uv sync
uv run playwright install chromium
```

> **For coding agents (Claude Code / Codex):** Always use `uv run` to execute commands in this project. Do not use `pip install` or bare `python` — use `uv run python` instead. To add a dependency, use `uv add <package>`.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `gh` CLI — authenticated (`gh auth login`) for PR creation in tasks that open PRs
- Chromium — installed via `uv run playwright install chromium`

## Quick Start

```bash
# Start the browser
uv run python -m src.cli start

# Navigate somewhere
uv run python -m src.cli navigate "https://example.com"

# Take a screenshot (prints the file path — read it with your vision)
uv run python -m src.cli screenshot

# Click, type, interact
uv run python -m src.cli click 640 450
uv run python -m src.cli type "hello world" --enter

# Stop when done
uv run python -m src.cli stop
```
