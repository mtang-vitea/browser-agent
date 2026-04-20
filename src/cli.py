"""CLI client for the browser server.

Each subcommand sends a request to the running server and prints the result.
The coding agent (Claude Code / Codex) calls these commands and reads
screenshots with its built-in vision to decide what to do next.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_PORT = 9223
PID_FILE = ".browser-pid"


def send(command: str, port: int = DEFAULT_PORT, **args) -> dict:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect(("127.0.0.1", port))
    sock.sendall(json.dumps({"command": command, "args": args}).encode())
    chunks = []
    while True:
        chunk = sock.recv(65536)
        if not chunk:
            break
        chunks.append(chunk)
    sock.close()
    return json.loads(b"".join(chunks))


def server_is_running(port: int = DEFAULT_PORT) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect(("127.0.0.1", port))
        sock.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False


def wait_for_server(port: int = DEFAULT_PORT, timeout: int = 15) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if server_is_running(port):
            return True
        time.sleep(0.5)
    return False


def main():
    parser = argparse.ArgumentParser(description="Browser agent CLI")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    sub = parser.add_subparsers(dest="command")

    start_p = sub.add_parser("start", help="Start the browser server in the background")
    start_p.add_argument("--headless", action="store_true")

    nav_p = sub.add_parser("navigate", help="Navigate to a URL")
    nav_p.add_argument("url")

    click_p = sub.add_parser("click", help="Click at coordinates")
    click_p.add_argument("x", type=int)
    click_p.add_argument("y", type=int)

    type_p = sub.add_parser("type", help="Type text into the focused element")
    type_p.add_argument("text")
    type_p.add_argument("--enter", action="store_true", help="Press Enter after typing")

    key_p = sub.add_parser("key", help="Press a keyboard key or combo")
    key_p.add_argument("key_name")

    scroll_p = sub.add_parser("scroll", help="Scroll the page")
    scroll_p.add_argument("direction", choices=["up", "down"])
    scroll_p.add_argument("--amount", type=int, default=500)

    sub.add_parser("screenshot", help="Take a screenshot and print the file path")

    wait_p = sub.add_parser("wait", help="Wait for a number of seconds")
    wait_p.add_argument("seconds", type=float)

    sub.add_parser("url", help="Print the current page URL")
    sub.add_parser("title", help="Print the current page title")
    sub.add_parser("stop", help="Stop the browser server")
    sub.add_parser("status", help="Check if the server is running")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "start":
        if server_is_running(args.port):
            print(f"Server already running on port {args.port}")
            return

        cmd = [sys.executable, "-m", "src.server", "--port", str(args.port)]
        if args.headless:
            cmd.append("--headless")

        log = Path(".browser-server.log")
        proc = subprocess.Popen(
            cmd,
            stdout=log.open("w"),
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        print(f"Starting browser server (pid {proc.pid})...")

        if wait_for_server(args.port):
            print(f"Browser server ready on 127.0.0.1:{args.port}")
        else:
            print("Server failed to start. Check .browser-server.log", file=sys.stderr)
            sys.exit(1)
        return

    if args.command == "status":
        if server_is_running(args.port):
            pid = Path(PID_FILE).read_text().strip() if Path(PID_FILE).exists() else "unknown"
            print(f"Running on port {args.port} (pid {pid})")
        else:
            print("Not running")
        return

    if not server_is_running(args.port):
        print("Browser server is not running. Start it with: uv run python -m src.cli start", file=sys.stderr)
        sys.exit(1)

    match args.command:
        case "navigate":
            result = send("navigate", args.port, url=args.url)
        case "click":
            result = send("click", args.port, x=args.x, y=args.y)
        case "type":
            result = send("type", args.port, text=args.text, press_enter=args.enter)
        case "key":
            result = send("key", args.port, key=args.key_name)
        case "scroll":
            result = send("scroll", args.port, direction=args.direction, amount=args.amount)
        case "screenshot":
            result = send("screenshot", args.port)
        case "wait":
            result = send("wait", args.port, seconds=args.seconds)
        case "url":
            result = send("url", args.port)
        case "title":
            result = send("title", args.port)
        case "stop":
            result = send("stop", args.port)
            pid_path = Path(PID_FILE)
            if pid_path.exists():
                try:
                    os.kill(int(pid_path.read_text().strip()), signal.SIGTERM)
                except (ProcessLookupError, ValueError):
                    pass
                pid_path.unlink(missing_ok=True)
        case _:
            parser.print_help()
            return

    if not result.get("ok"):
        print(f"Error: {result.get('error', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    if "path" in result:
        print(result["path"])
    elif "url" in result:
        print(result["url"])
    elif "title" in result:
        print(result["title"])
    elif "result" in result:
        print(result["result"])


if __name__ == "__main__":
    main()
