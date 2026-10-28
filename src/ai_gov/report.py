"""Markdown report and HTML register."""

from __future__ import annotations

import html
import json
from collections import Counter
from datetime import date
from pathlib import Path

from .classify import DISCLAIMER, Tier
from .controls import load_controls, nist_coverage
from .gap import SystemGap
from .incidents import AIID_URL, SNAPSHOT_PAGE, load_categories
from .schema import Inventory
from .timeline import load_timeline

SOURCES = [
    (
        "Regulation (EU) 2024/1689 (AI Act), official text",
        "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        "EU law, reuse permitted with attribution (Decision 2011/833/EU)",
    ),
    (
        "Regulation (EU) 2026/1744 (Digital Omnibus on AI), amended application dates",
        "https://eur-lex.europa.eu/eli/reg/2026/1744/oj",
        "EU law, reuse permitted with attribution; dates cross-checked on the AI Act Service Desk timeline",
    ),
    (
        "NIST AI Risk Management Framework 1.0 (NIST AI 100-1)",
        "https://www.nist.gov/itl/ai-risk-management-framework",
        "US government work, public domain",
    ),
    (
        "ISO/IEC 42001:2023",
        "https://www.iso.org/standard/81230.html",
        "Copyrighted; only paraphrased clause themes used",
    ),
    (
        "UCI Default of Credit Card Clients (Yeh, 2009)",
        "https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients",
        "CC BY 4.0",
    ),
    (
        "AI Incident Database",
        SNAPSHOT_PAGE,
        "Snapshot collections CC BY-SA; report text excluded. Only counts and links used",
    ),
]


INCIDENT_STATUS = "the snapshot host (pub-72b2b2fc36ec423189843747af98f80e.r2.dev) timed out on repeated requests on 2026-10-28, the GraphQL API accepts only authorised origins, and the GitHub repository holds code without data."


def _esc(s) -> str:
    return html.escape(str(s))


def load_evidence(path: Path) -> dict | None:
    return json.loads(path.read_text()) if path.exists() else None


def _tier_counts(gaps: list[SystemGap]) -> Counter:
    return Counter(g.classification.tier.value for g in gaps)


def _intersectional(a, c: dict) -> None:
    m = c["metrics"]
    ci = m.get("ci95", {})
    a(
        f"- {c['check']}: {m['cells_included']} of {m['cells_total']} cells have at least {m['min_cell_size']} people. "
        f"Demographic parity difference {m['demographic_parity_difference']}, equal opportunity difference {m['equal_opportunity_difference']}, "
        f"disparate impact ratio {m['disparate_impact_ratio']}; highest selection rate in {m['highest_selection_cell']}, lowest in {m['lowest_selection_cell']}."
        + (
            f" 95% bootstrap interval: demographic parity difference {ci['demographic_parity_difference']}, equal opportunity difference {ci['equal_opportunity_difference']}."
            if ci
            else ""
        )
    )
    a("")
    a(
        "| Cell (sex, age band) | n | Selection rate (95% CI) | True-positive rate (95% CI) | Compared |"
    )
    a("|---|---|---|---|---|")
    for r in c["details"]:
        tpr = (
            "n/a"
            if r["true_positive_rate"] is None
            else f"{r['true_positive_rate']} ({r['tpr_ci95'][0]} to {r['tpr_ci95'][1]})"
        )
        a(
            f"| {r['cell']} | {r['n']} | {r['selection_rate']} ({r['selection_ci95'][0]} to {r['selection_ci95'][1]}) | {tpr} | {'yes' if r['included'] else 'no, too small'} |"
        )
    a("")


def markdown(inv: Inventory, gaps: list[SystemGap], as_of: date, evidence: dict | None) -> str:
    L: list[str] = []
    a = L.append
    a("# AI governance report")
    a("")
    a(f"As of {as_of.isoformat()}. {inv.disclaimer.strip()}")
    a("")
    a(f"> {DISCLAIMER}")
    a("")
    tc = _tier_counts(gaps)
    live = [g for g in gaps if g.system.status.value in ("production", "pilot")]
    a("## 1. Summary")
    a("")
    a(f"- Systems in register: {len(gaps)} ({len(live)} in production or pilot)")
    a("- Tiers: " + ", ".join(f"{t.value} {tc.get(t.value, 0)}" for t in Tier))
    a(f"- Systems using personal data: {sum(g.system.uses_personal_data for g in gaps)}")
    tot_gap = sum(len(g.gaps) for g in gaps)
    a(
        f"- Control gaps found by register checks: {tot_gap} across {sum(1 for g in gaps if g.gaps)} systems"
    )
    stale = [
        g.system.id
        for g in live
        if g.system.last_validation is None or (as_of - g.system.last_validation).days > 365
    ]
    a(
        f"- Live systems without validation in the last 12 months: {len(stale)} ({', '.join(stale) or 'none'})"
    )
    a("")
    a("## 2. Register")
    a("")
    a(
        "| ID | System | Owner | Status | Model | Deployment | Oversight | Personal data | Last validation | Incidents |"
    )
    a("|---|---|---|---|---|---|---|---|---|---|")
    for g in gaps:
        s = g.system
        a(
            f"| {s.id} | {s.name} | {s.owner} | {s.status.value} | {s.model_type} | {s.deployment.value} | {s.human_oversight.mode.value} | {'yes' if s.uses_personal_data else 'no'} | {s.last_validation or 'none'} | {len(s.incidents)} |"
        )
    a("")
    a("## 3. EU AI Act risk tiers")
    a("")
    a("| ID | Tier | References | Rationale |")
    a("|---|---|---|---|")
    for g in gaps:
        c = g.classification
        a(
            f"| {g.system.id} | {c.tier.value} | {', '.join(c.references) or 'none'} | {' '.join(c.rationale + c.notes)} |"
        )
    a("")
    a("Obligation articles to read for each tier (pointers only; read the Regulation for content):")
    a("")
    for g in gaps:
        c = g.classification
        if c.tier in (Tier.HIGH, Tier.LIMITED, Tier.PROHIBITED):
            a(f"- {g.system.id} ({c.tier.value}): " + "; ".join(c.obligations))
    a("")
    a(f"### Application dates as of {as_of.isoformat()}")
    a("")
    a(
        "Dates are from Art 113 of Regulation (EU) 2024/1689 as amended by Regulation (EU) 2026/1744 (in force 27 July 2026). A date shown with an earlier original date has been postponed by that amendment."
    )
    a("")
    a("| Obligation group | Applies from | Original date | Applies on the report date |")
    a("|---|---|---|---|")
    for o in sorted(load_timeline()[1], key=lambda o: o.current):
        a(
            f"| {o.title} | {o.current.isoformat()} | {o.original.isoformat() if o.original else 'new'} | {'yes' if o.applies_on(as_of) else 'no'} |"
        )
    a("")
    a(
        "| ID | Tier | Obligation groups that follow from the tier | Already applicable | Not yet applicable |"
    )
    a("|---|---|---|---|---|")
    for g in gaps:
        now = [x.obligation.id for x in g.obligations if x.applies]
        later = [
            f"{x.obligation.id} ({x.obligation.current.isoformat()})"
            for x in g.obligations
            if not x.applies
        ]
        a(
            f"| {g.system.id} | {g.classification.tier.value} | {len(g.obligations)} | {', '.join(now) or 'none'} | {', '.join(later) or 'none'} |"
        )
    a("")
    a("## 4. Control gap assessment")
    a("")
    a(
        "`met` = the register entry is consistent with the control. `gap` = a register check failed. `evidence requested` = no automatic check; a document must be supplied. `met` does not prove the control works."
    )
    a("")
    a("| ID | Tier | Controls applicable | Met | Gap | Evidence requested | Gaps |")
    a("|---|---|---|---|---|---|---|")
    for g in gaps:
        a(
            f"| {g.system.id} | {g.classification.tier.value} | {len(g.results)} | {g.count('met')} | {g.count('gap')} | {g.count('evidence requested')} | {', '.join(r.control.id for r in g.gaps) or 'none'} |"
        )
    a("")
    a("### Gap detail")
    a("")
    for g in gaps:
        if not g.gaps:
            continue
        a(f"{g.system.id} {g.system.name}")
        a("")
        for r in g.gaps:
            a(f"- {r.control.id} {r.control.title}: " + "; ".join(r.details))
        a("")
    a("### Evidence checklist per system")
    a("")
    for g in gaps:
        a(
            f"<details><summary>{g.system.id} {_esc(g.system.name)} ({len([r for r in g.results if r.status != 'met'])} open)</summary>"
        )
        a("")
        for r in g.results:
            if r.status == "met":
                continue
            box = "[ ]"
            a(
                f"- {box} {r.control.id} {r.control.title} ({r.status}): "
                + "; ".join(r.control.evidence)
            )
        a("")
        a("</details>")
        a("")
    a("### Control library coverage")
    a("")
    a("| Control | Title | EU AI Act | ISO/IEC 42001 theme | NIST AI RMF |")
    a("|---|---|---|---|---|")
    for c in load_controls():
        a(
            f"| {c.id} | {c.title} | {', '.join(c.eu) or '-'} | {'; '.join(c.iso42001)} | {', '.join(c.nist)} |"
        )
    a("")
    cov = nist_coverage()
    a(
        "NIST AI RMF function coverage: "
        + "; ".join(f"{k} {len(v)} controls" for k, v in cov.items())
    )
    a("")
    a("## 5. Technical evidence")
    a("")
    if evidence is None:
        a("Not yet generated. Run `ai-gov evidence` (downloads the UCI dataset once).")
    else:
        p = evidence["performance"]
        ci_txt = (
            f" (95% bootstrap interval {p['test_auc_ci95'][0]} to {p['test_auc_ci95'][1]})"
            if "test_auc_ci95" in p
            else ""
        )
        a(
            f"Dataset: {evidence['dataset']}. Seed {evidence['seed']}. Illustrative model, not one of the register systems."
        )
        a("")
        a(
            f"Model: {p['model']}. Train/validation/test {p['train_rows']}/{p['validation_rows']}/{p['test_rows']}; test AUC {p['test_auc']}{ci_txt}; default rate {p['default_rate']}; decision threshold {p['threshold_from_validation_f1']} (max F1 on validation); flag rate on test {p['flag_rate_test']}."
        )
        a("")
        a("| Check | Status | Key metrics |")
        a("|---|---|---|")
        for c in evidence["checks"]:
            m = c["metrics"]
            keys = [k for k, v in m.items() if not isinstance(v, (dict, list))]
            a(f"| {c['check']} | {c['status']} | " + ", ".join(f"{k} {m[k]}" for k in keys) + " |")
        a("")
        for c in evidence["checks"]:
            if c["check"].startswith("fairness: intersectional"):
                _intersectional(a, c)
            elif c["check"].startswith("fairness"):
                m = c["metrics"]
                ci = m.get("ci95", {})
                a(
                    f"- {c['check']}: selection rate {m['selection_rate']}, true-positive rate {m['true_positive_rate']}"
                    + (
                        f"; 95% bootstrap interval: demographic parity difference {ci['demographic_parity_difference']}, equal opportunity difference {ci['equal_opportunity_difference']}, disparate impact ratio {ci['disparate_impact_ratio']}"
                        if ci
                        else ""
                    )
                )
            if c["check"].startswith("data_documentation") and c["details"]:
                a(
                    "- Values outside the documented domain: "
                    + "; ".join(
                        f"{d['column']} {d['undocumented_values']} ({d['share']:.1%} of rows)"
                        for d in c["details"]
                    )
                )
        a("")
        for c in evidence["checks"]:
            a(f"- {c['check']}: {c['note']}")
    a("")
    a("## 6. Incident lessons")
    a("")
    a(
        f"Failure-mode categories mapped to the controls that would be expected to catch them. Source for incident counts: [AI Incident Database]({AIID_URL}) snapshots; the database's licence excludes report text, so this repo stores no incident text, only the author's category mapping. No incident counts are shown: {INCIDENT_STATUS}"
    )
    a("")
    a("| Category | Controls expected to catch it | Why |")
    a("|---|---|---|")
    for c in load_categories():
        a(f"| {c.name} | {', '.join(c.controls)} | {c.why} |")
    a("")
    a("## 7. Sources and limits")
    a("")
    for n, u, lic in SOURCES:
        a(f"- [{n}]({u}): {lic}")
    a("")
    a(
        "Limits: register checks read declared facts, not live systems; 'met' is not an opinion on effectiveness; the tier is a screening result; examples are invented."
    )
    a("")
    a("By Utku Fidan · utkufidan.com")
    a("")
    return "\n".join(L)


def html_register(inv: Inventory, gaps: list[SystemGap], as_of: date) -> str:
    rows = []
    for g in gaps:
        s, c = g.system, g.classification
        cls = {
            "prohibited": "bad",
            "high-risk": "high",
            "limited-risk (transparency)": "lim",
            "minimal": "min",
        }[c.tier.value]
        rows.append(
            f"<tr><td>{_esc(s.id)}</td><td><strong>{_esc(s.name)}</strong><br><small>{_esc(s.purpose)}</small></td>"
            f"<td>{_esc(s.owner)}</td><td>{_esc(s.status.value)}</td><td>{_esc(s.model_type)}<br><small>{_esc(s.provenance.value)} · {_esc(s.deployment.value)}</small></td>"
            f"<td><span class='tier {cls}'>{_esc(c.tier.value)}</span><br><small>{_esc(', '.join(c.references))}</small></td>"
            f"<td>{_esc(s.human_oversight.mode.value)}</td><td>{'yes' if s.uses_personal_data else 'no'}</td>"
            f"<td>{_esc(s.last_validation or 'none')}</td><td>{len(g.gaps)}</td></tr>"
        )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI system register (illustrative)</title>
<style>
:root{{--bg:#fff;--fg:#1b1f24;--mute:#59636e;--line:#d0d7de;--head:#f6f8fa;--bad:#a40e26;--high:#bc4c00;--lim:#9a6700;--min:#1a7f37}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0d1117;--fg:#e6edf3;--mute:#9198a1;--line:#30363d;--head:#161b22;--bad:#ff7b72;--high:#ffa657;--lim:#e3b341;--min:#56d364}}}}
body{{margin:0;padding:24px 16px;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
main{{max-width:1200px;margin:auto}} h1{{font-size:1.4rem;margin:0 0 4px}} p.sub{{color:var(--mute);margin:0 0 16px}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;min-width:900px}}
th,td{{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}} th{{background:var(--head)}}
small{{color:var(--mute)}} .tier{{font-weight:600}} .bad{{color:var(--bad)}} .high{{color:var(--high)}} .lim{{color:var(--lim)}} .min{{color:var(--min)}}
footer{{margin-top:24px;color:var(--mute)}}
</style></head><body><main>
<h1>AI system register</h1>
<p class="sub">Illustrative data, as of {as_of.isoformat()}. Screening only, not legal advice.</p>
<div class="wrap"><table><thead><tr><th>ID</th><th>System</th><th>Owner</th><th>Status</th><th>Model</th><th>EU AI Act tier</th><th>Oversight</th><th>Personal data</th><th>Last validation</th><th>Gaps</th></tr></thead>
<tbody>
{chr(10).join(rows)}
</tbody></table></div>
<footer>By Utku Fidan · utkufidan.com</footer>
</main></body></html>
"""
