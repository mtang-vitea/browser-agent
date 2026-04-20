# Architecture

Browser Agent is a **tool for coding agents** — it provides a persistent browser that Claude Code or Codex can drive via CLI commands and observe via screenshots.

The coding agent is the intelligence layer. This project provides no AI of its own; it's pure browser automation infrastructure.

## How It Works

```
Coding Agent (Claude Code / Codex)
  │
  ├── runs CLI commands ──→  src/cli.py ──→ TCP ──→ src/server.py
  │                                                      │
  ├── reads screenshot files ←── screenshots/latest.png ←┘
  │
  └── decides what to do next (click, type, navigate, etc.)
```

1. The agent starts the browser server (`uv run python -m src.cli start`)
2. The agent sends commands (`navigate`, `click`, `type`, `screenshot`, etc.)
3. For `screenshot`, the server saves a PNG to disk and returns the file path
4. The agent reads the screenshot with its built-in vision to understand the page
5. The agent decides what to do next and sends the appropriate command
6. When done, the agent stops the server (`uv run python -m src.cli stop`)

## Components

### Browser Server (`src/server.py`)

A background TCP server (127.0.0.1:9223) that manages a persistent Playwright Chromium browser. Accepts JSON commands, executes them against the browser, and returns JSON results.

The server is long-lived — it stays running between CLI calls so the browser session (cookies, logins, page state) persists across commands.

### CLI Client (`src/cli.py`)

Thin client that sends commands to the server. Each subcommand maps to one browser action:

| Command | Description |
|---|---|
| `start [--headless]` | Launch the browser server in the background |
| `navigate <url>` | Go to a URL |
| `click <x> <y>` | Click at pixel coordinates |
| `type <text> [--enter]` | Type text into the focused element |
| `key <key>` | Press a key or combo (Enter, Tab, Meta+a) |
| `scroll <up\|down> [--amount N]` | Scroll the page |
| `screenshot` | Save screenshot to disk, print the file path |
| `wait <seconds>` | Wait (useful for page loads) |
| `url` | Print the current page URL |
| `title` | Print the current page title |
| `status` | Check if the server is running |
| `stop` | Shut down the browser and server |

### Browser Wrapper (`src/browser.py`)

Playwright wrapper used internally by the server. Handles viewport configuration, screenshot numbering, and action execution.

## Design Decisions

- **No AI dependencies** — no Anthropic SDK, no OpenAI SDK. The coding agent running this IS the AI.
- **CLI-driven** — every action is a simple shell command the agent can run via Bash.
- **Screenshots to disk** — saved as PNG files the agent reads with its built-in vision. Numbered sequentially (`step_001.png`, `step_002.png`, ...) plus a `latest.png` symlink.
- **Persistent browser** — the TCP server keeps the browser alive between commands so login sessions and page state carry over.
- **Headed by default** — the user can watch what's happening. Pass `--headless` to `start` for background execution.
