#!/usr/bin/env python3
"""One-time maintenance script for the cleardl ICT/SMC-lite fork.

Keeps only ICT/SMC knowledge cards and removes the original project's market-data,
indicator, chart-rendering, annotation, multi-school, embedding and packaging layers.

This script intentionally does NOT implement market data or chart rendering.
Those integrations are TODOs for the project's own MarketLens/MCP stack.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge_base"
ALLOWED_SCHOOLS = {"ICT", "SMC"}

REMOVE_DIRS = [
    "agents",
    "docs",
    "evals",
    "platforms",
    "tests",
    "knowledge_base/embedding_seed_v2",
    "knowledge_base/schemas",
    "scripts/_lib",
    "scripts/chart_render",
]

REMOVE_FILES = [
    "CHANGELOG.md",
    "CHANGELOG.zh.md",
    "INSTALL.md",
    "PRIVACY.md",
    "README_AGENT.md",
    "SKILL.body.md",
    "install.py",
    "install.ps1",
    "install.sh",
    "knowledge_base/_merge_report.json",
    "scripts/build_index.py",
    "scripts/build_knowledge_v2.py",
    "scripts/build_workbuddy_package.py",
    "scripts/evaluate_retrieval.py",
    "scripts/export_v2_embedding_seed.py",
    "scripts/kb_doctor.py",
    "scripts/kb_draw_annotation.py",
    "scripts/kb_klines.py",
    "scripts/kb_phase_b_to_c.py",
    "workflows/analysis_profiles.md",
    "workflows/annotate.md",
    "workflows/klines.md",
    ".github/workflows/prune-ict-smc-lite.yml",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: object) -> None:
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def card_id(card: dict) -> str | None:
    return card.get("global_card_id") or card.get("card_id")


def canonical(card: dict) -> str:
    return (
        card.get("global_canonical")
        or card.get("canonical_term")
        or card.get("title")
        or card_id(card)
        or ""
    )


def prune_cards(directory: Path) -> tuple[list[dict], int]:
    kept: list[dict] = []
    removed = 0
    for path in sorted(directory.glob("*.json")):
        try:
            card = load_json(path)
        except Exception as exc:
            raise RuntimeError(f"Invalid JSON: {path}: {exc}") from exc
        if card.get("school") not in ALLOWED_SCHOOLS:
            path.unlink()
            removed += 1
            continue
        kept.append(card)
    return kept, removed


def clean_cross_references(concepts: list[dict], cases: list[dict]) -> None:
    concept_ids = {card_id(c) for c in concepts if card_id(c)}
    case_ids = {card_id(c) for c in cases if card_id(c)}

    for path in sorted((KB / "concepts").glob("*.json")):
        card = load_json(path)
        changed = False

        rel = card.get("related_concepts")
        if isinstance(rel, list):
            new_rel = []
            for item in rel:
                if not isinstance(item, dict):
                    continue
                rid = item.get("global_card_id") or item.get("card_id")
                # Preserve term-only links; remove links explicitly targeting removed cards.
                if rid and rid not in concept_ids:
                    changed = True
                    continue
                new_rel.append(item)
            if new_rel != rel:
                card["related_concepts"] = new_rel

        illustrated = card.get("illustrated_by_cases")
        if isinstance(illustrated, list):
            new_illustrated = []
            for item in illustrated:
                if isinstance(item, str):
                    iid = item
                elif isinstance(item, dict):
                    iid = item.get("global_card_id") or item.get("card_id")
                else:
                    iid = None
                if iid and iid not in case_ids:
                    changed = True
                    continue
                new_illustrated.append(item)
            if new_illustrated != illustrated:
                card["illustrated_by_cases"] = new_illustrated

        if changed:
            write_json(path, card)

    for path in sorted((KB / "cases").glob("*.json")):
        card = load_json(path)
        changed = False

        ids = card.get("illustrates_concepts")
        if isinstance(ids, list):
            new_ids = [x for x in ids if not isinstance(x, str) or x in concept_ids]
            if new_ids != ids:
                card["illustrates_concepts"] = new_ids
                changed = True

        rel = card.get("related_concepts")
        if isinstance(rel, list):
            new_rel = []
            for item in rel:
                if not isinstance(item, dict):
                    continue
                rid = item.get("global_card_id") or item.get("card_id")
                if rid and rid not in concept_ids:
                    changed = True
                    continue
                new_rel.append(item)
            if new_rel != rel:
                card["related_concepts"] = new_rel

        if changed:
            write_json(path, card)


def rebuild_metadata(concepts: list[dict], cases: list[dict]) -> None:
    now = datetime.now(timezone.utc).isoformat()

    concept_rows = sorted(
        (
            {
                "card_id": card_id(c),
                "canonical_term": canonical(c),
                "school": c.get("school"),
            }
            for c in concepts
            if card_id(c)
        ),
        key=lambda x: (x["canonical_term"].lower(), x["card_id"]),
    )
    case_rows = sorted(
        (
            {
                "card_id": card_id(c),
                "title": canonical(c),
                "school": c.get("school"),
            }
            for c in cases
            if card_id(c)
        ),
        key=lambda x: (x["title"].lower(), x["card_id"]),
    )

    write_json(
        KB / "index.json",
        {
            "generated_at": now,
            "scope": ["ICT", "SMC"],
            "n_concepts": len(concept_rows),
            "n_cases": len(case_rows),
            "concepts": concept_rows,
            "cases": case_rows,
        },
    )

    mappings = []
    for c in concepts:
        cid = card_id(c)
        if not cid:
            continue
        aliases = c.get("aliases")
        mappings.append(
            {
                "canonical": canonical(c),
                "card_id": cid,
                "school": c.get("school"),
                "aliases": aliases if isinstance(aliases, list) else [],
            }
        )
    mappings.sort(key=lambda x: (x["canonical"].lower(), x["card_id"]))
    write_json(KB / "term_aliases.json", {"generated_at": now, "mappings": mappings})

    write_json(
        KB / "schools.json",
        {
            "registry_version": 1,
            "knowledge_schema_version": 1,
            "default_profile": {"id": "ict_smc", "schools": ["ICT", "SMC"]},
            "schools": [
                {
                    "id": "ict",
                    "name": "ICT",
                    "aliases": ["Inner Circle Trader"],
                    "knowledge_qna": True,
                },
                {
                    "id": "smc",
                    "name": "SMC",
                    "aliases": ["Smart Money Concepts"],
                    "knowledge_qna": True,
                },
            ],
            "todo": {
                "market_data": "Integrate MarketLens/MCP; intentionally not provided by this skill.",
                "chart_rendering": "Implement in project renderer; intentionally not provided by this skill.",
                "market_structure_tools": "Expose project-owned deterministic tools via MCP as needed.",
            },
        },
    )


def remove_legacy_layers() -> None:
    for rel in REMOVE_DIRS:
        path = ROOT / rel
        if path.exists():
            shutil.rmtree(path)
    for rel in REMOVE_FILES:
        path = ROOT / rel
        if path.exists():
            path.unlink()

    (ROOT / "requirements.txt").write_text(
        "# Runtime: Python 3.10+ standard library only.\n"
        "# TODO: add project-specific MCP/client dependencies only when MarketLens integration lands.\n",
        encoding="utf-8",
    )


def main() -> None:
    concepts, removed_concepts = prune_cards(KB / "concepts")
    cases, removed_cases = prune_cards(KB / "cases")

    clean_cross_references(concepts, cases)

    # Reload because cross-reference cleanup may have rewritten cards.
    concepts = [load_json(p) for p in sorted((KB / "concepts").glob("*.json"))]
    cases = [load_json(p) for p in sorted((KB / "cases").glob("*.json"))]

    rebuild_metadata(concepts, cases)
    remove_legacy_layers()

    print(
        f"ICT/SMC prune complete: concepts={len(concepts)} "
        f"(removed {removed_concepts}), cases={len(cases)} "
        f"(removed {removed_cases})"
    )


if __name__ == "__main__":
    main()
