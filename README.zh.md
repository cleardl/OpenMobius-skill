# ICT/SMC Knowledge Skill

这是从 OpenMobius-skill 精简出来的 ICT/SMC 专用版本。

目标不是做一个“全能交易 Agent”，而是把 ICT/SMC 知识与分析规则单独留下，行情数据、指标、图表和截图交给项目自己的基础设施实现。

## 当前保留内容

- 346 张 ICT/SMC 概念卡
- 904 张 ICT/SMC 案例卡
- SKILL.md
- 轻量本地检索 scripts/kb_retrieve.py
- 概念问答工作流 workflows/qna.md
- 行情/图表分析工作流骨架 workflows/analyze.md

知识库只允许 ICT 与 SMC，其他 School / 分类已经从这个 fork 中删除。

## 已删除

这个 fork 不再包含：

- 缠论
- Wyckoff
- Price Action
- VSA / Volume Analysis
- Elliott Wave
- Order Flow School
- Mobius Quant 行情 API
- SMC 自动指标 / detector
- 60+ 技术指标接口
- Playwright / Chromium
- lightweight-charts
- Pillow 图像标注
- ChromaDB
- embedding 模型和 seed
- 多 School 路由
- WorkBuddy / Cursor / Claude Code 等专用安装器和打包逻辑

因此安装后不会再下载数百 MB 的 embedding 模型或 Chromium。

运行时只要求 Python 3.10+，kb_retrieve.py 只使用 Python 标准库。

## 设计边界

这个 Skill 负责：

ICT/SMC 知识 -> 规则检索 -> AI 分析框架

它不负责：

行情获取 / 指标计算 / Volume Profile / Delta / Footprint / 图表渲染 / 截图

这些能力应该由外部项目提供。

计划中的架构：

AI Agent
  ├─ ICT/SMC Skill
  │    └─ 知识 / 规则 / 分析框架
  └─ MarketLens MCP
       ├─ ES/NQ OHLC(V)
       ├─ session / timeframe
       ├─ swing / structure（可选）
       ├─ POC / HVN / LVN（可选）
       ├─ Delta / Footprint（可选）
       └─ chart / screenshot（项目自行实现）

## TODO：MarketLens/MCP

目前 workflows/analyze.md 只定义分析输入契约，不绑定任何具体行情 API。

后续接入 MarketLens 时，建议至少提供：

- symbol
- timeframe
- session
- 数据时间范围
- OHLC / OHLCV
- 数据是否为 completed bar
- 数据来源与 freshness

可选：

- Swing / market structure
- Volume Profile：POC / HVN / LVN
- Delta / footprint / aggressive buy-sell
- 图表截图或 renderer 输出

Skill 不会在这些数据缺失时假装它们存在。

## 使用

概念检索：

python scripts/kb_retrieve.py "Fair Value Gap" --top-k 5 --format compact
python scripts/kb_retrieve.py "Order Block Breaker CISD" --top-k 8
python scripts/kb_retrieve.py "SMT divergence" --school ICT

只看案例：

python scripts/kb_retrieve.py "liquidity sweep ES NQ" --type case --top-k 5

JSON 输出：

python scripts/kb_retrieve.py "FVG" --format json

## 分析原则

这个 fork 特意避免把机械 detector 的结果当作 ground truth。

分析时要分清三层：

1. ICT/SMC 规则：知识库怎么定义。
2. 实际证据：图或行情数据到底发生了什么。
3. 解释：基于规则和证据得出的结论。

例如三根 K 线满足形式上的 FVG，并不自动意味着它就是一个高质量交易区域。还应结合 displacement、liquidity、market structure、时间背景以及外部提供的 VP / Order Flow 证据。

详见 SKILL.md 与 workflows/analyze.md。

## 来源与许可证

本仓库由 OpenMobius-skill fork 精简而来。保留上游 LICENSE 与 ATTRIBUTION.md。
