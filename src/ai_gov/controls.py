"""Control library loader and the requirement mapping view."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

DEFAULT_CONTROLS = Path(__file__).parent / "data" / "controls.yaml"


class Control(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    title: str
    objective: str
    tiers: list[str]
    when: str = "all"  # all | personal_data | vendor | production
    eu: list[str] = Field(default_factory=list)
    iso42001: list[str] = Field(default_factory=list)
    nist: list[str] = Field(default_factory=list)
    checks: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)

    @property
    def nist_functions(self) -> list[str]:
        return sorted({n.split()[0] for n in self.nist})


@lru_cache
def load_controls(path: Path | str | None = None) -> tuple[Control, ...]:
    p = Path(path) if path else DEFAULT_CONTROLS
    raw = yaml.safe_load(p.read_text())["controls"]
    controls = tuple(Control.model_validate(c) for c in raw)
    ids = [c.id for c in controls]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate control ids")
    return controls


def nist_coverage() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {"GOVERN": [], "MAP": [], "MEASURE": [], "MANAGE": []}
    for c in load_controls():
        for f in c.nist_functions:
            out[f].append(c.id)
    return out
