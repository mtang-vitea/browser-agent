# Architecture

Browser Agent is a two-layer system: a **browser agent** that sees and interacts with web pages via screenshots, and a **coder agent** that reads/writes code in local repositories.

## Components

### Browser Layer (`src/browser.py`, `src/actions.py`)

Playwright wrapper that provides action primitives to the AI:

- `navigate(url)` — load a URL
- `click(x, y)` — click at pixel coordinates identified from the screenshot
- `type_text(text)` — type into the focused element
- `press_key(key)` — keyboard shortcuts (Enter, Tab, Meta+a, etc.)
- `scroll(direction, amount)` — scroll the page
- `wait(seconds)` — pause for loading
- `extract_data(data)` — capture structured JSON from the page for downstream use
- `done(summary)` — signal task completion

Screenshots are captured as base64 JPEG and sent to Claude's vision API each step.

### Agent Loop (`src/agent.py`)

The core loop that drives the browser:

1. Take a screenshot of the current page
2. Send screenshot + conversation history to Claude
3. Claude returns tool calls (click, type, navigate, etc.)
4. Execute the tool calls against the browser
5. Repeat until `done` is called or max steps (50) reached

Returns an `AgentResult` with a summary string and a list of any structured data captured via `extract_data`.

### Coder Agent (`src/coder.py`)

A separate Claude agent loop for code modifications. Given a local repo path and a task description, it uses tools to:

- `read_file` / `write_file` — read and modify files
- `list_directory` — explore the repo structure
- `search_code` — grep for patterns
- `run_command` — run shell commands (install deps, run tests, etc.)

The coder works directly on local repos — no cloning. Repos are resolved from a base directory via `--repos-dir`.

### Tasks (`src/tasks/`)

Orchestrators that combine the browser and coder agents into multi-phase workflows. Each task is a self-contained async function.

### CLI (`src/cli.py`)

Entry point with subcommands:

- `run <task>` — free-form browser automation
- `fix-vulns` — the vulnerability-fixing pipeline (see [fix-vulns task docs](./fix-vulns-task.md))

## Design Decisions

- **Headed browser by default** — the user can watch and intervene (pass `--headless` to disable)
- **Local repos only** — repos are found on disk via `--repos-dir`, no cloning
- **Separate agent loops** — browser agent and coder agent are independent; tasks orchestrate them
- **Step limits** — browser agent caps at 50 steps, coder at 30, to prevent runaway execution
- **JPEG screenshots** — quality=75 keeps token usage reasonable while remaining legible to Claude's vision
