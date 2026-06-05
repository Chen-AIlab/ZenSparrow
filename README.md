# WorkBuddy × WeChat RPA 技能包

通过 RPA（Robotic Process Automation）模拟键盘鼠标操作，让 WorkBuddy AI 助手自动发送微信消息和文件。

> ⚠️ **安全声明**：本项目不含任何聊天记录、日志、截图或凭据。所有敏感数据均通过 `.gitignore` 排除。

## 项目结构

```
├── wechat-sender-mac/     # macOS 版微信发送 Skill
│   ├── SKILL.md           # Skill 使用文档
│   └── scripts/
│       └── send_wechat_msg.py   # 核心 RPA 脚本
├── wechat-sender-win/     # Windows 版微信发送 Skill
│   ├── SKILL.md
│   └── scripts/
│       └── send_wechat_msg.py
├── wechat-sender_介绍.md  # 功能介绍文档
├── .gitignore             # 安全排除规则
└── README.md
```

## 两个 Skill 速览

### wechat-sender-mac（macOS 发送）

通过微信 Mac 桌面端发送文本消息和文件。

- **文本发送**：自动激活微信 → 搜索联系人 → 粘贴消息 → 发送
- **文件发送**：Finder 复制文件 → 粘贴到微信聊天框 → 发送
- **签名支持**：默认添加 `—— workbuddy使用mac发送` 标识
- **日志 & 截图**：自动记录发送日志和确认截图

**核心特性**：
- 联系人中文名自动转拼音搜索，避免 WorkBuddy 联网搜索误判
- Cmd+F 连发 3 次，适配微信 Mac 的 Electron 窗口
- 使用 System Events `set frontmost` 可靠激活

### wechat-sender-win（Windows 发送）

Windows 版的微信发送 Skill，适配 Windows 微信客户端。

- 使用 `pygetwindow` + `win.activate()` 激活窗口
- `Ctrl+F` 搜索，`Ctrl` 替代 `Cmd` 系列快捷键
- 默认签名：`—— workbuddy使用win发送`
- ⚠️ 未在 Windows 环境实测，欢迎反馈

## 安装与使用

### 前置条件

1. 微信桌面客户端已登录
2. **macOS**：辅助功能权限已授权（系统设置 > 隐私与安全性 > 辅助功能）
3. Python 3.9+

### 安装依赖

```bash
# macOS
pip install pyautogui pyperclip pypinyin Pillow python-docx

# Windows（额外依赖）
pip install pyautogui pyperclip pypinyin Pillow python-docx pygetwindow
```

### 安装到 WorkBuddy

```bash
# 将 Skill 目录复制到 WorkBuddy skills 目录
cp -r wechat-sender-mac ~/.workbuddy/skills/
cp -r wechat-sender-win ~/.workbuddy/skills/
```

### 使用示例

在 WorkBuddy 中直接对话即可触发：

- "给 Fred 发微信：会议改到下午 3 点"
- "把这个文件发到微信文件传输助手"
- "通知龙虾作战室群：今晚聚餐取消"

## 技术原理

| 组件 | macOS | Windows |
|------|-------|---------|
| 窗口激活 | System Events `set frontmost` | `pygetwindow.activate()` |
| 搜索快捷键 | Cmd+F ×3 | Ctrl+F ×2 |
| 按键模拟 | `pyautogui` | `pyautogui` |
| 剪贴板 | `pyperclip` | `pyperclip` |
| 拼音转换 | `pypinyin` | `pypinyin` |
| 截图确认 | `screencapture` | `pyautogui.screenshot()` |

## 能力与边界

| ✅ 能做 | ❌ 不能做 |
|--------|----------|
| 发送文本消息到联系人/群聊 | 发送图片、语音、视频 |
| 发送本地文件 | 批量群发 |
| 自动添加签名区分来源 | 读取聊天记录（reader 开发中） |
| macOS + Windows 双平台 | — |

## 安全与隐私

- **不上传敏感数据**：日志、截图、聊天记录均通过 `.gitignore` 排除
- **本地运行**：所有操作在本地完成，不经过第三方服务器
- **签名区分**：自动添加 `workbuddy` 签名，方便接收方识别
- **建议**：使用前检查脚本内容，确认无意外操作

## License

MIT
