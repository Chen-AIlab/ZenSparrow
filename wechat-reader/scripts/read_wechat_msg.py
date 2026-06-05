#!/usr/bin/env python3
"""
WeChat Reader for macOS — 读取微信聊天记录（基础版：截图）。

依赖：pyautogui, pyperclip, pypinyin, Pillow
Python 环境：/Users/ailab/.workbuddy/binaries/python/envs/wechat-rpa/bin/python

用法：
  python read_wechat_msg.py <联系人名称>
  python read_wechat_msg.py --ocr <联系人名称>  # 需要先安装tesseract
"""

import argparse
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

SKILL_DIR = Path.home() / ".workbuddy" / "skills" / "wechat-reader"
LOG_FILE = SKILL_DIR / "read_log.jsonl"
SCREENSHOT_DIR = SKILL_DIR / "screenshots"


def to_pinyin(text: str) -> str:
    if not re.search(r'[\u4e00-\u9fff]', text):
        return text
    parts = pinyin(text, style=Style.NORMAL, errors=lambda x: [x])
    return "".join(p[0] for p in parts)


def activate_wechat() -> bool:
    """激活微信到前台"""
    subprocess.run(["osascript", "-e",
        'tell application "System Events" to set frontmost of first process whose name is "WeChat" to true'],
        capture_output=True, timeout=5)
    time.sleep(1.5)
    
    v = subprocess.run(["osascript", "-e",
        'tell application "System Events" to get name of first application process whose frontmost is true'],
        capture_output=True, text=True, timeout=5)
    return "WeChat" in v.stdout


def open_search() -> None:
    """打开搜索框（Cmd+F 连发3次）"""
    for _ in range(3):
        pyautogui.hotkey("command", "f")
        time.sleep(0.5)


def take_screenshot(contact_name: str) -> Path:
    """使用 screencapture 截图并保存到 skill 的 screenshots 目录"""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c for c in contact_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    screenshot_path = SCREENSHOT_DIR / f"wechat_{safe_name}_{timestamp}.png"
    
    # 使用系统截图命令（全屏）
    subprocess.run([
        "screencapture", "-x",  # -x 禁止声音
        str(screenshot_path)
    ], timeout=5)
    
    time.sleep(0.5)
    
    if screenshot_path.exists():
        print(f"截图已保存: {screenshot_path}", file=sys.stderr)
        return screenshot_path
    else:
        raise FileNotFoundError("截图失败")


def ocr_image(image_path: Path) -> str:
    """使用 tesseract OCR 识别图片中的文字"""
    try:
        import pytesseract
        from PIL import Image
        
        img = Image.open(image_path)
        # 使用中文简体+英文
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        return text.strip()
    except ImportError:
        print("ERROR: 未安装 pytesseract", file=sys.stderr)
        print("  请运行: pip install pytesseract Pillow", file=sys.stderr)
        print("  以及: brew install tesseract tesseract-lang", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"WARNING: OCR 识别失败: {e}", file=sys.stderr)
        return ""


def read_wechat(contact_name: str, use_ocr: bool = False) -> dict:
    """
    读取指定联系人的聊天。
    返回包含截图路径（和OCR文本）的字典。
    """
    
    if not subprocess.run(["pgrep", "-x", "WeChat"], capture_output=True).returncode == 0:
        print("ERROR: WeChat 未运行", file=sys.stderr)
        sys.exit(1)
    
    # 1. 激活微信
    print("正在激活微信...", file=sys.stderr)
    if not activate_wechat():
        print("ERROR: 无法激活 WeChat 窗口", file=sys.stderr)
        sys.exit(1)
    
    # 2. 搜索联系人
    print(f"正在搜索联系人: {contact_name}...", file=sys.stderr)
    open_search()
    pyautogui.hotkey("command", "a")
    time.sleep(0.15)
    pyperclip.copy(to_pinyin(contact_name))
    pyautogui.hotkey("command", "v")
    time.sleep(0.6)
    
    # 3. 回车打开聊天
    pyautogui.press("enter")
    time.sleep(1.0)
    
    # 4. 截图
    print("正在截图...", file=sys.stderr)
    screenshot_path = take_screenshot(contact_name)
    
    result = {
        "contact": contact_name,
        "screenshot": str(screenshot_path),
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    
    # 5. （可选）OCR 识别
    if use_ocr:
        print("正在 OCR 识别...", file=sys.stderr)
        ocr_text = ocr_image(screenshot_path)
        result["ocr_text"] = ocr_text
        print(ocr_text)
    
    return result


def log_result(result: dict) -> None:
    """写入读取日志"""
    SKILL_DIR.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description='读取微信聊天记录')
    parser.add_argument('--ocr', action='store_true', help='使用 OCR 识别文字（需要安装 tesseract）')
    parser.add_argument('contact_name', help='联系人名称')
    
    args = parser.parse_args()
    
    result = read_wechat(args.contact_name, use_ocr=args.ocr)
    log_result(result)
    
    if not args.ocr:
        print(f"截图已保存: {result['screenshot']}")
        print("如需 OCR 识别，请使用 --ocr 参数（需要先安装 tesseract）")


if __name__ == "__main__":
    main()
