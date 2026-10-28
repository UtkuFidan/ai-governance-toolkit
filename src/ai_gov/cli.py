"""Command line: ai-gov inventory validate | classify | gap | timeline | evidence | report."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from pydantic import ValidationError

from . import report as rpt
from .classify import DISCLAIMER, classify
from .gap import assess
from .schema import json_schema, load_inventory


def _asof(s: str | None) -> date:
    return date.fromisoformat(s) if s else date.today()


def cmd_validate(a) -> int:
    try:
        inv = load_inventory(a.file)
    except (ValidationError, ValueError, OSError) as e:
        print(f"INVALID: {e}", file=sys.stderr)
        return 1
    print(f"OK: {len(inv.systems)} systems valid")
    if a.write_schema:
        Path(a.write_schema).write_text(json.dumps(json_schema(), indent=2) + "\n")
        print(f"schema written to {a.write_schema}")
    return 0


def cmd_classify(a) -> int:
    inv = load_inventory(a.file)
    print(DISCLAIMER + "\n")
    for s in inv.systems:
        c = classify(s)
        print(f"{s.id}  {c.tier.value:<28} {', '.join(c.references) or '-':<28} {s.name}")
        if a.verbose:
            for r in c.rationale + c.notes:
                print(f"      {r}")
    return 0


def cmd_gap(a) -> int:
    inv = load_inventory(a.file)
    for g in assess(inv, _asof(a.as_of)):
        print(
            f"{g.system.id}  {g.classification.tier.value:<28} met {g.count('met'):>2}  gap {g.count('gap'):>2}  evidence requested {g.count('evidence requested'):>2}  {', '.join(r.control.id for r in g.gaps)}"
        )
    return 0


def cmd_evidence(a) -> int:
    from .evidence import taiwan  # heavy imports only when needed

    out = Path(a.out)
    res = taiwan.run(Path(a.raw_dir))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=2) + "\n")
    for c in res["checks"]:
        print(f"{c['status']:<5} {c['check']}")
    print(f"written {out}")
    return 0


def cmd_report(a) -> int:
    inv = load_inventory(a.file)
    d = _asof(a.as_of)
    gaps = assess(inv, d)
    outdir = Path(a.out_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    ev = rpt.load_evidence(outdir / "evidence_results.json")
    (outdir / "ai_governance_report.md").write_text(rpt.markdown(inv, gaps, d, ev))
    (outdir / "register.html").write_text(rpt.html_register(inv, gaps, d))
    print(f"written {outdir / 'ai_governance_report.md'} and {outdir / 'register.html'}")
    return 0


def cmd_timeline(a) -> int:
    from .timeline import load_timeline

    d = _asof(a.as_of)
    print(f"EU AI Act obligation groups as of {d.isoformat()} (not legal advice)\n")
    for o in sorted(load_timeline()[1], key=lambda o: o.current):
        was = f"  (was {o.original.isoformat()})" if o.postponed else ""
        print(
            f"{'applies' if o.applies_on(d) else 'not yet':<8} {o.current.isoformat()}{was}  {o.title}"
        )
    return 0


def cmd_incidents(a) -> int:
    from . import incidents

    if a.snapshot:
        res = incidents.count_snapshot(Path(a.snapshot))
        print(json.dumps(res, indent=2))
        return 0
    for c in incidents.load_categories():
        print(f"{c.name}: {', '.join(c.controls)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="ai-gov", description="AI governance toolkit (illustrative data, not legal advice)"
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    inv = sub.add_parser("inventory").add_subparsers(dest="sub", required=True)
    v = inv.add_parser("validate")
    v.add_argument("--file")
    v.add_argument("--write-schema", metavar="PATH")
    v.set_defaults(fn=cmd_validate)
    c = sub.add_parser("classify")
    c.add_argument("--file")
    c.add_argument("-v", "--verbose", action="store_true")
    c.set_defaults(fn=cmd_classify)
    g = sub.add_parser("gap")
    g.add_argument("--file")
    g.add_argument("--as-of")
    g.set_defaults(fn=cmd_gap)
    e = sub.add_parser("evidence")
    e.add_argument("--raw-dir", default="data/raw")
    e.add_argument("--out", default="reports/evidence_results.json")
    e.set_defaults(fn=cmd_evidence)
    r = sub.add_parser("report")
    r.add_argument("--file")
    r.add_argument("--as-of")
    r.add_argument("--out-dir", default="reports")
    r.set_defaults(fn=cmd_report)
    t = sub.add_parser("timeline")
    t.add_argument("--as-of")
    t.set_defaults(fn=cmd_timeline)
    i = sub.add_parser("incidents")
    i.add_argument("--snapshot", help="path to an AIID incidents.csv you downloaded")
    i.set_defaults(fn=cmd_incidents)
    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
