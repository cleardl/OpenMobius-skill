# ICT/SMC knowledge base

This directory contains only ICT and SMC cards.

knowledge_base/
  concepts/          346 ICT/SMC concept cards
  cases/             904 ICT/SMC case-study cards
  index.json         compact card catalog
  term_aliases.json  aliases for retained concepts
  schools.json       ICT/SMC-only registry + external integration TODOs

## Concept cards

Typical fields include school, definition, aliases, identification_rules, trading_implication, common_mistakes, definition_per_source, and source_cards.

## Case cards

Typical fields include school, asset, timeframe, market_context, key_observation, analysis_steps, lessons, and source provenance.

## Retrieval

The repository no longer ships vector indexes or embedding models.

Use:

python scripts/kb_retrieve.py "Fair Value Gap" --top-k 5 --format compact

The retriever scans the retained JSON cards locally and ranks them with a lightweight lexical/BM25-style score plus exact canonical/alias boosts.

## Provenance

The cards are retained from the upstream OpenMobius-skill knowledge base and filtered by the card-level school field. Only ICT and SMC cards remain.

See ATTRIBUTION.md and LICENSE.
