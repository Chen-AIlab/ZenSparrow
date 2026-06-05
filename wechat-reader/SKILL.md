---
name: wechat-reader
description: |
  读取微信聊天记录（RPA 自动化）。
  当用户要求查看微信消息、读取聊天记录、看看XX发了什么时使用此 skill。
  触发词：读取微信、查看XX消息、XX发了什么、看微信聊天记录。
agent_created: true
---

# WeChat Reader

通过 WeChat Mac 桌面客户端，使用 RPA 截图方式读取指定联系人或群聊的最近消息。

## 核心原则

每次操作从零开始完整流程：激活微信 → 搜索 → 打开聊天 → 截图 → 返回。

**绝不假设微信窗口状态。** 与 sender 一样，每次必须走完整原子流程。

## 交互流程

### 截图模式（默认）

打开指定联系人的聊天窗口，全屏截图保存。

```bash
/Users/ailab/.workbuddy/binaries/python/envs/wechat-rpa/bin/python \
  {skill_dir}/scripts/read_wechat_msg.py "<联系人名称>"
```

流程：
1. 强制激活微信到前台（System Events `set frontmost`），等待 **1.5 秒**
2. Cmd+F 连发 3 次（间隔 0.5 秒），确保 Electron 接收
3. 联系人名称自动转拼音，粘贴到搜索框 → 回车打开聊天
4. 使用 `screencapture` 系统命令全屏截图（避免 pyautogui sandbox 限制）
5. 截图保存到 `{skill_dir}/screenshots/`

### OCR 模式（需安装 tesseract）

在截图基础上自动识别文字：

```bash
/Users/ailab/.workbuddy/binaries/python/envs/wechat-rpa/bin/python \
  {skill_dir}/scripts/read_wechat_msg.py --ocr "<联系人名称>"
```

**前置依赖**：
```bash
brew install tesseract tesseract-lang
/Users/ailab/.workbuddy/binaries/python/envs/wechat-rpa/bin/pip install pytesseract
```

## 能力与边界

| ✅ 可以 | ❌ 不能 |
|--------|--------|
| 截取当前聊天窗口全屏 | 自动滚动历史消息 |
| OCR 识别可见文字 | 读取图片/语音/视频内容 |
| 单次读取一个聊天 | 批量读取多个聊天 |
| macOS 版 | Windows 版（待适配） |
| 含日志记录（JSONL） | — |

## 日志

**位置**：`{skill_dir}/read_log.jsonl`

每行为一条 JSON 记录：
```json
{
  "contact": "联系人名称",
  "screenshot": "screenshots/wechat_xxx_20260603_171633.png",
  "timestamp": "2026-06-03T17:16:33"
}
```

## 注意事项

- WeChat Mac 必须保持登录状态
- 截图使用系统 `screencapture` 命令（无 sandbox 问题）
- OCR 功能需额外安装 tesseract
- 读取期间键盘和鼠标会被短暂占用，请勿操作
- 联系人名称需与微信中显示名称一致
