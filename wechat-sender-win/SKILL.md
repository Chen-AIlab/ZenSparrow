---
name: wechat-sender-win
description: |
  通过 WeChat Windows 桌面客户端发送微信消息（RPA 自动化）。
  触发词：给XX发微信、发消息给XX、微信发送、发到微信、用微信通知、
  找到XX群、搜XX微信、找XX聊天、给XX说、通知XX。
  联系人中文名自动转拼音搜索，避免被 WorkBuddy 误判为联网搜索。
agent_created: true
---

# WeChat Sender (Windows)

通过 WeChat Windows 桌面客户端，使用 RPA 模拟键盘和鼠标操作来发送微信消息。

## 核心原则（最高优先级）

**绝不假设微信窗口状态。** 每轮对话都可能发生窗口切换，每次与微信交互都必须从零开始执行完整流程：激活微信 → 搜索 → 选中 → 操作 → 发送。

**拼音搜索规则。** 联系人名称包含中文时，自动转为拼音再搜索（例如"组长群"→"zuzhangqun"），避免 WorkBuddy 将中文名误判为联网搜索。

## 安装

```bash
pip install pyautogui pyperclip pygetwindow Pillow pypinyin python-docx
```

把 skill 文件夹放到 `~/.workbuddy/skills/wechat-sender-win/`。

## 交互流程

### 1. 收集信息
- **收件人**：微信联系人或群聊的显示名称
- **消息内容**：要发送的文本

### 2. 建议添加签名
发送文本消息前，建议在消息末尾添加签名：
> `—— workbuddy使用win发送`

### 3. 发送文本消息

```bash
python {skill_dir}/scripts/send_wechat_msg.py "<联系人名称>" "<消息内容>"
```

流程：
1. `pygetwindow` 激活微信窗口，等待 0.8 秒
2. Ctrl+F **连发 2 次** 打开搜索框
3. 中文名转拼音 → Ctrl+V 粘贴搜索 → 回车选中聊天
4. Ctrl+V 粘贴消息 → 回车发送
5. 截图确认 + 日志记录

### 4. 发送文件

打开聊天后：
1. 鼠标点击输入区域确保焦点
2. 文件管理器选中文件 → Ctrl+C 复制
3. 切回微信 → Ctrl+V 粘贴 → 回车发送

## 确认与日志

- **日志**：`{skill_dir}/logs/send_log.jsonl`
- **截图**：`{skill_dir}/logs/screenshots/`
- `OK+confirmed`：发送成功 + 截图确认
- `OK`：发送成功但截图未生成

## 注意事项

- WeChat Windows 窗口标题必须为「微信」
- 窗口不能被最小化
- 与 macOS 版的核心区别：Ctrl 替代 Cmd，pygetwindow 替代 AppleScript
