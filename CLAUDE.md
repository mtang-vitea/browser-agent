# Browser Agent

AI-powered browser automation using Claude's vision and Playwright.

## Setup

```bash
pip install -e .
playwright install chromium
```

## Run

```bash
# Free-form browser task
python -m src.cli run "Go to slack and read my latest messages"

# Fix vulnerabilities from Slack report
python -m src.cli fix-vulns
python -m src.cli fix-vulns --model claude-sonnet-4-6 --org vitea-ai
```

## Architecture

- `src/browser.py` — Playwright wrapper with action primitives (click, type, scroll, navigate, screenshot)
- `src/agent.py` — Main agent loop: screenshot → Claude vision → execute tool calls → repeat. Returns `AgentResult` with summary + extracted structured data.
- `src/actions.py` — Tool definitions that Claude can invoke (including `extract_data` for structured output)
- `src/coder.py` — Code-fixing agent: Claude with file read/write/search tools to fix vulnerabilities in cloned repos
- `src/tasks/fix_vulns.py` — Two-phase task: (1) browser agent reads Slack #vulnerabilities channel, (2) coder agent fixes each vuln and opens PRs
- `src/cli.py` — CLI entry point with subcommands: `run` (free-form) and `fix-vulns`

## Key decisions

- Uses headed browser (visible) by default so the user can watch and intervene
- Screenshots are sent as base64 JPEG to Claude's vision API
- Agent loop caps at 50 steps to prevent runaway execution
- Browser state persists across steps (cookies, sessions) for multi-step tasks
- Coder agent shallow-clones repos to temp dirs, pushes fix branches, creates PRs via `gh`
