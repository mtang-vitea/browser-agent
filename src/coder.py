from __future__ import annotations

import os
import subprocess
from pathlib import Path

import anthropic

MAX_STEPS = 30

CODER_TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file in the repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to repo root"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file (creates or overwrites).",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to repo root"},
                "content": {"type": "string", "description": "Full file content to write"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and directories at a path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path relative to repo root", "default": "."},
            },
        },
    },
    {
        "name": "search_code",
        "description": "Search for a regex pattern across the codebase (recursive grep).",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Regex search pattern"},
                "path": {"type": "string", "description": "Directory to search in (default: repo root)", "default": "."},
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "run_command",
        "description": "Run a shell command in the repo directory. Use for package manager commands, tests, etc.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"},
            },
            "required": ["command"],
        },
    },
    {
        "name": "done",
        "description": "Signal that the vulnerability fix is complete.",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "description": "Summary of changes made to fix the vulnerability"},
            },
            "required": ["summary"],
        },
    },
]


def _exec(cmd: str, cwd: str, timeout: int = 60) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout + result.stderr
        return output[:4000] if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "(command timed out)"


def fix_vulnerability(
    repo_path: str,
    vuln_description: str,
    model: str = "claude-sonnet-4-6",
) -> str:
    client = anthropic.Anthropic()

    system = f"""You are a security engineer fixing a vulnerability in a code repository.
The repo is cloned locally at: {repo_path}

Your job:
1. Understand the vulnerability described below.
2. Find the affected code/dependency in the repo.
3. Apply the minimal fix (upgrade a dependency version, patch code, etc.).
4. Run any available tests or build commands to verify the fix doesn't break things.
5. Call done with a summary of what you changed.

Be precise — only change what's necessary to fix the vulnerability."""

    messages = [
        {
            "role": "user",
            "content": f"Fix this vulnerability:\n\n{vuln_description}",
        }
    ]

    for step in range(MAX_STEPS):
        print(f"  [coder step {step + 1}]")

        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            tools=CODER_TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []

        for block in response.content:
            if block.type == "text" and block.text:
                print(f"  Coder: {block.text[:200]}")
            elif block.type == "tool_use":
                name = block.name
                args = block.input
                print(f"  Action: {name}({list(args.keys())})")

                if name == "done":
                    summary = args["summary"]
                    print(f"  Fix complete: {summary}")
                    return summary

                result = _execute_coder_tool(repo_path, name, args)
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    }
                )

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

        if response.stop_reason == "end_turn" and not tool_results:
            return "Coder stopped without completing the fix."

    return "Reached maximum steps without completing the fix."


def _execute_coder_tool(repo_path: str, name: str, args: dict) -> str:
    match name:
        case "read_file":
            fpath = os.path.join(repo_path, args["path"])
            try:
                content = Path(fpath).read_text()
                return content[:8000] if len(content) > 8000 else content
            except FileNotFoundError:
                return f"File not found: {args['path']}"
            except Exception as e:
                return f"Error reading file: {e}"

        case "write_file":
            fpath = os.path.join(repo_path, args["path"])
            Path(fpath).parent.mkdir(parents=True, exist_ok=True)
            Path(fpath).write_text(args["content"])
            return f"Wrote {len(args['content'])} bytes to {args['path']}"

        case "list_directory":
            dpath = os.path.join(repo_path, args.get("path", "."))
            try:
                entries = sorted(os.listdir(dpath))
                return "\n".join(entries)
            except FileNotFoundError:
                return f"Directory not found: {args.get('path', '.')}"

        case "search_code":
            pattern = args["pattern"]
            search_path = args.get("path", ".")
            return _exec(f"grep -rn --include='*' '{pattern}' {search_path}", repo_path)

        case "run_command":
            return _exec(args["command"], repo_path)

        case _:
            return f"Unknown tool: {name}"
