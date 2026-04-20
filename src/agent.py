from __future__ import annotations

import anthropic

from .actions import TOOLS
from .browser import BrowserSession

MAX_STEPS = 50

SYSTEM_PROMPT = """You are a browser automation agent. You can see the current state of a web browser via screenshots and perform actions to accomplish the user's task.

Guidelines:
- Look at the screenshot carefully to understand the current page state before acting.
- Click on specific coordinates you can see in the screenshot.
- If a page is loading, use the wait tool.
- If you need to scroll to see more content, use the scroll tool.
- When the task is complete, call the done tool with a summary.
- If you get stuck, try a different approach rather than repeating the same action.
- For login pages, describe what you see and ask the user to log in manually if credentials are needed."""


async def run(task: str, headless: bool = False, model: str = "claude-sonnet-4-6") -> str:
    client = anthropic.Anthropic()
    browser = BrowserSession(headless=headless)
    await browser.start()

    messages = [{"role": "user", "content": task}]

    try:
        for step in range(MAX_STEPS):
            screenshot_b64 = await browser.screenshot()

            if messages[-1]["role"] == "user":
                messages[-1]["content"] = [
                    {"type": "text", "text": messages[-1]["content"]}
                    if isinstance(messages[-1]["content"], str)
                    else *messages[-1]["content"],
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": screenshot_b64,
                        },
                    },
                ]
            else:
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": screenshot_b64,
                                },
                            }
                        ],
                    }
                )

            print(f"\n--- Step {step + 1} ---")

            response = client.messages.create(
                model=model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages,
            )

            assistant_content = response.content
            messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            done_summary = None

            for block in assistant_content:
                if block.type == "text" and block.text:
                    print(f"Agent: {block.text}")
                elif block.type == "tool_use":
                    name = block.name
                    args = block.input
                    print(f"Action: {name}({args})")

                    if name == "done":
                        done_summary = args["summary"]
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": "Task complete.",
                            }
                        )
                        break

                    result = await _execute(browser, name, args)
                    print(f"Result: {result}")
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            if done_summary:
                print(f"\n=== Task Complete ===\n{done_summary}")
                return done_summary

            if tool_results:
                messages.append({"role": "user", "content": tool_results})

            if response.stop_reason == "end_turn" and not tool_results:
                print("\nAgent stopped without calling done.")
                break

        return "Reached maximum steps without completing the task."
    finally:
        await browser.stop()


async def _execute(browser: BrowserSession, name: str, args: dict) -> str:
    match name:
        case "navigate":
            return await browser.navigate(args["url"])
        case "click":
            return await browser.click(args["x"], args["y"])
        case "type_text":
            return await browser.type_text(args["text"], args.get("press_enter", False))
        case "press_key":
            return await browser.press_key(args["key"])
        case "scroll":
            return await browser.scroll(args["direction"], args.get("amount", 500))
        case "wait":
            return await browser.wait(args["seconds"])
        case _:
            return f"Unknown action: {name}"
