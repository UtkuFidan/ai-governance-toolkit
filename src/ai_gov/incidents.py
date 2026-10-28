"""Incident lessons: failure-mode categories mapped to controls.

AI Incident Database (AIID) terms of use (checked 2026-10-28): the incident, classification and
entity collections in the snapshots are under CC BY-SA, but the report `text` field, submissions and
displayed media are excluded from that licence. This module therefore keeps only AGGREGATED COUNTS
and incident ids/links, never incident text. The author's own category mapping ships with the repo;
counts are computed from a snapshot the user downloads themselves.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

CATEGORIES_FILE = Path(__file__).parent / "data" / "incident_categories.yaml"
AIID_URL = "https://incidentdatabase.ai/"
SNAPSHOT_PAGE = "https://incidentdatabase.ai/research/snapshots/"


class IncidentCategory(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    name: str
    keywords: list[str]
    controls: list[str]
    why: str


def load_categories() -> list[IncidentCategory]:
    raw = yaml.safe_load(CATEGORIES_FILE.read_text())["categories"]
    return [IncidentCategory.model_validate(c) for c in raw]


def bucket(text: str, cats: list[IncidentCategory]) -> list[str]:
    t = text.lower()
    return [c.id for c in cats if any(k in t for k in c.keywords)]


def count_snapshot(csv_path: Path, examples: int = 3) -> dict:
    """Aggregate an AIID `incidents.csv` snapshot. Returns counts and ids only (no text)."""
    cats = load_categories()
    counts: Counter = Counter()
    ids: dict[str, list[str]] = defaultdict(list)
    n = unmatched = 0
    with csv_path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            n += 1
            hit = bucket(f"{row.get('title', '')} {row.get('description', '')}", cats)
            if not hit:
                unmatched += 1
            for c in hit:
                counts[c] += 1
                if len(ids[c]) < examples:
                    ids[c].append(str(row.get("incident_id", "")))
    return {
        "incidents_in_snapshot": n,
        "unmatched": unmatched,
        "by_category": {
            c.id: {
                "count": counts[c.id],
                "example_links": [f"{AIID_URL}cite/{i}/" for i in ids[c.id]],
            }
            for c in cats
        },
        "method": "keyword bucketing of title+description; one incident can sit in several categories",
        "source": SNAPSHOT_PAGE,
    }
