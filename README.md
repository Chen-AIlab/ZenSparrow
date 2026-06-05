# WeChat Sender

通过 RPA 模拟键盘鼠标，让 AI 助手自动发送微信消息和文件。

## 版本

| 目录 | 平台 | 签名 |
|------|------|------|
| [mac/](./mac/) | macOS | `—— workbuddy使用mac发送` |
| [win/](./win/) | Windows | `—— workbuddy使用win发送` |

## 快速开始

### macOS

```bash
pip install pyautogui pyperclip pypinyin Pillow python-docx
cp -r mac ~/.workbuddy/skills/wechat-sender/
```

### Windows

```bash
pip install pyautogui pyperclip pypinyin Pillow python-docx pygetwindow
# 将 win 目录复制到 skills 目录
```

## 功能

- 发送文本消息到联系人或群聊
- 发送本地文件
- 自动添加签名区分来源
- 发送日志 + 截图确认

## 能力边界

| ✅ | ❌ |
|----|-----|
| 文本消息 | 图片/语音/视频 |
| 本地文件 | 批量群发 |
| 中英文联系人 | 读取聊天记录 |

## 技术要点

- macOS：WeChat 是 Electron 应用，必须用 System Events `set frontmost` 激活
- 联系人中文名自动转拼音搜索
- Cmd+F/Ctrl+F 需连发确保 Electron 接收

## 注意事项

- 首次使用需在系统设置中授权辅助功能权限
- 发送期间不要操作键盘鼠标
- 微信需保持登录状态
