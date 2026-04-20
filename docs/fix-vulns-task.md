# Fix Vulnerabilities Task

Reads a vulnerability report from Slack, then fixes each vulnerability in-place on local repos and opens PRs.

## Usage

```bash
uv run python -m src.cli fix-vulns --repos-dir ~/Code
uv run python -m src.cli fix-vulns --repos-dir ~/Code --model claude-sonnet-4-6
uv run python -m src.cli fix-vulns --repos-dir ~/Code --headless
```

### Required flags

- `--repos-dir` — base directory where repositories live on your machine. The task resolves repo names from the Slack message to local paths by searching this directory. For example, if Slack says `vitea-ai/backend`, it looks for `~/Code/backend` or `~/Code/vitea-ai/backend`.

### Optional flags

- `--headless` — run the browser without a visible window
- `--model` — Claude model to use (default: `claude-sonnet-4-6`)

## How It Works

### Phase 1: Read Slack

The browser agent:

1. Opens `https://app.slack.com`
2. Navigates to the `#vulnerabilities` channel (via Ctrl+K search)
3. Finds the most recent message from **Vuln Scanner**
4. Extracts structured vulnerability data using `extract_data`:

```json
{
  "vulnerabilities": [
    {
      "repo": "org/repo-name",
      "package": "affected-package",
      "current_version": "x.y.z",
      "fixed_version": "a.b.c",
      "severity": "critical|high|medium|low",
      "cve": "CVE-XXXX-XXXXX",
      "description": "Brief description"
    }
  ]
}
```

If the user is not logged into Slack, the agent will pause and describe the login page so the user can authenticate manually.

### Phase 2: Fix Each Vulnerability

For each vulnerability, the task:

1. **Resolves the local repo path** — looks for `{repos_dir}/{repo_name}` and `{repos_dir}/{org}/{repo_name}`
2. **Creates a fix branch** — `fix/{cve-or-package-name}` branched from the current HEAD
3. **Runs the coder agent** — Claude analyzes the repo, finds the dependency file, upgrades the package, runs install/lock commands, and verifies with tests
4. **Commits and pushes** — stages all changes, commits with a descriptive message
5. **Opens a PR** — via `gh pr create` with CVE, severity, description, and change summary

### Repo Resolution

Given a repo identifier like `vitea-ai/backend` and `--repos-dir ~/Code`, the task tries these paths in order:

1. `~/Code/backend` (repo name only)
2. `~/Code/vitea-ai/backend` (org/repo-name)

If neither exists, the vulnerability is skipped with a warning.

## Prerequisites

- Logged into Slack in a Chromium-compatible browser (or be ready to log in when prompted)
- `gh` CLI authenticated with push access to the target repos
- Local clones of the repos that may appear in vulnerability reports
- `ANTHROPIC_API_KEY` set in environment or `.env`
