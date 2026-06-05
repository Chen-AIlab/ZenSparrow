# skunk

**网站探索工具箱** — 连接真实浏览器，自动浏览页面、截图留证、提取导航结构、检测前端报错，搞清楚一个网站的全貌。

## 解决什么问题

产品经理、设计师、QA 想搞清楚一个网站的页面结构和用户路径时，通常只能手动点一遍，截图、记笔记、画流程图。站点改版了又要重来一遍。

skunk 把这个过程自动化：像一个真实用户那样浏览网站，沿途记录每一步——看到了什么页面、点哪里能跳过去、哪些页面有 JS 报错。

## 四个模块

| 模块 | 作用 | 探索场景 |
|------|------|-------------|
| `browser` | 启动或连接已有 Chrome，注入反指纹脚本 | 用你日常的浏览器，带上登录态，不会被当成机器人踢掉 |
| `page` | 安全导航 + 人类滚动节奏 | 模拟真实用户的浏览行为，触发懒加载和动态内容 |
| `dom` | 多选择器兜底提取，console 报错收集 | 提取页面链接、导航结构；同时检测哪些页面有前端报错 |
| `snapshot` | 失败时自动保存 HTML 快照 + 截图 | 每一步都留底，事后可以回溯审查 |

## 技术细节

这些是在实际项目中踩坑后沉淀下来的——每个点背后都对应着一类"不处理就会翻车"的场景。

**反指纹注入**：启动时自动向页面注入脚本，修复三个最常见的自动化检测点：
- `navigator.webdriver` → 置为 undefined
- `navigator.plugins` → 填入真实 Chrome 插件列表
- `Notification.permissions.query` → 返回用户正常交互才会有的状态

**Fallback 选择器链**：不依赖单一选择器。`extract_with_fallbacks` 按优先级逐个尝试，CSS Modules 的 hash 变了、DOM 结构改了，只要有一个备选命中就能拿到结果。`extract_all_with_fallbacks` 遍历所有备选并自动去重。

**CDP 深层序列化解包**：`Runtime.evaluate` 返回的 JS 对象有时是 `[[k,v],...]` 嵌套数组或 `{"type":"object","value":...}` 包装格式。`deep_to_python` 递归解包成普通 Python dict/list，调用方无需关心 CDP 的内部格式。

**Console 劫持**：在页面脚本执行前注入，拦截 `console.error` 和 `console.warn`，存入 `window.__ce` / `window.__cw`。重复注入无害（内部标志位防双重劫持）。探索完一个页面后读取，就知道哪些 JS 悄悄挂了。

**容错设计**：
- 导航失败自动重试（默认 2 次），最终返回 False 而非抛异常
- 提取失败返回 None，不阻塞后续流程
- 快照保存失败不中断探索
- `close_browser` 对已关闭的浏览器调用不抛异常

## 和其他工具的区别

一般爬虫关注"爬得快、存得多"。skunk 关注"像一个真实访客那样看网站"：

- **CDP 连接模式**：连到你本机正在用的 Chrome，网站看到的是你，不是一个无头幽灵
- **滚动行为仿真**：随机幅度、随机间隔，不触发风控
- **自动留底**：每步截图 + HTML 保存，不用手动复制粘贴
- **报错探测**：劫持 console.error/warn，页面默默挂了你能知道

## 快速开始

```bash
pip install git+https://github.com/Chen-AIlab/ZenSparrow.git
```

```python
import asyncio
from pathlib import Path
from skunk import launch_browser, safe_goto, human_scroll
from skunk import extract_with_fallbacks, extract_all_with_fallbacks
from skunk import inject_console_hook, save_screenshot, save_html_snapshot

async def explore_site():
    browser, context = await launch_browser(headless=False)
    page = await context.new_page()

    # 注入报错探测
    await inject_console_hook(page)

    # 访问首页
    await safe_goto(page, "https://example.com", wait_selector="body")
    await human_scroll(page)

    # 提取所有导航链接
    links = await extract_all_with_fallbacks(page, [
        'nav a', '[class*="nav"] a', 'a[href]'
    ], attribute="href")

    # 截图 + 保存 HTML
    await save_screenshot(page, Path("journey"), label="homepage")
    await save_html_snapshot(page, Path("journey"), label="homepage")

    # 检测报错
    errors = await page.evaluate("window.__ce || []")
    print(f"首页 JS 报错: {len(errors)} 条")

    # 逐页探索...
    await browser.close()

asyncio.run(explore_site())
```

### 连接已有 Chrome（推荐）

```bash
# 终端启动带调试端口的 Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome_profile
```

```python
browser, context = await launch_browser(cdp_url="http://localhost:9222")
# 此后的所有操作都在你真实的 Chrome 里执行，带着你的登录态
```

## 依赖

仅 `playwright`。安装后运行 `playwright install chromium`。

## 设计原则

- 每个模块 < 100 行
- 零额外依赖（除 Playwright）
- 函数式 API，无基类/抽象层
- 不抛致命异常——导航失败返回 False，提取失败返回 None
- 默认参数覆盖最常见场景，需要时可逐个覆盖
