from __future__ import annotations

import argparse
import asyncio

from dotenv import load_dotenv


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="AI browser agent powered by Claude")
    parser.add_argument("task", help="Task description for the agent to perform")
    parser.add_argument("--headless", action="store_true", help="Run browser without GUI")
    parser.add_argument("--model", default="claude-sonnet-4-6", help="Claude model to use")
    args = parser.parse_args()

    from .agent import run

    result = asyncio.run(run(args.task, headless=args.headless, model=args.model))
    print(f"\nResult: {result}")


if __name__ == "__main__":
    main()
