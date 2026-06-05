# WorkBuddy × WeChat RPA 技能包

通过 RPA（Robotic Process Automation）模拟键盘鼠标操作，让 WorkBuddy AI 助手能够自动发送和读取微信消息。

> ⚠️ **安全声明**：本项目不含任何聊天记录、日志、截图或凭据。所有敏感数据均通过 `.gitignore` 排除。

## 项目结构

```
├── wechat-sender/         # macOS 版微信发送 Skill
│   ├── SKILL.md           # Skill 使用文档
│   └── scripts/
│       └── send_wechat_msg.py   # 核心 RPA 脚本
├── wechat-sender-win/     # Windows 版微信发送 Skill
│   ├── SKILL.md
│   └── scripts/
│       └── send_wechat_msg.py
├── wechat-reader/         # macOS 版微信读取 Skill
│   ├── SKILL.md
│   └── scripts/
│       └── read_wechat_msg.py   # 截图+OCR 读取脚本
├── wechat-sender_介绍.md  # 功能介绍文档
├── .gitignore             # 安全排除规则
└── README.md
```

## 三个 Skill 速览

### 1. wechat-sender（macOS 发送）

通过微信 Mac 桌面端发送文本消息和文件。

- **文本发送**：自动激活微信 → 搜索联系人 → 粘贴消息 → 发送
- **文件发送**：Finder 复制文件 → 粘贴到微信聊天框 → 发送
- **签名支持**：默认添加 `—— workbuddy使用mac发送` 标识
- **日志 & 截图**：自动记录发送日志和确认截图

**核心特性**：
- 联系人中文名自动转拼音搜索
- 应对 Electron 窗口的 Cmd+F 连发机制
- System Events `set frontmost` 可靠激活

### 2. wechat-sender-win（Windows 发送）

Windows 版的微信发送 Skill，适配 Windows 微信客户端。

- 使用 `pygetwindow` + `win.activate()` 激活窗口
- `Ctrl+F` 搜索，`Ctrl` 替代 `Cmd` 系列快捷键
- ⚠️ 未在 Windows 环境实测，欢迎反馈

### 3. wechat-reader（macOS 读取）

通过截图 + 可选 OCR 读取微信聊天记录。

- **截图模式**：打开聊天 → 系统截图 → 返回截图路径
- **OCR 模式**（需安装 tesseract）：自动识别截图中的文字

## 安装与使用

### 前置条件

1. 微信桌面客户端已登录
2. macOS 辅助功能权限已授权（系统设置 > 隐私与安全性 > 辅助功能）
3. Python 3.9+

### 安装依赖

```bash
pip install pyautogui pyperclip pypinyin Pillow python-docx
```

### 安装到 WorkBuddy

```bash
# 将 Skill 目录复制到 WorkBuddy skills 目录
cp -r wechat-sender ~/.workbuddy/skills/
cp -r wechat-sender-win ~/.workbuddy/skills/
cp -r wechat-reader ~/.workbuddy/skills/
```

### 使用示例

在 WorkBuddy 中直接对话即可触发：

- "给 Fred 发微信：会议改到下午 3 点"
- "查看龙虾作战室群的消息"
- "把这个文件发到微信文件传输助手"

## 技术原理

| 组件 | 技术方案 |
|------|---------|
| 窗口激活 | macOS: System Events `set frontmost` / Windows: `pygetwindow.activate()` |
| 按键模拟 | `pyautogui.hotkey()` |
| 剪贴板 | `pyperclip` |
| 拼音转换 | `pypinyin`（中文联系人 → 拼音搜索） |
| 截图 | macOS: `screencapture` 系统命令 |
| OCR（可选） | `tesseract` + `pytesseract` |

## 能力与边界

| ✅ 能做 | ❌ 不能做 |
|--------|----------|
| 发送/读取文本消息 | 发送/读取图片、语音、视频 |
| 发送本地文件 | 批量群发 |
| 单次读取一个聊天 | 自动滚动历史消息 |
| macOS (sender + reader) | Windows reader（待开发） |

## 安全与隐私

- **不上传敏感数据**：日志、截图、聊天记录均通过 `.gitignore` 排除
- **本地运行**：所有操作在本地完成，不经过第三方服务器
- **签名区分**：自动添加 `workbuddy` 签名，方便接收方识别
- **建议**：使用前检查脚本内容，确认无意外操作

## 贡献

欢迎提交 Issue 和 PR。如有 Windows 环境测试反馈，请告知。

## License

MIT
