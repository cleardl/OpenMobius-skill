# Workflow: ICT/SMC Concept Q&A

Use this workflow for definitions, distinctions, rules, terminology, strategy logic, and conceptual debates about ICT/SMC.

## 1. Form a retrieval query

Use the user's exact term plus nearby ICT/SMC concepts when useful.

Examples:

Fair Value Gap displacement imbalance
Order Block Breaker CISD
internal external liquidity DOL
SMT divergence correlated markets

## 2. Retrieve local knowledge

<PYTHON> scripts/kb_retrieve.py "<query>" --top-k 5 --format compact

Use --type concept for pure definitions and --type case when examples are important.

Use --school ICT or --school SMC only when the user explicitly asks for one side.

## 3. Answer from the cards

Prefer:

- definition
- identification rules
- trading implication
- common mistakes
- source-specific differences

Do not repeat every field mechanically.

When the cards contain conflicting claims, identify the disagreement. Do not turn a source-specific rule into universal ICT doctrine.

## 4. Separate description from causal story

ICT/SMC teaching often uses causal language about institutions, market makers, stop hunting or price delivery.

When the user asks whether such claims are literally true, distinguish:

- the observable price pattern,
- the ICT/SMC interpretation,
- what can and cannot be inferred from ordinary OHLC(V) data.

Do not present an institutional-intent narrative as directly observed fact.

## 5. No market-data fabrication

This workflow contains no live data.

If the user changes from a conceptual question to “what is ES/NQ doing now?”, switch to analyze.md and require either:

- user-provided chart/data, or
- an external market-data tool such as the future MarketLens/MCP integration.
