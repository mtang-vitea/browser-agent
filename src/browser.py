from __future__ import annotations

import asyncio
import base64
from pathlib import Path

from playwright.async_api import async_playwright, Browser, Page

VIEWPORT = {"width": 1280, "height": 900}
SCREENSHOTS_DIR = Path("screenshots")


class BrowserSession:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self._playwright = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        SCREENSHOTS_DIR.mkdir(exist_ok=True)
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        context = await self._browser.new_context(viewport=VIEWPORT)
        self._page = await context.new_page()

    async def stop(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    @property
    def page(self) -> Page:
        assert self._page is not None, "Browser not started"
        return self._page

    async def screenshot(self) -> str:
        raw = await self.page.screenshot(type="jpeg", quality=75)
        return base64.b64encode(raw).decode()

    async def navigate(self, url: str) -> str:
        await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
        return f"Navigated to {self.page.url}"

    async def click(self, x: int, y: int) -> str:
        await self.page.mouse.click(x, y)
        await asyncio.sleep(0.3)
        return f"Clicked at ({x}, {y})"

    async def type_text(self, text: str, press_enter: bool = False) -> str:
        await self.page.keyboard.type(text, delay=30)
        if press_enter:
            await self.page.keyboard.press("Enter")
        return f"Typed: {text!r}" + (" + Enter" if press_enter else "")

    async def press_key(self, key: str) -> str:
        await self.page.keyboard.press(key)
        return f"Pressed: {key}"

    async def scroll(self, direction: str, amount: int = 500) -> str:
        delta = -amount if direction == "up" else amount
        await self.page.mouse.wheel(0, delta)
        await asyncio.sleep(0.3)
        return f"Scrolled {direction} by {amount}px"

    async def wait(self, seconds: float) -> str:
        seconds = min(seconds, 10)
        await asyncio.sleep(seconds)
        return f"Waited {seconds}s"
