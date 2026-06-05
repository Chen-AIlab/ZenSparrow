"""DOM 提取工具：fallback 选择器链、CDP 深层序列化解包、console 劫持。"""

from __future__ import annotations

from typing import Any, Optional

from playwright.async_api import Page


async def extract_with_fallbacks(
    page: Page,
    selectors: list[str],
    attribute: Optional[str] = None,
) -> Optional[str]:
    """按优先级遍历选择器列表，返回第一个非空结果。

    Args:
        page: Playwright Page。
        selectors: 选择器列表，按优先级从高到低。
        attribute: 提取属性名（如 "content", "href"），默认提取 text_content。

    Returns:
        第一个匹配到的文本，或 None。
    """
    for sel in selectors:
        try:
            el = await page.query_selector(sel)
            if not el:
                continue
            value = await el.get_attribute(attribute) if attribute else await el.text_content()
            if value and value.strip():
                return value.strip()
        except Exception:
            continue
    return None


async def extract_all_with_fallbacks(
    page: Page,
    selectors: list[str],
    attribute: Optional[str] = None,
) -> list[str]:
    """遍历选择器列表，返回所有命中的结果（去重）。

    Args:
        page: Playwright Page。
        selectors: 选择器列表。
        attribute: 提取属性名。

    Returns:
        去重后的文本列表。
    """
    seen: set[str] = set()
    results: list[str] = []
    for sel in selectors:
        try:
            for el in await page.query_selector_all(sel):
                value = await el.get_attribute(attribute) if attribute else await el.text_content()
                if value and value.strip() and value.strip() not in seen:
                    seen.add(value.strip())
                    results.append(value.strip())
        except Exception:
            continue
    return results


def deep_to_python(value: Any) -> Any:
    """将 CDP Runtime.evaluate 的深层序列化值转为普通 Python 对象。

    CDP 有时将 JS 对象返回为 [[key, val], ...] 嵌套数组格式，
    或 {"type": "object", "value": ...} 包装格式。此函数递归解包。
    """
    if isinstance(value, list):
        if value and isinstance(value[0], list) and len(value[0]) == 2 and isinstance(value[0][0], str):
            return {k: deep_to_python(v) for k, v in value}
        return [deep_to_python(x) for x in value]
    if isinstance(value, dict):
        return deep_to_python(value.get("value", value)) if "type" in value else value
    return value


async def inject_console_hook(page: Page) -> None:
    """劫持 console.error/warn，收集页面 JS 报错。

    在页面脚本执行前注入效果最好。注入后可通过 page.evaluate 读取
    window.__ce（errors）和 window.__cw（warns）数组。

    重复调用无害——内部用 __consoleHooked 标志防止双重劫持。
    """
    await page.evaluate("""
        if (!window.__consoleHooked) {
            window.__consoleHooked = true;
            window.__ce = [];
            window.__cw = [];
            const _e = console.error;
            const _w = console.warn;
            console.error = function() {
                window.__ce.push(Array.from(arguments).join(' '));
                _e.apply(console, arguments);
            };
            console.warn = function() {
                window.__cw.push(Array.from(arguments).join(' '));
                _w.apply(console, arguments);
            };
        }
    """)
