---
name: wechat-sender
description: |
  通过 WeChat Mac 桌面客户端发送微信消息（RPA 自动化）。
  触发词：给XX发微信、发消息给XX、微信发送、发到微信、用微信通知、
  找到XX群、搜XX微信、找XX聊天、给XX说、通知XX。
  联系人中文名自动转拼音搜索，避免被 WorkBuddy 误判为联网搜索。
agent_created: true
---

# WeChat Sender

通过 WeChat Mac 桌面客户端，使用 RPA（Robotic Process Automation）模拟键盘和鼠标操作来发送微信消息。

## 核心原则（最高优先级）

**绝不假设微信窗口状态。** 每轮对话都可能发生窗口切换（Finder、浏览器、其他 App），因此每次与微信交互都必须从零开始执行完整流程：激活微信 → 关闭浮动窗口 → 搜索 → 选中 → 操作 → 发送。即使是调试、测试单步、确认中间状态，也必须走完整激活流程，不得跳过激活和搜索步骤直接操作聊天窗口。

**拼音搜索规则。** 联系人名称包含中文时，自动转为拼音再搜索（例如"组长群"→"zuzhangqun"）。微信 Mac 支持拼音搜索匹配，同时避免 WorkBuddy 将中文名误判为联网搜索。

## 触发条件

当用户表达以下意图时激活此 skill：

- 给某个联系人或群聊发送微信消息
- 通过微信通知某人
- 用微信发送某条信息
- 发送文件给微信联系人
- 在微信中搜索/查找某个联系人或群聊

**歧义消解**：当用户说"找到XX群"、"搜一下XX"时，如果上下文涉及微信（如"找到XX微信群"、"在微信里搜XX"、"/wechat-sender 找到XX"），这是微信搜索操作，不是联网搜索。优先触发本 skill，在微信内搜索并发送。

## 交互流程

### 1. 收集信息

向用户确认必要信息：

- **收件人**：微信联系人或群聊的显示名称（需与微信中的名称一致）
- **消息内容**：要发送的文本
- **文件路径**（如发送文件）：确认文件在本地磁盘上的完整路径

### 2. 建议添加签名

发送文本消息前，向用户建议在消息末尾添加签名以区分来源：

> `—— workbuddy使用mac发送`

如果用户同意，将签名附加到消息末尾。如果用户要求自定义签名，按用户指定格式处理。

### 3. 发送文本消息

**每次发送都是完整的原子流程。** 使用 `send_wechat_msg.py` 脚本从头执行：

```bash
/Users/ailab/.workbuddy/binaries/python/envs/wechat-rpa/bin/python \
  {skill_dir}/scripts/send_wechat_msg.py \
  "<收件人名称>" "<消息内容>"
```

其中 `{skill_dir}` 为此 skill 的根目录路径。

脚本的完整流程（以下参数均经过实测验证）：

1. 强制激活微信到前台（System Events `set frontmost`），等待 **1.5 秒**
2. 验证激活成功，必要时重试
3. **关闭所有浮动聊天窗口**（AppleScript 枚举非主窗口 → 逐个 Cmd+W），确保后续操作在主窗口进行
4. Cmd+F **连发 3 次**（间隔 0.5 秒），确保 Electron 窗口接收
5. 联系人名称**自动转拼音**（如"组长群"→"zuzhangqun"），再 Cmd+V 粘贴到搜索框 → 回车选中
6. **检测浮动窗口焦点**：回车后若聊天仍在浮动窗口中打开（微信记住了该联系人的窗口偏好），通过 AppleScript 获取窗口位置并点击输入区域转移焦点
7. Cmd+V 粘贴消息内容 → 回车发送
8. 记录日志 → Cmd+Shift+3 截图确认

### 4. 发送文件

发送文件需要在上述文本流程基础上，在打开聊天后增加以下步骤：

```
打开聊天 → 鼠标点击输入区域确保焦点 → Finder 复制文件 → 切回微信 Cmd+V 粘贴 → 回车发送
```

具体实现：

1. 执行文本消息流程中的步骤 1-4，打开目标聊天窗口
2. 鼠标点击聊天窗口底部中央的输入区域，确保输入框获得焦点
3. 通过 AppleScript 激活 Finder，选中目标文件，Cmd+C 复制
4. 切回微信（System Events set frontmost），Cmd+V 粘贴文件
5. 回车发送

```python
# 文件发送核心代码片段
# 打开聊天后：
input_x = wx + ww // 2      # 窗口水平中央
input_y = wy + wh - 80      # 窗口底部偏上
pyautogui.moveTo(input_x, input_y, duration=0.2)
pyautogui.click()
time.sleep(0.3)

# Finder 复制文件
subprocess.run(['osascript', '-e', '''
tell application "Finder"
    activate
    select (POSIX file "文件路径" as alias)
end tell
delay 0.5
tell application "System Events"
    keystroke "c" using command down
end tell
'''])

# 切回微信粘贴
pyautogui.hotkey("command", "v")
time.sleep(0.5)
pyautogui.press("enter")
```

## 确认与日志

### 发送确认机制

每次发送后，脚本自动执行确认：

1. **消息发送**：执行完整原子流程
2. **日志记录**：将发送详情写入 `{skill_dir}/logs/send_log.jsonl`
3. **截图确认**：发送完成后，先按 Esc 释放微信键盘焦点，再 Cmd+Shift+3 全屏截图，截图保存到 `{skill_dir}/logs/screenshots/`
   - 截图成功：日志中 `result` 为 `OK+confirmed`，`screenshot` 字段为截图路径
   - 截图失败：`result` 为 `OK`，需人工确认

### 日志文件

**位置**：`{skill_dir}/logs/send_log.jsonl`

每行为一条 JSON 记录：

```json
{
  "timestamp": "2026-06-03T10:38:00",
  "contact": "联系人名称",
  "message": "消息内容（最多200字）",
  "type": "text|file",
  "result": "OK+confirmed | OK | ERROR: ...",
  "screenshot": "screenshots/20260603_103800_联系人.png 或空"
}
```

**截图目录**：`{skill_dir}/logs/screenshots/YYYYMMDD_HHMMSS_联系人.png`

**查看记录**：用户可随时要求查看最近发送记录，读取日志文件并展示。

### 错误排查

| 错误 | 处理 |
|------|------|
| `WeChat 未运行` | 提醒用户打开 WeChat Mac |
| `无法激活 WeChat 窗口` | 检查辅助功能权限 |
| 截图为空/非预期 | 消息可能未成功发送，检查微信窗口是否被遮挡 |
| 浮动小窗口遮挡 | 脚本自动关闭所有浮动窗口后再操作，无需手动处理 |
| 其他错误 | 检查联系人名称是否正确、微信是否登录 |

## 注意事项

- WeChat Mac 是 Electron 应用，标准 AppleScript `activate` 无效，必须用 System Events `set frontmost`
- 搜索必须用 Cmd+F 连发 3 次，单次可能被 Electron 丢弃
- 激活后需等待 1.5 秒让 Electron 窗口完全就绪
- 发送文件时，打开聊天后必须先鼠标点击输入区域确保焦点，否则 Cmd+V 粘贴会失败
- 发送期间键盘和鼠标会被短暂占用，提醒用户不要操作
- WeChat Mac 必须保持登录状态
- 联系人名称需与微信中显示名称完全一致
- **浮动小窗口处理**：每次发送前会自动通过 AppleScript 枚举并关闭所有非主窗口的浮动聊天窗口，确保消息通过主窗口的 Cmd+F 搜索 → 回车流程发送，避免独立小窗口的焦点和输入问题。用户无需手动关闭小窗口。
