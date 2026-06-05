"""浏览器启动、反检测注入、UA 轮转。"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, BrowserContext

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
]

VIEWPORT = {"width": 1920, "height": 1080}

ANTI_DETECTION_BOOT_SCRIPT = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'plugins', {
    get: () => [
        {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
        {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
        {name: 'Native Client', filename: 'internal-nacl-plugin'},
    ]
});
Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
window.chrome = { runtime: {} };
Object.defineProperty(window, 'Notification', {
    get: () => ({ permission: 'default' })
});
const _originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications'
        ? Promise.resolve({ state: 'prompt' })
        : _originalQuery(parameters)
);
"""


def get_random_ua() -> str:
    return random.choice(USER_AGENTS)


async def launch_browser(
    headless: bool = False,
    cdp_url: Optional[str] = None,
    profile_dir: Optional[Path] = None,
) -> tuple[Browser, BrowserContext]:
    """启动浏览器并注入反检测脚本。

    Args:
        headless: 是否无头模式。对反爬严格的站点设为 False。
        cdp_url: CDP 连接地址，如 "http://localhost:9222"。优先使用。
        profile_dir: Chrome 用户数据目录路径。

    Returns:
        (browser, context) 元组。
    """
    pw = await async_playwright().start()

    if cdp_url:
        browser = await pw.chromium.connect_over_cdp(cdp_url)
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context(viewport=VIEWPORT)
        # CDP 模式下不注入 boot script（真实 Chrome 不需要）
        return browser, context

    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-extensions",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
    ]

    browser = await pw.chromium.launch(headless=headless, args=launch_args)

    context = await browser.new_context(
        viewport=VIEWPORT,
        user_agent=get_random_ua(),
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
        permissions=["geolocation"],
        java_script_enabled=True,
        bypass_csp=True,
    )
    await context.add_init_script(ANTI_DETECTION_BOOT_SCRIPT)

    return browser, context


async def close_browser(browser: Browser) -> None:
    """安全关闭浏览器。已关闭的情况下不抛异常。"""
    try:
        await browser.close()
    except Exception:
        pass
