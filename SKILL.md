---
name: ict-smc-knowledge
description: Lightweight ICT/SMC trading knowledge skill for concept Q&A and evidence-grounded market analysis. Use for ICT/SMC terms such as liquidity, FVG, Order Block, Breaker, Mitigation Block, CISD, MSS, BOS/CHoCH, SMT, PD Array, Premium/Discount, DOL, Killzone, Daily/Weekly Profiles, and related chart analysis. This fork contains no market-data client, indicator engine, chart renderer, screenshot pipeline, or non-ICT/SMC schools. Market data and rendering must come from user-provided inputs or an external project tool such as MarketLens/MCP.
---

# ICT/SMC Knowledge Skill

A lightweight ICT/SMC-only fork of OpenMobius-skill.

The skill has two jobs:

1. Ground ICT/SMC concept answers in the local knowledge cards.
2. Ground market/chart analysis in both local ICT/SMC rules and observable evidence supplied by the user or an external market-data tool.

It intentionally does not fetch market data, calculate indicators, render charts, launch Chromium, or annotate screenshots.

## Scope

Included:

- 346 ICT/SMC concept cards.
- 904 ICT/SMC case cards.
- Local lexical retrieval using Python standard library only.
- Concept Q&A workflow.
- Market/chart analysis workflow skeleton.

Removed:

- ChanLun, Wyckoff, Price Action, VSA, Elliott Wave, Order Flow and other non-ICT/SMC schools/categories.
- Mobius Quant API client and symbol resolver.
- Built-in SMC indicator/detector.
- Technical-indicator API.
- Playwright / Chromium / lightweight-charts renderer.
- Pillow annotation pipeline.
- ChromaDB, embeddings and model downloads.
- Multi-school routing and compare/augment logic.
- Platform-specific installers and packaging.

## External integration TODO

Market data and rendering belong to the host project.

TODO: wire the analysis workflow to MarketLens/MCP or another project-owned data layer.

Expected responsibilities of the external layer:

- Fetch current/historical OHLC or OHLCV.
- Expose exact session/timeframe/provenance.
- Optionally expose deterministic swing/structure calculations.
- Optionally expose Volume Profile: POC, HVN, LVN.
- Optionally expose Delta / footprint / order-flow evidence.
- Render or screenshot charts when required.

This skill must not silently fall back to remembered prices or pretend that external data exists.

## Core reasoning rule

Never collapse these three layers into one:

1. ICT/SMC rule — what the retrieved knowledge card says.
2. Observed evidence — what is actually visible in the chart/data.
3. Interpretation — the conclusion drawn from the rule + evidence.

A mechanically detected pattern is not ground truth. For example, a three-candle non-overlap may satisfy a formal FVG definition, but its context, displacement quality, liquidity relationship and relevance still require analysis.

## Routing

Use workflows/qna.md when the user asks about concepts, definitions, rules, distinctions, or strategy logic.

Use workflows/analyze.md when the user asks to analyze a chart, pasted market data, or market data provided by an external tool.

## Knowledge retrieval

Run:

<PYTHON> scripts/kb_retrieve.py "<query>" --top-k 5 --format compact

Examples:

<PYTHON> scripts/kb_retrieve.py "Fair Value Gap displacement" --type concept
<PYTHON> scripts/kb_retrieve.py "Order Block Breaker CISD" --top-k 8
<PYTHON> scripts/kb_retrieve.py "liquidity sweep NQ ES" --type case --top-k 5
<PYTHON> scripts/kb_retrieve.py "SMT divergence" --school ICT

Use --format json when structured output is needed.

## Analysis priorities

For ICT/SMC market analysis, prefer this sequence rather than scanning every concept:

1. Higher-timeframe context / bias.
2. External and internal liquidity.
3. Liquidity sweep / stop run.
4. Displacement and delivery-state change: CISD / MSS / BOS / CHoCH as applicable.
5. Relevant PD Arrays: FVG, IFVG, Order Block, Breaker, Mitigation Block, BPR, etc.
6. Draw on Liquidity / targets.
7. Time context: session, Killzone, daily/weekly profile when relevant.
8. Optional external confirmation: Volume Profile / Order Flow, only when such data was actually supplied.

Do not force all eight layers into every answer.

## Output discipline

- Preserve technical terms such as FVG, Order Block, Breaker, CISD, MSS, BOS, CHoCH, SMT, DOL, PD Array, IFVG.
- State uncertainty explicitly.
- Do not fabricate precise prices, levels, timestamps, Delta, POC/HVN/LVN, or footprint evidence.
- Do not claim that price must seek liquidity or fill an FVG.
- Distinguish descriptive ICT terminology from causal claims about institutions/market makers.
- When sources within the knowledge cards disagree, report the disagreement instead of merging it into a fake consensus.
