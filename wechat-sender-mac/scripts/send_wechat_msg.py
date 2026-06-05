#!/usr/bin/env python3
"""
WeChat RPA for macOS — 通过 WeChat Mac 桌面客户端发送消息（含日志和确认）。

依赖：pyautogui, pyperclip
Python 环境：/Users/ailab/.workbuddy/binaries/python/envs/wechat-rpa/bin/python

前置条件：
  1. WeChat Mac 必须已在运行（后台即可）
  2. 系统设置 → 隐私与安全性 → 辅助功能 → 已授权运行环境
  3. 目标联系人/群聊必须存在于微信中

用法：
  python send_wechat_msg.py <联系人名称> <消息内容>

每次调用都是完整原子流程，不受当前窗口状态影响。
发送后自动记录日志并截图确认。
"""

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import pyautogui
import pyperclip
from pypinyin import pinyin, Style

# ── 路径配置 ──────────────────────────────────────────────

SKILL_DIR = Path.home() / ".workbuddy" / "skills" / "wechat-sender"
LOG_FILE = SKILL_DIR / "logs" / "send_log.jsonl"
SCREENSHOT_DIR = SKILL_DIR / "logs" / "screenshots"


def ensure_dirs() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


# ── 日志 ──────────────────────────────────────────────────

def write_log(contact: str, message: str, msg_type: str = "text",
              result: str = "OK", screenshot: str = "") -> None:
    """追加一条发送记录到日志文件。"""
    ensure_dirs()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "contact": contact,
        "message": message[:200],  # 截断过长消息
        "type": msg_type,
        "result": result,
        "screenshot": screenshot,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── 发送确认截图 ──────────────────────────────────────────

def capture_confirmation(contact: str) -> str:
    """
    通过 Cmd+Shift+3 全屏截图来确认发送结果。
    截图自动保存到桌面，随后移动到日志目录。
    返回截图文件路径，失败返回空字符串。
    """
    ensure_dirs()

    try:
        # 记录截图前的桌面文件列表（中英文系统文件名不同）
        desktop = Path.home() / "Desktop"
        before = set(f.name for f in desktop.glob("*.png") if "截屏" in f.name or "Screenshot" in f.name)

        # 释放 WeChat 键盘焦点，确保 Cmd+Shift+3 被系统接收
        time.sleep(0.5)
        pyautogui.press("escape")
        time.sleep(0.3)

        # Cmd+Shift+3 全屏截图（无需 GUI 交互）
        pyautogui.hotkey("command", "shift", "3")
        time.sleep(2.0)

        # 查找新生成的截图文件
        after = set(f.name for f in desktop.glob("*.png") if "截屏" in f.name or "Screenshot" in f.name)
        new_files = after - before

        if new_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{contact}.png"
            dest = SCREENSHOT_DIR / filename

            src = desktop / list(new_files)[0]
            src.rename(dest)
            return str(dest)
    except Exception:
        pass
    return ""


# ── 拼音转换 ──────────────────────────────────────────────

def to_pinyin(text: str) -> str:
    """将中文转为拼音（小写、无空格），用于微信搜索。非中文直接返回。"""
    if not re.search(r'[\u4e00-\u9fff]', text):
        return text
    parts = pinyin(text, style=Style.NORMAL, errors=lambda x: [x])
    return "".join(p[0] for p in parts)


# ── 核心函数 ──────────────────────────────────────────────

def is_wechat_running() -> bool:
    result = subprocess.run(
        ["pgrep", "-x", "WeChat"],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def activate_wechat() -> None:
    """
    强制将微信窗口拉到前台。
    WeChat Mac 是 Electron 应用，不能用标准 activate，必须用 System Events。
    等待 1.5 秒确保 Electron 窗口完全就绪。
    """
    script = '''
    tell application "System Events"
        set wechatProcess to first process whose name is "WeChat"
        set frontmost of wechatProcess to true
    end tell
    '''
    subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=5,
    )
    time.sleep(1.5)


def close_floating_windows() -> None:
    """
    关闭微信中所有浮动的独立聊天窗口，只保留主窗口。
    这确保后续操作都在主窗口中进行，避免小窗口焦点问题。

    方法：用 AppleScript 枚举 WeChat 所有窗口标题，
    对非主窗口（标题不是"微信"/"WeChat"）逐次发送 Cmd+W 关闭。
    """
    script = '''
    tell application "System Events"
        tell process "WeChat"
            set output to ""
            repeat with w in every window
                set wTitle to title of w
                if wTitle is not "微信" and wTitle is not "WeChat" then
                    set output to output & wTitle & "|"
                end if
            end repeat
            return output
        end tell
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=5,
    )
    titles_raw = result.stdout.strip()
    if not titles_raw:
        return  # 没有浮动窗口

    floating_titles = [t for t in titles_raw.split("|") if t]
    # 逐个关闭浮动窗口
    for _ in floating_titles:
        pyautogui.hotkey("command", "w")
        time.sleep(0.4)


def open_search() -> None:
    """Cmd+F 打开搜索框，连发 3 次确保 Electron 窗口接收。"""
    for _ in range(3):
        pyautogui.hotkey("command", "f")
        time.sleep(0.5)


def detect_and_focus_chat() -> None:
    """
    搜索回车后，检测聊天是否在浮动窗口中打开。
    如果是，点击浮动窗口输入区域获取焦点，确保后续粘贴操作定位正确。
    """
    script = '''
    tell application "System Events"
        tell process "WeChat"
            repeat with w in every window
                set wTitle to title of w
                if wTitle is not "微信" and wTitle is not "WeChat" and wTitle is not "" then
                    set wPos to position of w
                    set wSize to size of w
                    set x to item 1 of wPos
                    set y to item 2 of wPos
                    set ww to item 1 of wSize
                    set wh to item 2 of wSize
                    return (x as string) & "," & (y as string) & "," & (ww as string) & "," & (wh as string)
                end if
            end repeat
            return "MAIN"
        end tell
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True, text=True, timeout=5,
    )

    output = result.stdout.strip()
    if output == "MAIN":
        return  # 聊天在主窗口内打开，焦点正确，无需处理

    # 浮动窗口：获取位置，点击输入区域（窗口底部中央偏上）转移焦点
    try:
        parts = output.split(",")
        x, y, ww, wh = int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3])
        # 输入框大约在窗口底部往上 60px，水平居中
        input_x = x + ww // 2
        input_y = y + wh - 60
        pyautogui.moveTo(input_x, input_y, duration=0.3)
        pyautogui.click()
        time.sleep(0.4)
    except Exception:
        pass  # 若检测失败，继续尝试粘贴（Keyboard 事件可能仍能到达）


def send_wechat(contact_name: str, message: str, with_confirm: bool = True,
                msg_type: str = "text") -> str:
    """
    向微信联系人或群聊发送消息。返回 result ("OK" 或错误信息)。

    完整原子流程:
      1. 强制激活微信到前台 (System Events set frontmost) + 等待 1.5s
      2. 关闭所有浮动聊天窗口，只保留主窗口
      3. Cmd+F × 3 打开搜索框
      4. Cmd+A 清空 + Cmd+V 粘贴联系人名称 → 回车选中聊天
      5. 检测是否弹出浮动窗口，若是则点击输入区域获取焦点
      6. Cmd+V 粘贴消息内容 → 回车发送
      7. (可选) 截图确认
      8. 写入日志
    """

    ensure_dirs()

    if not is_wechat_running():
        err = "WeChat 未运行，请先打开 WeChat Mac。"
        write_log(contact_name, message, msg_type, err)
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    try:
        activate_wechat()
    except Exception:
        err = "无法激活 WeChat 窗口。"
        write_log(contact_name, message, msg_type, err)
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)

    # 验证前台 + 重试
    for _ in range(2):
        verify = subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to get name of first application process whose frontmost is true'],
            capture_output=True, text=True, timeout=5,
        )
        if "WeChat" in verify.stdout:
            break
        activate_wechat()

    # 关闭所有浮动聊天窗口，确保操作在主窗口进行
    close_floating_windows()
    time.sleep(0.5)

    # 打开搜索框
    open_search()

    # 联系人名称转拼音后再搜索（避免 WorkBuddy 触发联网搜索）
    search_name = to_pinyin(contact_name)

    # 清空已有内容 → 粘贴拼音搜索词
    pyautogui.hotkey("command", "a")
    time.sleep(0.15)
    pyperclip.copy(search_name)
    pyautogui.hotkey("command", "v")
    time.sleep(0.6)

    # 回车选中第一个匹配聊天（微信可能弹出浮动窗口）
    pyautogui.press("enter")
    time.sleep(1.0)  # 等浮动窗口完全就绪

    # 若聊天在浮动窗口中打开，点击获取焦点
    detect_and_focus_chat()

    # 粘贴消息内容 → 回车发送
    pyperclip.copy(message)
    pyautogui.hotkey("command", "v")
    time.sleep(0.2)
    pyautogui.press("enter")
    time.sleep(0.3)

    # 截图确认
    screenshot_path = ""
    if with_confirm:
        screenshot_path = capture_confirmation(contact_name)

    # 写入日志
    write_log(contact_name, message, msg_type,
              f"OK{'+confirmed' if screenshot_path else ''}",
              screenshot_path)

    print("OK")
    return "OK"


# ── CLI ──────────────────────────────────────────────────

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="WeChat RPA 发送器")
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
