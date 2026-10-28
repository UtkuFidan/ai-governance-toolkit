"""Gap assessment: which controls apply to each system and what the register already shows.

Automatic checks only look at facts held in the register. Everything else is 'evidence
requested': a person must supply the document. A 'met' result means the register entry is
consistent with the control, not that the control operates effectively.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, timedelta

from .classify import Classification, Tier, classify
from .controls import Control, load_controls
from .schema import AISystem, Inventory, Provenance, Status
from .timeline import ObligationStatus, status_for

Check = Callable[[AISystem, Classification, date], tuple[bool, str]]


def _owner_defined(s, c, d):
    return bool(s.owner.strip()), f"owner role: {s.owner}"


def _not_prohibited(s, c, d):
    if c.tier is Tier.PROHIBITED:
        if s.status in (Status.REJECTED, Status.RETIRED):
            return True, "prohibited practice indicated, but the system is " + s.status.value
        return False, "answers indicate a prohibited practice (" + ", ".join(c.references) + ")"
    return True, "no prohibited practice indicated"


def _documentation_exists(s, c, d):
    n = len(s.documentation)
    return n >= 2, f"{n} document(s) listed (expect at least 2)"


def _data_dictionary(s, c, d):
    ok = any("data dictionary" in x.lower() for x in s.documentation)
    return ok, "data dictionary listed" if ok else "no data dictionary listed"


def _oversight_defined(s, c, d):
    m = s.human_oversight.mode.value
    return m != "none", f"oversight mode: {m}"


def _oversight_override(s, c, d):
    return (
        s.human_oversight.can_override,
        f"reviewer can override: {s.human_oversight.can_override}",
    )


def _validated(s, c, d):
    if s.last_validation is None:
        return False, "no validation date recorded"
    age = (d - s.last_validation).days
    return age <= 365, f"last validation {s.last_validation} ({age} days before {d})"


def _independent(s, c, d):
    return s.independent_validation, f"independent validation: {s.independent_validation}"


def _monitoring_defined(s, c, d):
    f = s.monitoring.frequency.strip().lower()
    return f not in ("", "none") and bool(
        s.monitoring.metrics
    ), f"frequency {f or 'none'}, {len(s.monitoring.metrics)} metric(s)"


def _thresholds(s, c, d):
    return s.monitoring.thresholds_defined, f"thresholds defined: {s.monitoring.thresholds_defined}"


def _no_open_incidents(s, c, d):
    open_ = [i for i in s.incidents if not i.resolved]
    return not open_, f"{len(open_)} open of {len(s.incidents)} incident(s)"


def _vendor_docs(s, c, d):
    docs = [x for x in s.documentation if "brochure" not in x.lower()]
    return len(docs) >= 2, f"{len(docs)} non-marketing document(s) from or about the vendor"


CHECKS: dict[str, Check] = {
    "owner_defined": _owner_defined,
    "not_prohibited": _not_prohibited,
    "documentation_exists": _documentation_exists,
    "data_dictionary_present": _data_dictionary,
    "oversight_defined": _oversight_defined,
    "oversight_can_override": _oversight_override,
    "validated_within_12_months": _validated,
    "independent_validation": _independent,
    "monitoring_defined": _monitoring_defined,
    "thresholds_defined": _thresholds,
    "no_open_incidents": _no_open_incidents,
    "vendor_documentation": _vendor_docs,
}


@dataclass
class ControlResult:
    control: Control
    status: str  # met | gap | evidence requested
    details: list[str] = field(default_factory=list)


@dataclass
class SystemGap:
    system: AISystem
    classification: Classification
    results: list[ControlResult]
    obligations: list[ObligationStatus] = field(default_factory=list)

    def count(self, status: str) -> int:
        return sum(1 for r in self.results if r.status == status)

    @property
    def gaps(self) -> list[ControlResult]:
        return [r for r in self.results if r.status == "gap"]


def applies(c: Control, s: AISystem, tier: Tier) -> bool:
    if tier.value not in c.tiers:
        return False
    if c.when == "personal_data":
        return s.uses_personal_data
    if c.when == "vendor":
        return s.provenance is Provenance.VENDOR
    if c.when == "production":
        return s.status in (Status.PRODUCTION, Status.PILOT)
    return True


def assess_system(s: AISystem, as_of: date) -> SystemGap:
    cl = classify(s)
    results = []
    live = s.status in (Status.PRODUCTION, Status.PILOT)
    for c in load_controls():
        if not applies(c, s, cl.tier):
            continue
        if c.id == "VAL-01" and not live:
            continue
        if not c.checks:
            results.append(ControlResult(c, "evidence requested", []))
            continue
        outs = [CHECKS[k](s, cl, as_of) for k in c.checks]
        status = "met" if all(ok for ok, _ in outs) else "gap"
        results.append(ControlResult(c, status, [msg for _, msg in outs]))
    return SystemGap(s, cl, results, status_for(cl, as_of))


def assess(inv: Inventory, as_of: date | None = None) -> list[SystemGap]:
    d = as_of or date.today()
    return [assess_system(s, d) for s in inv.systems]


def validation_due(s: AISystem) -> date | None:
    return s.last_validation + timedelta(days=365) if s.last_validation else None
