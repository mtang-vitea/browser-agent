from __future__ import annotations

import argparse
import asyncio

from dotenv import load_dotenv


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="AI browser agent powered by Claude")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a free-form browser task")
    run_parser.add_argument("task", help="Task description for the agent to perform")
    run_parser.add_argument("--headless", action="store_true", help="Run browser without GUI")
    run_parser.add_argument("--model", default="claude-sonnet-4-6", help="Claude model to use")

    vuln_parser = subparsers.add_parser("fix-vulns", help="Read Slack vuln report and fix vulnerabilities")
    vuln_parser.add_argument("--headless", action="store_true", help="Run browser without GUI")
    vuln_parser.add_argument("--model", default="claude-sonnet-4-6", help="Claude model to use")
    vuln_parser.add_argument("--org", default=None, help="GitHub org for repos (if not in vuln report)")

    args = parser.parse_args()

    if args.command == "fix-vulns":
        from .tasks.fix_vulns import run_fix_vulns

        asyncio.run(run_fix_vulns(
            headless=args.headless,
            model=args.model,
            github_org=args.org,
        ))
    elif args.command == "run":
        from .agent import run

        result = asyncio.run(run(args.task, headless=args.headless, model=args.model))
        print(f"\nResult: {result.summary}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
