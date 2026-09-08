# ICT/SMC Knowledge Skill

A lightweight ICT/SMC-only fork of OpenMobius-skill.

This repository keeps the trading knowledge and analysis rules while removing the original market-data, indicator, rendering, embedding, multi-school, and packaging layers.

## Included

- 346 ICT/SMC concept cards
- 904 ICT/SMC case cards
- Standard SKILL.md
- Standard-library lexical retriever: scripts/kb_retrieve.py
- Q&A workflow
- Market/chart analysis workflow skeleton

## Removed

- ChanLun, Wyckoff, Price Action, VSA, Elliott Wave and other non-ICT/SMC schools
- Mobius Quant API integration
- Built-in SMC detector and indicator API
- Chart rendering and screenshot stack
- Playwright / Chromium / lightweight-charts
- Pillow annotation
- ChromaDB / embeddings / model seeds
- Multi-school routing
- Platform-specific installers and packages

Runtime requirement: Python 3.10+ only. The retriever uses the standard library.

## Architecture

AI Agent
  ├─ ICT/SMC Skill
  │    └─ knowledge / rules / analysis framework
  └─ External market-data layer
       └─ TODO: MarketLens/MCP

The external layer should own OHLC(V), sessions, deterministic structure tools, Volume Profile, Order Flow, and chart rendering.

See SKILL.md and workflows/analyze.md.

## Attribution

This repository is a trimmed fork of OpenMobius-skill. The upstream LICENSE and ATTRIBUTION.md are retained.
