#!/usr/bin/env python3
"""
WeChat RPA for Windows — 通过 WeChat Windows 桌面客户端发送消息（含日志和截图确认）。

依赖：pyautogui, pyperclip, pygetwindow, Pillow, pypinyin
Python 环境：需安装以下依赖
    pip install pyautogui pyperclip pygetwindow Pillow pypinyin python-docx

前置条件：
  1. WeChat Windows 必须已登录且正在运行
  2. 目标联系人/群聊必须存在于微信中
  3. 微信窗口不能被最小化

用法：
  python send_wechat_msg.py <联系人名称> <消息内容>

每次调用都是完整原子流程，不受当前窗口状态影响。
"""

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import pyautogui
import pygetwindow as gw
import pyperclip
from pypinyin import pinyin, Style

# ── 路径配置 ──────────────────────────────────────────────

SKILL_DIR = Path.home() / ".workbuddy" / "skills" / "wechat-sender-win"
LOG_FILE = SKILL_DIR / "logs" / "send_log.jsonl"
SCREENSHOT_DIR = SKILL_DIR / "logs" / "screenshots"


def ensure_dirs() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


# ── 日志 ──────────────────────────────────────────────────

def write_log(contact: str, message: str, msg_type: str = "text",
              result: str = "OK", screenshot: str = "") -> None:
    ensure_dirs()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "contact": contact,
        "message": message[:200],
        "type": msg_type,
        "result": result,
        "screenshot": screenshot,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── 拼音转换 ──────────────────────────────────────────────

def to_pinyin(text: str) -> str:
    """将中文转为拼音（小写、无空格），用于微信搜索。非中文直接返回。"""
    if not re.search(r'[\u4e00-\u9fff]', text):
        return text
    parts = pinyin(text, style=Style.NORMAL, errors=lambda x: [x])
    return "".join(p[0] for p in parts)


# ── 核心函数 ──────────────────────────────────────────────

def activate_wechat() -> None:
    """
    强制将微信窗口拉到前台。
    Windows 上使用 pygetwindow 查找并激活微信窗口。
    """
    wechat_wins = gw.getWindowsWithTitle('微信')
    if wechat_wins:
        win = wechat_wins[0]
        if win.isMinimized:
            win.restore()
        win.activate()
    time.sleep(0.8)


def open_search() -> None:
    """Ctrl+F 打开搜索框，连发 2 次确保接收。"""
    for _ in range(2):
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.3)


def capture_confirmation(contact: str) -> str:
    """
    截图确认发送结果。Windows 上 pyautogui.screenshot 直接可用。
    """
    ensure_dirs()
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{contact}.png"
        filepath = SCREENSHOT_DIR / filename
        img = pyautogui.screenshot()
        img.save(str(filepath))
        return str(filepath)
    except Exception:
        return ""


def send_wechat(contact_name: str, message: str, with_confirm: bool = True,
                msg_type: str = "text") -> str:
    """
    向微信联系人或群聊发送消息。Windows 版本。

    完整原子流程:
      1. pygetwindow 激活微信窗口
      2. Ctrl+F × 2 打开搜索框
      3. 中文名自动转拼音 → 粘贴搜索 → 回车选中聊天
      4. Ctrl+V 粘贴消息 → 回车发送
      5. 截图确认 + 写入日志
    """

    ensure_dirs()

    # 检查微信是否运行
    wechat_wins = gw.getWindowsWithTitle('微信')
    if not wechat_wins:
        err = "WeChat 未运行，请先打开 WeChat Windows。"
        write_log(contact_name, message, msg_type, err)
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    # 1. 激活微信
    activate_wechat()

    # 2. 打开搜索框
    open_search()

    # 3. 转拼音 + 搜索
    search_name = to_pinyin(contact_name)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyperclip.copy(search_name)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.6)

    # 4. 回车选中
    pyautogui.press("enter")
    time.sleep(0.6)

    # 5. 粘贴消息 → 发送
    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(0.3)

    # 6. 截图确认
    screenshot_path = ""
    if with_confirm:
        screenshot_path = capture_confirmation(contact_name)

    write_log(contact_name, message, msg_type,
              f"OK{'+confirmed' if screenshot_path else ''}",
              screenshot_path)

    print("OK")
    return "OK"


# ── CLI ──────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="WeChat RPA 发送器 (Windows)")
    parser.add_argument("contact", help="联系人名称")
    parser.add_argument("message", help="消息内容")
    parser.add_argument("--no-confirm", action="store_true", help="跳过截图确认")
    parser.add_argument("--file", action="store_true", help="标记为文件发送")
    args = parser.parse_args()

    msg_type = "file" if args.file else "text"
    send_wechat(args.contact, args.message,
                with_confirm=not args.no_confirm,
                msg_type=msg_type)


if __name__ == "__main__":
    main()
