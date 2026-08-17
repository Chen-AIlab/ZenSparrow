# ZenSparrow 🐦

个人工具箱，存放各种小功能制品，面向对外分享。

## 功能目录

| 功能 | 分支 | 说明 | 状态 |
|------|------|------|------|
| [微信发送](./tree/wechat-sender) | `wechat-sender` | 通过 AI 助手自动发送微信消息和文件，支持 macOS / Windows | ✅ |
| [skunk](./tree/skunk) | `skunk` | 网站探索工具箱：连接真实浏览器，自动浏览、截图、提取结构、检测报错 | ✅ |
| [deck-nav-modes](./tree/deck-nav-modes) | `deck-nav-modes` | 演讲材料导航模式生成器：6 种导航模式 + 内置体验馆，一键生成 HTML 演示材料 | ✅ |

## 使用方式

每个功能在独立分支中。查看某个功能：

```
# 切换到对应分支即可看到完整代码和文档
git checkout <分支名>
```

或者直接在 GitHub 上点击上方功能目录中的链接。

## 安装 skill（以 deck-nav-modes 为例）

`deck-nav-modes` 是一个 Claude Code skill（含 SKILL.md + 参考文档 + 体验馆，需完整下载）。

**方式一：git clone（推荐，最可靠）**

```bash
git clone -b deck-nav-modes --single-branch git@github.com:Chen-AIlab/ZenSparrow.git
cp -r ZenSparrow/deck-nav-modes ~/.claude/skills/
```

**方式二：下载 zip 压缩包**

在分支页点击 `Code → Download ZIP`，解压后把 `deck-nav-modes` 文件夹复制到 `~/.claude/skills/`。

完成后重启 Claude Code，即可在对话中直接使用该 skill。

## 版本更新

| 日期 | 更新 |
|------|------|
| 2026-08-07 | 上线 deck-nav-modes 演讲材料导航模式生成器 |
| 2026-06-05 | 上线 skunk 网站探索工具箱 |
| 2025-06-05 | 初始创建，上线 wechat-sender（macOS + Windows） |
