"""页面导航、滚动、等待策略。"""

from __future__ import annotations

import asyncio
import random
from typing import Optional

from playwright.async_api import Page


async def safe_goto(
    page: Page,
    url: str,
    wait_selector: Optional[str] = None,
    wait_timeout: int = 10000,
    max_retries: int = 2,
    post_load_sleep: float = 3.0,
) -> bool:
    """安全导航到 URL，带重试和动态内容等待。

    策略：domcontentloaded → 等待骨架屏替换 → 等待内容选择器（可选）。

    Args:
        page: Playwright Page。
        url: 目标 URL。
        wait_selector: 等待出现的选择器，用于确认内容加载完成。
        wait_timeout: 选择器等待超时（ms）。
        max_retries: 最大重试次数。
        post_load_sleep: domcontentloaded 后等待秒数（等待骨架屏替换）。

    Returns:
        成功与否。
    """
    for attempt in range(max_retries):
        try:
            await page.goto(url, wait_until="domcontentloaded")
            await asyncio.sleep(post_load_sleep)
            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=wait_timeout)
                except Exception:
                    pass  # best-effort
            return True
        except Exception:
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
    return False


async def human_scroll(
    page: Page,
    times: int = 3,
    min_delta: int = 300,
    max_delta: int = 800,
    min_delay: float = 0.3,
    max_delay: float = 0.8,
) -> None:
    """人为滚动页面，随机幅度和间隔。

    使用 window.scrollBy 而非 mouse.wheel，避免复杂 SPA 页面崩溃。
    """
    for _ in range(random.randint(max(1, times - 1), times + 1)):
        try:
            delta = random.randint(min_delta, max_delta)
            await page.evaluate(f"window.scrollBy(0, {delta})")
            await asyncio.sleep(random.uniform(min_delay, max_delay))
        except Exception:
            pass
