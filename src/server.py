"""Background browser server.

Manages a persistent Playwright browser and accepts commands over TCP.
Start directly: uv run python -m src.server
Or via CLI:     uv run python -m src.cli start
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from .browser import BrowserSession

DEFAULT_PORT = 9223
PID_FILE = ".browser-pid"


async def handle(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, browser: BrowserSession) -> bool:
    data = await reader.read(65536)
    if not data:
        writer.close()
        return False

    request = json.loads(data.decode())
    command = request.get("command", "")
    args = request.get("args", {})

    result = await execute(browser, command, args)

    writer.write(json.dumps(result).encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()

    return command == "stop"


async def execute(browser: BrowserSession, command: str, args: dict) -> dict:
    try:
        match command:
            case "navigate":
                msg = await browser.navigate(args["url"])
                return {"ok": True, "result": msg}
            case "click":
                msg = await browser.click(int(args["x"]), int(args["y"]))
                return {"ok": True, "result": msg}
            case "type":
                msg = await browser.type_text(args["text"], args.get("press_enter", False))
                return {"ok": True, "result": msg}
            case "key":
                msg = await browser.press_key(args["key"])
                return {"ok": True, "result": msg}
            case "scroll":
                msg = await browser.scroll(args["direction"], int(args.get("amount", 500)))
                return {"ok": True, "result": msg}
            case "screenshot":
                path = await browser.screenshot()
                return {"ok": True, "path": path}
            case "wait":
                msg = await browser.wait(float(args.get("seconds", 1)))
                return {"ok": True, "result": msg}
            case "url":
                return {"ok": True, "url": browser.page.url}
            case "title":
                return {"ok": True, "title": await browser.page.title()}
            case "stop":
                return {"ok": True, "result": "Server stopping."}
            case _:
                return {"ok": False, "error": f"Unknown command: {command}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


async def main(port: int = DEFAULT_PORT, headless: bool = False) -> None:
    browser = BrowserSession(headless=headless)
    await browser.start()
    Path(PID_FILE).write_text(str(os.getpid()))

    stop_event = asyncio.Event()

    async def on_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        should_stop = await handle(reader, writer, browser)
        if should_stop:
            stop_event.set()

    server = await asyncio.start_server(on_connection, "127.0.0.1", port)
    print(f"Browser server ready on 127.0.0.1:{port} (pid {os.getpid()})")

    await stop_event.wait()

    server.close()
    await server.wait_closed()
    await browser.stop()
    Path(PID_FILE).unlink(missing_ok=True)
    print("Browser server stopped.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(port=args.port, headless=args.headless))
