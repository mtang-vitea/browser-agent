# Adding a New Task

Tasks are documented workflows that a coding agent (Claude Code / Codex) follows using the browser CLI and its native tools. Each task is a markdown file in `docs/` that describes what to do step by step.

## What a task doc should include

1. **Workflow** — step-by-step instructions with the exact CLI commands to run. Include `screenshot` calls at decision points so the agent can see what's on screen.
2. **What to extract** — describe what information the agent should read from the browser (e.g. message contents, table data, status indicators).
3. **What to do with it** — describe the actions to take with the extracted information (e.g. edit files, run commands, open PRs).
4. **Prerequisites** — logins, CLI tools, local state the agent needs before starting.

## Pattern

Most tasks follow this structure:

```bash
# 1. Start the browser
uv run python -m src.cli start

# 2. Navigate and interact
uv run python -m src.cli navigate "https://..."
uv run python -m src.cli screenshot
# → Agent reads the screenshot and decides what to click/type

# 3. Extract information by reading screenshots
uv run python -m src.cli screenshot
# → Agent reads the page content from the screenshot

# 4. Act on the information using native tools
# (edit files, run git commands, open PRs, etc.)

# 5. Clean up
uv run python -m src.cli stop
```

## Available browser commands

| Command | Description |
|---|---|
| `start [--headless]` | Launch the browser server |
| `navigate <url>` | Go to a URL |
| `click <x> <y>` | Click at pixel coordinates (read from screenshot) |
| `type <text> [--enter]` | Type text into the focused element |
| `key <key>` | Press a key or combo (Enter, Tab, Meta+k) |
| `scroll <up\|down> [--amount N]` | Scroll the page |
| `screenshot` | Take a screenshot — prints file path for the agent to read |
| `wait <seconds>` | Wait for page loads |
| `url` | Print current URL |
| `title` | Print current page title |
| `stop` | Shut down the browser |

All commands are prefixed with `uv run python -m src.cli`.

## Tips

- **Screenshot at every decision point.** The agent needs to see the page to know where to click. Take a screenshot after every navigation, click, or page change.
- **Use `key "Meta+k"` for Slack search, `key "Meta+a"` for select-all**, etc. Check the app's keyboard shortcuts.
- **The browser persists between commands.** Login sessions, cookies, and page state carry over — no need to re-authenticate on every command.
- **Headed mode is default.** The user can watch and intervene. Use `--headless` only for fully automated runs.

## After writing the task doc

Add a link to it in **all three places**:

- `CLAUDE.md` — under the `## Docs` section
- `AGENTS.md` — under the `## Docs` section (keep them in sync)
- `docs/architecture.md` — mention the new task
