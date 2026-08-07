# 6 种导航模式 · 结构与代码要点

生成前只读本文件中所选模式的小节即可。

## 目录

- M1 线性 Linear
- M2 目录中心 Hub & Spoke
- M3 混合 Linear + Hub
- M4 长页滚动 Scrolling
- M5 时间线主轴 Timeline Hub
- M6 缩略图总览 Grid Overview
- 通用规范（所有模式共用）

---

## M1 线性 Linear

**结构**：单 HTML 文件，N 个 `<section class="slide">` 全屏平铺，JS 控制当前页。

**骨架**：`assets/linear/deck.html` 可直接改造，已内置：

- 键盘 ←→ / PageUp Down / 空格翻页；滚轮（带节流）；触屏 swipe；点击右半屏前进
- 底部 dot 分页指示器；ESC 呼出页码索引
- 入场动效：每个 section 内 `[data-anim]` 元素在翻页后序列 fade-up（Motion One 或纯 CSS transition 皆可）

**要点**：

- 翻页用 `transform:translateX(-N*100vw)` 整体横移或 section `display` 切换皆可；横移更有"放映"感。
- 滚轮必须加 300-600ms 节流，否则一滚翻三页。
- 内容超出 100vh 的页禁止出现——每页内容必须自含在一屏内。

**不适合**：需要现场自由跳转查阅的场合。

---

## M2 目录中心 Hub & Spoke

**结构**：多页面站点，共享一份 CSS。

```
app/
├── index.html      # 目录页（hub）：标题 + .hub-grid 卡片网格
├── shared.css      # 全部页面共用的设计系统 + .back-btn + .hub-card
├── topic-a.html    # 详情页（spoke），可多个
├── hub-b.html      # 二级目录（可选）：本身是详情页，卡片再链到子详情页
└── images/
```

**骨架**：`assets/hub-spoke/` 可直接改造，已内置：

- `.hub-card`：圆角卡片 + hover 上浮（`translateY(-4px)` + 阴影加深），整卡可点
- `.back-btn`：左上角固定胶囊返回按钮，链回目录页；二级目录里的详情页返回二级目录
- 详情页骨架：页眉 chrome + 大标题 + 内容区 + 页脚，所有详情页同一骨架保证格式稳定
- 二级目录写法：把 hub 卡片做成 `a.card-link` 包住详情卡片即可

**要点**：

- 返回按钮 `position:fixed; top; left; z-index` 要高，且不遮挡内容（详情页内容区左上留出安全距离）。
- 目录卡片数量建议 4-8 个；超过 8 个考虑分组或二级目录。
- 卡片网格用 `grid-template-columns:repeat(auto-fit,minmax(280px,1fr))` 自适应。

**不适合**：无人操作鼠标的纯自动放映场合。

---

## M3 混合 Linear + Hub

**现成骨架**：`assets/preview/m3.html` 是完整可运行的 M3 实现（含章节菜单呼出层、ESC 切换、jump(n) 跳转），直接改造，不要从零拼。

**结构**：在 M1 单文件基础上，把"目录"做成 ESC 呼出层或第 0 页：

- 目录层列出各章节锚点，点击 `goTo(n)` 直接跳到对应 section
- 菜单打开时禁用滚轮/键盘翻页，点击空白或再按 ESC 关闭
- 每个章节首页可放"⌂ 目录"小按钮 `goTo(0)`

**要点**：跳转后继续按 ←→ 线性走，两种导航不冲突。苹果/华为发布会实际就是这种模式。

---

## M4 长页滚动 Scrolling

**结构**：单文件，章节纵向排列，配合滚动体验：

- `scroll-snap-type:y proximity`（可选，让章节自动吸附）
- 章节进入视口时触发入场动效（IntersectionObserver 加 class）
- 顶部固定迷你进度条或章节锚点导航（小圆点/文字链）

**要点**：

- 不投屏使用，所以字号可以比演讲模式小（正文 16px 可接受）。
- 图片懒加载 `loading="lazy"`，长页性能关键。
- 结尾放"回到顶部"按钮。

**不适合**：投屏演讲——没有"当前页"概念，演讲者和观众容易脱节。

---

## M5 时间线主轴 Timeline Hub

**结构**：M2 的变体——目录页不是卡片网格，而是一条横向/纵向时间线，节点可点击进入详情页，返回按钮同 M2。

**要点**：

- 横向时间线节点上下交错排 label，避免拥挤；当前/重点节点用 accent 色放大。
- 节点 5-10 个最佳；更多则改用纵向时间线（左侧轴 + 右侧卡片）。
- 详情页骨架与 M2 完全相同。

**适合**：roadmap、排期、发展历程——目录本身就携带"先后顺序"信息。

---

## M6 缩略图总览 Grid Overview

**结构**：单文件，两层视图：

1. 总览层：所有 section 的缩略图平铺（CSS Grid）
2. 放映层：点击缩略图进入 M1 线性放映；ESC 退回总览

**缩略图实现**（二选一）：

- **同源缩放**（推荐，永远同步）：每个 section 复制进一个 `iframe` 或复用 DOM，外套容器 `transform:scale(0.18); transform-origin:top left; pointer-events:none`
- **截图**：Chromium headless 对每页截图生成 png，总览页引用；内容改动后需重新截图

**要点**：缩略图卡片 hover 高亮 + 显示页码标题；总览页本身也要能容纳 20-40 页不拥挤（每行 4-5 列）。

---

## 通用规范

**格式稳定（核心承诺）**：

- 同等级页面共用同一骨架类（如 `.page-shell`：页眉 / 标题区 / 内容区 / 页脚），边距用 CSS 变量（如 `--pad-x:5vw; --pad-y:5.6vh`）统一，禁止每页 inline 调边距。
- 标题统一左对齐在同一内容轴上（statement/封面页除外）。

**演示字号下限**：正文 ≥18px；说明/图注/卡片描述 ≥16px；meta/标签 ≥14px。

**可修改性约定**（用户常需自己改内容）：

- 图片槽位：`<img src="images/08-demo.png" onerror="this.style.display='none'">` + 附近放注释 `<!-- 图片槽位：把图片放到 images/08-demo.png 即自动显示 -->`
- 视频槽位：注释好的示例 `<!-- 视频：把上面 img 换成 <video src="images/08-demo.mp4" autoplay muted loop playsinline style="width:100%"> -->`
- 每处正文上方一行 HTML 注释标明"此处改 XX 文字"。

**试看版本**：任何模式生成后都必须 `build_version`（type html，project_dir /mnt/agents/output/app）。多页面模式确保 index.html 为入口；单文件模式文件名就是 index.html。

---

## 模式切换速查（内容迁移指引）

换模式时**保留内容文本，只重构导航骨架**。常见切换路径：

| 切换 | 操作 |
|---|---|
| M1 → M2 | 每个 `<section class="slide">` 拆成一个独立 `.html` 详情页（套 hub-spoke 的 page 骨架 + back-btn）；新建目录页，卡片 href 指向各详情页；删除翻页 JS |
| M2 → M1 | 每个详情页的主体内容按目录顺序包成 `<section class="slide">`，合并进单文件 `#track`；删除 back-btn，改页码（0X / NN） |
| M1 ↔ M4 | 线性页直接纵向堆叠：去掉 `#track` 平移和 `overflow:hidden`，section 改 `min-height:100vh`；M4 → M1 反向操作 |
| M2 → M5 | 目录卡片网格替换为时间线节点（`.tl-node`），href 不变，详情页骨架不动 |
| M1 → M3 | 保留线性轨道，新增 ESC 呼出章节菜单层（参考 `assets/preview/m3.html` 的 `#menu` 结构） |
| M1/M2 → M6 | 对每页截图（Chromium headless，`?s=N` 参数定位线性页）生成缩略图，做总览页，缩略图链接带页码参数 |

**迁移检查清单**：① 内容文字逐页核对无遗漏 ② 页码 / chrome 编号更新 ③ 返回/跳页手段在新模式下可用 ④ 图片槽位路径仍然有效 ⑤ 重新保存试看版本。
