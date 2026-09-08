# Workflow: ICT/SMC Market / Chart Analysis

Use this workflow when the user asks to analyze:

- an attached chart,
- pasted OHLC/OHLCV,
- structured market data,
- or data returned by an external market-data tool.

This fork contains no built-in market-data client and no chart renderer.

## Input provenance

Before analysis, identify which input path is being used.

### Path A — user chart image

Use visual evidence from the image.

- Read only prices/timestamps that are actually legible.
- Approximate visual structure may be discussed with uncertainty.
- Do not invent exact levels hidden by resolution/cropping.
- This skill does not annotate or redraw the image.

### Path B — user-pasted data

Preserve the supplied snapshot.

State the timeframe/session if supplied. Do not silently replace it with another dataset.

### Path C — external market-data tool

TODO: integrate MarketLens/MCP.

Expected minimum payload:

symbol
timeframe
session
time range
OHLC or OHLCV
bar completion status
source/provenance
freshness timestamp

Optional external evidence:

swing / structure
POC / HVN / LVN
Delta / footprint
aggressive buy/sell
chart screenshot / renderer output

Never claim optional evidence if it was not actually provided.

## Grounding

Retrieve only concepts relevant to what is visible in the data.

Typical query:

<PYTHON> scripts/kb_retrieve.py "liquidity sweep displacement CISD MSS FVG order block" --top-k 8 --format compact

For a specific pattern, run a narrower second retrieval rather than loading the entire knowledge base.

## Analysis sequence

Use only the layers that are relevant.

### 1. Higher-timeframe context

- directional bias or range context
- relevant dealing range
- important previous highs/lows
- higher-timeframe PD Arrays when observable

### 2. Liquidity

Identify, when supported by evidence:

- Buy Side Liquidity / Sell Side Liquidity
- external vs internal liquidity
- equal highs/lows
- prior swing highs/lows
- sweep / run / grab distinctions

Do not assume every old high/low is a meaningful liquidity pool.

### 3. Delivery / structure change

Look for observable evidence of:

- displacement
- CISD
- MSS
- BOS / CHoCH

Treat terminology carefully because different ICT/SMC sources use overlapping but non-identical definitions.

A detector label is not proof by itself. Explain which prices/bars satisfy the retrieved rule.

### 4. PD Arrays

Evaluate only relevant arrays:

- FVG / IFVG
- Order Block
- Breaker
- Mitigation Block
- BPR
- Premium / Discount / Equilibrium
- other ICT/SMC arrays returned by retrieval

Do not mechanically treat every three-candle gap as a high-quality FVG or every final opposite candle as a meaningful Order Block.

### 5. Draw on Liquidity / scenarios

State the likely target or invalidation as a scenario, not certainty.

Prefer:

- bullish scenario
- bearish scenario
- what evidence would confirm it
- what evidence would invalidate it

### 6. Time context

Use Killzone, session, daily/weekly profile or news timing only when relevant and known.

### 7. Optional Volume Profile / Order Flow confirmation

This is external to the Skill.

If MarketLens or the user provides VP/Order Flow data, it may be used to test ICT hypotheses, for example:

- whether an Order Block overlaps a meaningful acceptance/HVN region,
- whether an FVG aligns with low-volume traversal/LVN behavior,
- whether CISD is accompanied by a change in aggressive order flow.

These are confirmations/challenges, not automatic replacements for ICT definitions.

## Required answer structure

For substantial market analysis, prefer:

### Data / provenance
What chart/data was actually used.

### Context
Higher-timeframe/range bias and relevant time context.

### Liquidity
Important external/internal liquidity and any sweep evidence.

### Structure / delivery
Displacement, CISD/MSS/BOS/CHoCH evidence.

### PD Arrays
Only the relevant FVG/OB/Breaker/etc. zones.

### Scenarios
Primary and alternate scenario, with confirmation/invalidation.

### Uncertainty
What cannot be known from the available data.

Do not fabricate trade execution, order flow, market-maker intent, or exact prices not present in the input.
