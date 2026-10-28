"""EU AI Act application timeline: which obligation groups apply on a given date.

Dates come from `data/ai_act_timeline.yaml` (Art 113 of Regulation (EU) 2024/1689 as amended by
Regulation (EU) 2026/1744). Not legal advice; check the consolidated text before relying on a date.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from .classify import Classification, Tier

TIMELINE_FILE = Path(__file__).parent / "data" / "ai_act_timeline.yaml"


class Act(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    title: str
    url: str
    in_force: date
    published_oj: date | None = None
    cited_by: list[str] = Field(default_factory=list)


class Obligation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    title: str
    articles: list[str]
    original: date | None
    current: date
    basis: str
    note: str = ""

    @property
    def postponed(self) -> bool:
        return self.original is not None and self.current > self.original

    def applies_on(self, d: date) -> bool:
        return d >= self.current


@dataclass
class ObligationStatus:
    obligation: Obligation
    applies: bool


@lru_cache
def load_timeline(path: Path | str | None = None) -> tuple[tuple[Act, ...], tuple[Obligation, ...]]:
    raw = yaml.safe_load(Path(path or TIMELINE_FILE).read_text())
    return (
        tuple(Act.model_validate(a) for a in raw["acts"]),
        tuple(Obligation.model_validate(o) for o in raw["obligations"]),
    )


def obligation(oid: str) -> Obligation:
    return next(o for o in load_timeline()[1] if o.id == oid)


def obligation_ids(c: Classification) -> list[str]:
    """Obligation groups that follow from a system's screening result."""
    ids = ["ai_literacy"]
    if c.tier is Tier.PROHIBITED:
        ids.append("prohibitions")
    if c.tier is Tier.HIGH:
        if "Art 6(2)" in c.references:
            ids.append("high_risk_annex_iii")
        if "Art 6(1)" in c.references:
            ids.append("high_risk_annex_i")
    if c.tier is Tier.LIMITED or any("Art 50" in n for n in c.notes):
        ids.append("transparency")
    return ids


def status_for(c: Classification, as_of: date) -> list[ObligationStatus]:
    return [ObligationStatus(o, o.applies_on(as_of)) for o in map(obligation, obligation_ids(c))]


def applicable_on(as_of: date) -> list[Obligation]:
    """All obligation groups that apply on the date, earliest first."""
    return sorted((o for o in load_timeline()[1] if o.applies_on(as_of)), key=lambda o: o.current)
