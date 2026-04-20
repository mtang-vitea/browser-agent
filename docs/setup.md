# Setup

## Install

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
cd browser-agent
uv sync
uv run playwright install chromium
```

> **For coding agents (Claude Code / Codex):** Always use `uv run` to execute commands in this project. Do not use `pip install` or bare `python` — use `uv run python` or `uv run browser-agent` instead. To add a dependency, use `uv add <package>`.

## Environment

Copy `.env.example` to `.env` and set your API key:

```bash
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY
```

Or export it directly:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `gh` CLI — authenticated (`gh auth login`) for PR creation
- Chromium — installed via `uv run playwright install chromium`

## Quick Start

```bash
# Free-form browser task
uv run python -m src.cli run "Go to github.com and check my notifications"

# Fix vulnerabilities from Slack
uv run python -m src.cli fix-vulns --repos-dir ~/Code
```
