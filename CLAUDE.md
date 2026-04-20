# Browser Agent

AI-powered browser automation using Claude's vision and Playwright.

## Setup

```bash
pip install -e .
playwright install chromium
```

## Run

```bash
python -m src.cli "Go to slack and read my latest messages"
```

## Architecture

- `src/browser.py` — Playwright wrapper with action primitives (click, type, scroll, navigate, screenshot)
- `src/agent.py` — Main agent loop: screenshot → Claude vision → execute tool calls → repeat
- `src/actions.py` — Tool definitions that Claude can invoke
- `src/cli.py` — CLI entry point

## Key decisions

- Uses headed browser (visible) by default so the user can watch and intervene
- Screenshots are sent as base64 images to Claude's vision API
- Agent loop caps at 50 steps to prevent runaway execution
- Browser state persists across steps (cookies, sessions) for multi-step tasks
