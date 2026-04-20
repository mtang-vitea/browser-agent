# Adding a New Task

Tasks are multi-phase orchestrators that combine the browser agent and/or coder agent to accomplish a workflow. Each task lives in `src/tasks/` as its own module.

## Steps

### 1. Create the task module

Add a new file in `src/tasks/`, e.g. `src/tasks/my_task.py`:

```python
from __future__ import annotations

from ..agent import run as run_browser_agent, AgentResult
from ..coder import fix_vulnerability  # if you need code modifications


# Prompt that tells the browser agent exactly what to do.
# Be specific — include step-by-step instructions and the
# exact JSON schema you want from extract_data.
BROWSER_PROMPT = """Your task: ...

Steps:
1. Navigate to ...
2. Find ...
3. Use extract_data to capture structured data:
   {
     "key": "value schema here"
   }
4. Call done when finished."""


async def run_my_task(
    headless: bool = False,
    model: str = "claude-sonnet-4-6",
) -> None:
    # Phase 1: Browser agent gathers information
    result: AgentResult = await run_browser_agent(
        task=BROWSER_PROMPT,
        headless=headless,
        model=model,
    )

    # result.extracted_data is a list of dicts from extract_data calls
    # result.summary is the string from the done tool

    # Phase 2: Act on the extracted data
    for item in result.extracted_data:
        print(item)
        # ... do work (call coder agent, run commands, etc.)
```

**Key APIs:**

| Function | Import | Purpose |
|---|---|---|
| `run(task, headless, model, system_prompt)` | `from ..agent import run` | Run the browser agent. Returns `AgentResult` with `.summary` and `.extracted_data`. Pass `system_prompt` to override the default. |
| `fix_vulnerability(repo_path, vuln_description, model)` | `from ..coder import fix_vulnerability` | Run the coder agent on a local repo. Returns a summary string of changes made. |

### 2. Register the CLI subcommand

Add a subparser in `src/cli.py`:

```python
# In main(), after the existing subparsers:
my_parser = subparsers.add_parser("my-task", help="Description of what this task does")
my_parser.add_argument("--headless", action="store_true", help="Run browser without GUI")
my_parser.add_argument("--model", default="claude-sonnet-4-6", help="Claude model to use")
# Add any task-specific flags here

# In the if/elif chain:
elif args.command == "my-task":
    from .tasks.my_task import run_my_task

    asyncio.run(run_my_task(
        headless=args.headless,
        model=args.model,
    ))
```

### 3. Write a task doc

Create `docs/my-task.md` documenting:

- **Usage** — CLI command with all flags
- **How it works** — what the browser agent does, what happens with the extracted data
- **Prerequisites** — any logins, CLI tools, or local state required

### 4. Update the indexes

Add a link to the new task doc in **all three places**:

- `CLAUDE.md` — under the `## Docs` section
- `AGENTS.md` — under the `## Docs` section (keep them in sync)
- `docs/architecture.md` — under `### CLI` to document the new subcommand

## Guidelines

- **Browser prompts should be very specific.** Include step-by-step instructions and the exact JSON schema for `extract_data`. Vague prompts lead to unreliable extraction.
- **Use `extract_data` before `done`.** The browser agent can call `extract_data` multiple times to accumulate structured data. Call it as you read information, not all at once at the end.
- **Keep tasks async.** The browser agent is async, so task entry points should be `async def` and called with `asyncio.run()` from the CLI.
- **Tasks can be browser-only, coder-only, or both.** Not every task needs both agents — a task that just reads a webpage and prints a summary only needs the browser agent.
- **Validate extracted data.** The browser agent returns whatever Claude puts in `extract_data` — check for missing keys before acting on it.
- **Use `system_prompt` to specialize.** Pass a custom system prompt to `run()` if the default browser agent persona isn't right for your task.

## Example: Browser-Only Task

A task that just reads information without modifying any code:

```python
async def run_check_status(headless: bool = False, model: str = "claude-sonnet-4-6") -> None:
    result = await run_browser_agent(
        task="Go to https://status.example.com and extract_data with the current status of each service. Call done when finished.",
        headless=headless,
        model=model,
    )

    for data in result.extracted_data:
        for service, status in data.items():
            print(f"  {service}: {status}")
```
