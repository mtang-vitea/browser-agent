from __future__ import annotations

import os
import subprocess

from ..agent import run as run_browser_agent
from ..coder import fix_vulnerability

SLACK_TASK_PROMPT = """Your task: Go to Slack and find vulnerability scanner results.

Steps:
1. Navigate to https://app.slack.com
2. If you need to log in, describe what you see and wait for the user. Otherwise continue.
3. Find the channel called "vulnerabilities" (use Ctrl+K or the channel sidebar to search).
4. Once in the channel, find the most recent message from "Vuln Scanner" (or similar bot name).
5. Read the full message carefully. It should list one or more repositories with vulnerability details.
6. Use extract_data to capture the vulnerability information in this exact JSON structure:
   {
     "vulnerabilities": [
       {
         "repo": "org/repo-name",
         "package": "affected-package-name",
         "current_version": "x.y.z",
         "fixed_version": "a.b.c",
         "severity": "critical|high|medium|low",
         "cve": "CVE-XXXX-XXXXX",
         "description": "Brief description of the vulnerability"
       }
     ]
   }
7. If the message is long, scroll to read all of it and capture ALL vulnerabilities.
8. Call done when you've extracted everything.

Be thorough — capture every vulnerability mentioned in the message."""


def _resolve_repo_path(repos_dir: str, repo_identifier: str) -> str | None:
    """Find a repo on disk given a name like 'org/repo' or just 'repo'."""
    parts = repo_identifier.strip().split("/")
    repo_name = parts[-1]

    candidates = [
        os.path.join(repos_dir, repo_name),
        os.path.join(repos_dir, *parts),
    ]

    for candidate in candidates:
        if os.path.isdir(os.path.join(candidate, ".git")):
            return candidate

    return None


async def run_fix_vulns(
    repos_dir: str,
    headless: bool = False,
    model: str = "claude-sonnet-4-6",
) -> None:
    print("=" * 60)
    print("PHASE 1: Reading vulnerability report from Slack")
    print("=" * 60)

    result = await run_browser_agent(
        task=SLACK_TASK_PROMPT,
        headless=headless,
        model=model,
    )

    vulns = []
    for data in result.extracted_data:
        vulns.extend(data.get("vulnerabilities", []))

    if not vulns:
        print("\nNo vulnerabilities extracted from Slack. Exiting.")
        return

    print(f"\nFound {len(vulns)} vulnerabilities to fix:")
    for i, v in enumerate(vulns, 1):
        print(f"  {i}. [{v.get('severity', '?').upper()}] {v.get('repo', '?')} — "
              f"{v.get('package', '?')} {v.get('cve', '')}")

    print(f"\nResolving repos from: {repos_dir}")

    print("\n" + "=" * 60)
    print("PHASE 2: Fixing vulnerabilities")
    print("=" * 60)

    repos_processed: set[str] = set()

    for i, vuln in enumerate(vulns, 1):
        repo = vuln.get("repo", "")
        if not repo:
            print(f"\n[{i}/{len(vulns)}] Skipping — no repo specified")
            continue

        print(f"\n{'—' * 40}")
        print(f"[{i}/{len(vulns)}] Fixing: {repo}")
        print(f"  Package: {vuln.get('package', 'unknown')}")
        print(f"  CVE: {vuln.get('cve', 'N/A')}")
        print(f"  Severity: {vuln.get('severity', 'unknown')}")
        print(f"{'—' * 40}")

        repo_path = _resolve_repo_path(repos_dir, repo)
        if not repo_path:
            print(f"  Repo not found locally. Searched:")
            parts = repo.split("/")
            print(f"    - {os.path.join(repos_dir, parts[-1])}")
            if len(parts) > 1:
                print(f"    - {os.path.join(repos_dir, *parts)}")
            print(f"  Skipping.")
            continue

        print(f"  Found at: {repo_path}")

        branch_name = f"fix/{vuln.get('cve', vuln.get('package', 'vuln')).lower().replace(' ', '-')}"

        print(f"  Creating branch: {branch_name}")
        _run_git(repo_path, ["checkout", "-b", branch_name])

        vuln_desc = _format_vuln_description(vuln)

        print(f"  Running coder agent...")
        fix_summary = fix_vulnerability(
            repo_path=repo_path,
            vuln_description=vuln_desc,
            model=model,
        )

        has_changes = subprocess.run(
            ["git", "diff", "--quiet"], cwd=repo_path, capture_output=True
        ).returncode != 0

        has_staged = subprocess.run(
            ["git", "diff", "--cached", "--quiet"], cwd=repo_path, capture_output=True
        ).returncode != 0

        has_untracked = bool(subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=repo_path, capture_output=True, text=True
        ).stdout.strip())

        if not (has_changes or has_staged or has_untracked):
            print(f"  No changes detected — skipping PR creation")
            _run_git(repo_path, ["checkout", "-"])
            _run_git(repo_path, ["branch", "-D", branch_name])
            continue

        print(f"  Committing and pushing...")
        _run_git(repo_path, ["add", "-A"])
        _run_git(repo_path, [
            "commit", "-m",
            f"fix: {vuln.get('package', 'dependency')} vulnerability ({vuln.get('cve', 'security fix')})\n\n{fix_summary}"
        ])
        _run_git(repo_path, ["push", "-u", "origin", branch_name])

        pr_title = f"fix: {vuln.get('cve', 'Security fix')} — upgrade {vuln.get('package', 'dependency')}"
        pr_body = f"""## Vulnerability Fix

**CVE:** {vuln.get('cve', 'N/A')}
**Package:** {vuln.get('package', 'unknown')}
**Severity:** {vuln.get('severity', 'unknown')}
**Current Version:** {vuln.get('current_version', '?')} → **Fixed Version:** {vuln.get('fixed_version', '?')}

## Description
{vuln.get('description', 'Security vulnerability fix.')}

## Changes
{fix_summary}
"""
        pr_result = subprocess.run(
            ["gh", "pr", "create", "--title", pr_title, "--body", pr_body],
            cwd=repo_path, capture_output=True, text=True, timeout=30,
        )
        if pr_result.returncode == 0:
            pr_url = pr_result.stdout.strip()
            print(f"  PR created: {pr_url}")
        else:
            print(f"  PR creation failed: {pr_result.stderr}")

        repos_processed.add(repo)

    print("\n" + "=" * 60)
    print(f"Done. Processed {len(repos_processed)} repos, {len(vulns)} vulnerabilities.")
    print("=" * 60)


def _format_vuln_description(vuln: dict) -> str:
    lines = [
        f"Repository: {vuln.get('repo', 'unknown')}",
        f"Vulnerable package: {vuln.get('package', 'unknown')}",
        f"Current version: {vuln.get('current_version', 'unknown')}",
        f"Fixed version: {vuln.get('fixed_version', 'unknown')}",
        f"CVE: {vuln.get('cve', 'N/A')}",
        f"Severity: {vuln.get('severity', 'unknown')}",
        f"Description: {vuln.get('description', 'No description provided')}",
        "",
        "Fix this vulnerability by upgrading the package to the fixed version.",
        "Find the relevant dependency file (package.json, requirements.txt, pyproject.toml, go.mod, Gemfile, pom.xml, etc.),",
        "update the version, and run the appropriate install/lock command to update the lockfile.",
    ]
    return "\n".join(lines)


def _run_git(repo_path: str, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo_path, capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"  git {' '.join(args)} failed: {result.stderr}")
    return result.stdout
