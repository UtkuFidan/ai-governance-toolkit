from datetime import date

import pytest

from ai_gov.classify import classify_answers
from ai_gov.cli import main
from ai_gov.gap import assess
from ai_gov.schema import Questionnaire, load_inventory
from ai_gov.timeline import applicable_on, load_timeline, obligation, obligation_ids, status_for


def test_original_dates_match_article_113():
    assert obligation("prohibitions").original == date(2025, 2, 2)
    assert obligation("gpai").original == date(2025, 8, 2)
    assert obligation("high_risk_annex_iii").original == date(2026, 8, 2)
    assert obligation("high_risk_annex_i").original == date(2027, 8, 2)


def test_omnibus_amendments_are_applied():
    assert obligation("high_risk_annex_iii").current == date(2027, 12, 2)
    assert obligation("high_risk_annex_i").current == date(2028, 8, 2)
    assert obligation("transparency_marking_legacy").current == date(2026, 12, 2)
    assert obligation("high_risk_annex_iii").postponed
    assert not obligation("prohibitions").postponed
    assert obligation("transparency").current == date(2026, 8, 2)  # Art 50 was not deferred


def test_every_current_date_is_not_before_the_original():
    for o in load_timeline()[1]:
        assert o.original is None or o.current >= o.original


def test_applicable_on_changes_with_the_date():
    ids = lambda d: {o.id for o in applicable_on(d)}  # noqa: E731
    assert ids(date(2025, 3, 1)) == {"prohibitions", "ai_literacy"}
    assert "gpai" in ids(date(2025, 9, 1)) and "transparency" not in ids(date(2025, 9, 1))
    now = ids(date(2026, 10, 28))
    assert "transparency" in now and "high_risk_annex_iii" not in now
    assert "high_risk_annex_iii" in ids(date(2027, 12, 2))
    assert "high_risk_annex_i" not in ids(date(2028, 8, 1))
    assert "high_risk_annex_i" in ids(date(2028, 8, 2))


def test_obligation_groups_follow_the_tier():
    base = Questionnaire()
    assert obligation_ids(classify_answers("x", base)) == ["ai_literacy"]
    credit = classify_answers("x", Questionnaire(annex_iii_use_case="5(b)"))
    assert "high_risk_annex_iii" in obligation_ids(credit)
    annex_i = classify_answers(
        "x",
        Questionnaire(
            safety_component_of_annex_i_product=True,
            third_party_conformity_assessment_required=True,
        ),
    )
    assert "high_risk_annex_i" in obligation_ids(annex_i)
    assert "high_risk_annex_iii" not in obligation_ids(annex_i)
    social = classify_answers("x", Questionnaire(social_scoring=True))
    assert "prohibitions" in obligation_ids(social)
    chat = classify_answers("x", Questionnaire(interacts_directly_with_natural_persons=True))
    assert "transparency" in obligation_ids(chat)


def test_register_shows_what_applies_on_the_date():
    inv = load_inventory()
    credit = next(
        g
        for g in assess(inv, date(2026, 10, 28))
        if g.classification.references and "Annex III 5(b)" in g.classification.references
    )
    early = {
        s.obligation.id: s.applies for s in status_for(credit.classification, date(2026, 10, 28))
    }
    late = {
        s.obligation.id: s.applies for s in status_for(credit.classification, date(2027, 12, 2))
    }
    assert early["high_risk_annex_iii"] is False and late["high_risk_annex_iii"] is True
    assert early["ai_literacy"] is True


def test_cli_timeline(capsys):
    assert main(["timeline", "--as-of", "2026-10-28"]) == 0
    out = capsys.readouterr().out
    assert "not yet" in out and "2027-12-02" in out and "was 2026-08-02" in out


def test_asof_flows_into_the_report(tmp_path):
    assert main(["report", "--as-of", "2027-12-02", "--out-dir", str(tmp_path)]) == 0
    md = (tmp_path / "ai_governance_report.md").read_text()
    assert "Application dates as of 2027-12-02" in md
    row = next(r for r in md.splitlines() if r.startswith("| High-risk systems under Annex III"))
    assert row.endswith("| yes |")
    assert pytest is not None
