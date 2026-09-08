#!/usr/bin/env python3
"""Lightweight ICT/SMC knowledge retriever.

No network, ChromaDB, embeddings, model downloads, or external packages.
Ranks local JSON cards with a small BM25-style lexical scorer plus
canonical-term / alias boosts.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge_base"
ALLOWED_SCHOOLS = {"ICT", "SMC"}

WORD_RE = re.compile(r"[a-z0-9_+\-/]+|[\u4e00-\u9fff]+", re.I)
CJK_RE = re.compile(r"[\u4e00-\u9fff]+")


def normalize(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def terms(text: Any) -> list[str]:
    s = normalize(text)
    out: list[str] = []
    for token in WORD_RE.findall(s):
        out.append(token)
        if CJK_RE.fullmatch(token):
            chars = list(token)
            out.extend(chars)
            out.extend("".join(chars[i:i + 2]) for i in range(len(chars) - 1))
    return out


def card_id(card: dict) -> str:
    return str(card.get("global_card_id") or card.get("card_id") or "")


def title(card: dict) -> str:
    return str(
        card.get("global_canonical")
        or card.get("canonical_term")
        or card.get("title")
        or card_id(card)
    )


def flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(f"{k} {flatten(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " ".join(flatten(v) for v in value)
    return str(value)


def searchable_text(card: dict) -> str:
    preferred = [
        title(card),
        flatten(card.get("aliases")),
        flatten(card.get("definition")),
        flatten(card.get("definition_per_source")),
        flatten(card.get("identification_rules")),
        flatten(card.get("trading_implication")),
        flatten(card.get("common_mistakes")),
        flatten(card.get("market_context")),
        flatten(card.get("key_observation")),
        flatten(card.get("analysis_steps")),
        flatten(card.get("lessons")),
        flatten(card.get("asset")),
        flatten(card.get("timeframe")),
    ]
    return " ".join(x for x in preferred if x)


def load_cards(card_type: str, school: str | None) -> list[dict]:
    dirs: list[tuple[str, Path]] = []
    if card_type in ("all", "concept"):
        dirs.append(("concept", KB / "concepts"))
    if card_type in ("all", "case"):
        dirs.append(("case", KB / "cases"))

    cards: list[dict] = []
    for typ, directory in dirs:
        for path in sorted(directory.glob("*.json")):
            card = json.loads(path.read_text(encoding="utf-8"))
            if card.get("school") not in ALLOWED_SCHOOLS:
                continue
            if school and card.get("school") != school:
                continue
            card = dict(card)
            card["_type"] = typ
            card["_path"] = str(path.relative_to(ROOT)).replace("\\", "/")
            cards.append(card)
    return cards


def rank(query: str, cards: list[dict]) -> list[tuple[float, dict]]:
    q_terms = terms(query)
    if not q_terms:
        return []
    q_count = Counter(q_terms)

    docs: list[list[str]] = [terms(searchable_text(c)) for c in cards]
    dfs: Counter[str] = Counter()
    for doc in docs:
        for t in set(doc):
            if t in q_count:
                dfs[t] += 1

    n = max(1, len(cards))
    avgdl = sum(len(d) for d in docs) / n if docs else 1.0
    k1, b = 1.4, 0.75
    qnorm = normalize(query)

    ranked: list[tuple[float, dict]] = []
    for card, doc in zip(cards, docs):
        tf = Counter(doc)
        dl = max(1, len(doc))
        score = 0.0

        for t, qf in q_count.items():
            f = tf.get(t, 0)
            if not f:
                continue
            df = dfs.get(t, 0)
            idf = math.log(1.0 + (n - df + 0.5) / (df + 0.5))
            denom = f + k1 * (1.0 - b + b * dl / max(avgdl, 1e-9))
            score += idf * (f * (k1 + 1.0) / denom) * (1.0 + 0.1 * (qf - 1))

        canonical = normalize(title(card))
        aliases = [
            normalize(x)
            for x in (card.get("aliases") or [])
            if isinstance(x, str)
        ]

        if qnorm == canonical:
            score += 40.0
        elif qnorm and qnorm in canonical:
            score += 18.0

        for alias in aliases:
            if qnorm == alias:
                score += 32.0
            elif qnorm and qnorm in alias:
                score += 12.0

        if score > 0:
            ranked.append((score, card))

    ranked.sort(key=lambda x: (-x[0], title(x[1]).lower(), card_id(x[1])))
    return ranked


def compact_card(card: dict, score: float) -> dict:
    fields = {
        "score": round(score, 4),
        "type": card.get("_type"),
        "school": card.get("school"),
        "card_id": card_id(card),
        "title": title(card),
        "path": card.get("_path"),
    }
    if card.get("_type") == "concept":
        for key in (
            "definition",
            "identification_rules",
            "trading_implication",
            "common_mistakes",
            "merge_notes",
        ):
            if card.get(key):
                fields[key] = card[key]
    else:
        for key in (
            "asset",
            "timeframe",
            "market_context",
            "key_observation",
            "analysis_steps",
            "lessons",
        ):
            if card.get(key):
                fields[key] = card[key]
    return fields


def print_compact(results: list[tuple[float, dict]]) -> None:
    for i, (score, card) in enumerate(results, 1):
        print(f"## {i}. {title(card)}")
        print(
            f"school={card.get('school')} type={card.get('_type')} "
            f"score={score:.3f} id={card_id(card)}"
        )
        if card.get("_type") == "concept":
            if card.get("definition"):
                print("Definition:", card["definition"])
            rules = card.get("identification_rules") or []
            if rules:
                print("Rules:")
                for rule in rules[:8]:
                    print("-", rule)
            if card.get("trading_implication"):
                print("Implication:", card["trading_implication"])
            mistakes = card.get("common_mistakes") or []
            if mistakes:
                print("Common mistakes:")
                for item in mistakes[:5]:
                    print("-", item)
        else:
            if card.get("asset") or card.get("timeframe"):
                print(f"Context: {card.get('asset', '')} {card.get('timeframe', '')}".strip())
            if card.get("market_context"):
                print("Market context:", card["market_context"])
            if card.get("key_observation"):
                print("Key observation:", card["key_observation"])
            steps = card.get("analysis_steps") or []
            if steps:
                print("Analysis steps:")
                for step in steps[:8]:
                    print("-", step)
        print()


def main() -> int:
    p = argparse.ArgumentParser(description="Retrieve ICT/SMC knowledge cards")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--type", choices=["all", "concept", "case"], default="all")
    p.add_argument("--school", choices=["ICT", "SMC"], default=None)
    p.add_argument(
        "--format",
        choices=["compact", "json", "markdown"],
        default="compact",
    )
    p.add_argument("--list-schools", action="store_true")
    args = p.parse_args()

    if args.list_schools:
        payload = {"schools": ["ICT", "SMC"], "default": ["ICT", "SMC"]}
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print("ICT\nSMC")
        return 0

    if not args.query.strip():
        p.error("query is required unless --list-schools is used")
    if args.top_k < 1:
        p.error("--top-k must be >= 1")

    cards = load_cards(args.type, args.school)
    results = rank(args.query, cards)[: args.top_k]

    if args.format == "json":
        print(
            json.dumps(
                {
                    "query": args.query,
                    "count": len(results),
                    "results": [compact_card(c, s) for s, c in results],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_compact(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
