import json
from datetime import date

from ai_gov.cli import main
from ai_gov.controls import load_controls, nist_coverage
from ai_gov.gap import assess
from ai_gov.incidents import count_snapshot, load_categories
from ai_gov.schema import load_inventory

ASOF = date(2026, 10, 28)


def by_id():
    return {g.system.id: g for g in assess(load_inventory(), ASOF)}


def test_control_library_maps_to_all_frameworks():
    cs = load_controls()
    assert len({c.id for c in cs}) == len(cs)
    assert set(nist_coverage()) == {"GOVERN", "MAP", "MEASURE", "MANAGE"}
    assert all(v for v in nist_coverage().values())
    assert all(c.iso42001 and c.nist for c in cs)


def test_stale_validation_is_a_gap():
    g = by_id()["AI-002"]  # validated 2025-06-30
    assert "VAL-01" in {r.control.id for r in g.gaps}


def test_recent_validation_is_not_a_gap():
    assert "VAL-01" not in {r.control.id for r in by_id()["AI-001"].gaps}


def test_vendor_system_has_vendor_and_incident_gaps():
    ids = {r.control.id for r in by_id()["AI-010"].gaps}
    assert {"THP-01", "INC-01", "HUM-01", "VAL-01"} <= ids


def test_rejected_prohibited_proposal_is_met_not_gap():
    g = by_id()["AI-012"]
    assert g.count("gap") == 0 and g.count("met") == 1


def test_high_risk_gets_more_controls_than_minimal():
    g = by_id()
    assert len(g["AI-002"].results) > len(g["AI-007"].results)


def test_every_control_check_exists():
    from ai_gov.gap import CHECKS

    assert {k for c in load_controls() for k in c.checks} <= set(CHECKS)


def test_incident_categories_reference_real_controls():
    ids = {c.id for c in load_controls()}
    for cat in load_categories():
        assert set(cat.controls) <= ids


def test_snapshot_counts_keep_no_text(tmp_path):
    f = tmp_path / "incidents.csv"
    f.write_text(
        "incident_id,title,description\n"
        "1,Chatbot hallucinated policy,secret narrative text\n"
        "2,Hiring tool shows gender bias,more text\n"
        "3,Unrelated item,nothing\n"
    )
    res = count_snapshot(f)
    assert res["incidents_in_snapshot"] == 3 and res["unmatched"] == 1
    assert res["by_category"]["bias"]["count"] == 1
    assert res["by_category"]["genai_error"]["example_links"] == [
        "https://incidentdatabase.ai/cite/1/"
    ]
    assert "secret narrative" not in json.dumps(res)


def test_report_end_to_end(tmp_path, capsys):
    ev = tmp_path / "evidence_results.json"
    ev.write_text(
        json.dumps(
            {
                "dataset": "test",
                "seed": 1,
                "performance": {
                    "model": "m",
                    "train_rows": 1,
                    "validation_rows": 1,
                    "test_rows": 1,
                    "test_auc": 0.7,
                    "default_rate": 0.2,
                    "threshold_from_validation_f1": 0.3,
                    "flag_rate_test": 0.2,
                },
                "checks": [
                    {
                        "check": "fairness: X",
                        "status": "pass",
                        "metrics": {
                            "selection_rate": {},
                            "true_positive_rate": {},
                            "demographic_parity_difference": 0.01,
                        },
                        "thresholds": {},
                        "note": "n",
                        "details": [],
                    }
                ],
            }
        )
    )
    assert main(["report", "--as-of", "2026-10-28", "--out-dir", str(tmp_path)]) == 0
    md = (tmp_path / "ai_governance_report.md").read_text()
    for h in [
        "## 2. Register",
        "## 3. EU AI Act risk tiers",
        "## 4. Control gap",
        "## 5. Technical evidence",
        "Application dates as of",
        "By Utku Fidan · utkufidan.com",
    ]:
        assert h in md
    assert "not legal advice" in md.lower()
    html = (tmp_path / "register.html").read_text()
    assert "AI-012" in html and "illustrative" in html.lower()


def test_cli_classify_and_gap_run(capsys):
    assert main(["classify", "-v"]) == 0
    assert main(["gap", "--as-of", "2026-10-28"]) == 0
    out = capsys.readouterr().out
    assert "not legal advice" in out.lower() and "AI-010" in out
