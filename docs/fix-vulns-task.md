# Fix Vulnerabilities Task

Read the latest vulnerability report from Slack, then fix each vulnerability in the local repos and open PRs.

## Workflow

### Phase 1: Read the Slack vulnerability report

```bash
# Start the browser
uv run python -m src.cli start

# Go to Slack
uv run python -m src.cli navigate "https://app.slack.com"
uv run python -m src.cli screenshot
# → Read the screenshot. If login is needed, wait for the user to log in manually.

# Find the #vulnerabilities channel (Ctrl+K to search)
uv run python -m src.cli key "Meta+k"
uv run python -m src.cli screenshot
uv run python -m src.cli type "vulnerabilities" --enter
uv run python -m src.cli wait 2
uv run python -m src.cli screenshot

# Read the latest message from Vuln Scanner
# Scroll as needed to read the full message
uv run python -m src.cli screenshot
uv run python -m src.cli scroll down
uv run python -m src.cli screenshot
```

After reading the message, extract the vulnerability details:
- Repository name (e.g. `vitea-ai/backend`)
- Package name and versions (current → fixed)
- CVE identifier
- Severity

### Phase 2: Fix each vulnerability

For each repo listed in the report:

1. **Find the repo locally** — check `~/Code/{repo-name}` or `~/Code/{org}/{repo-name}`
2. **Create a fix branch:**
   ```bash
   cd ~/Code/{repo-name}
   git checkout -b fix/{cve-or-package-name}
   ```
3. **Fix the vulnerability** — find the dependency file (`package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, etc.), upgrade the affected package to the fixed version, and run the appropriate install/lock command
4. **Verify** — run tests if available
5. **Commit, push, and open a PR:**
   ```bash
   git add -A
   git commit -m "fix: upgrade {package} to {fixed_version} ({cve})"
   git push -u origin fix/{cve-or-package-name}
   gh pr create --title "fix: {cve} — upgrade {package}" --body "## Vulnerability Fix\n\n**CVE:** {cve}\n**Package:** {package}\n**Severity:** {severity}\n**Version:** {current} → {fixed}\n"
   ```
6. **Return to main** — `git checkout main`

Repeat for each vulnerability, one repo at a time.

### Phase 3: Clean up

```bash
# Stop the browser when done with Slack
uv run python -m src.cli stop
```

## Prerequisites

- Logged into Slack in the browser (or ready to log in when prompted)
- `gh` CLI authenticated with push access to the target repos
- Local clones of the repos at `~/Code/`
