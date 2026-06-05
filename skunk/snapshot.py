"""失败现场保存：HTML 快照、截图。"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from playwright.async_api import Page


def _make_filename(url: str, label: str, ext: str) -> str:
    """从 URL 和标签生成安全的文件名。"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_label = "".join(c if c.isalnum() or c in "_-" else "_" for c in label)
    safe_url = "".join(c if c.isalnum() else "_" for c in url[:80])
    return f"{ts}_{safe_label}_{safe_url}.{ext}"


async def save_html_snapshot(
    page: Page, output_dir: Path, url: str = "", label: str = "snapshot"
) -> Path:
    """保存当前页面 HTML 到文件，用于离线调试选择器失败。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    html = await page.content()
    fname = _make_filename(url or page.url, label, "html")
    path = output_dir / fname
    path.write_text(html, encoding="utf-8")
    return path


async def save_screenshot(
    page: Page, output_dir: Path, url: str = "", label: str = "screenshot", full_page: bool = True
) -> Path:
    """截取当前页面并保存为 PNG。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    fname = _make_filename(url or page.url, label, "png")
    path = output_dir / fname
    await page.screenshot(path=str(path), full_page=full_page)
    return path
