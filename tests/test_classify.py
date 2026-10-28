import pytest

from ai_gov.classify import Tier, classify, classify_answers
from ai_gov.schema import Questionnaire, load_inventory


def q(**kw):
    return Questionnaire(**kw)


def cl(**kw):
    return classify_answers("T", q(**kw))


def test_default_is_minimal():
    c = cl()
    assert c.tier is Tier.MINIMAL
    assert c.obligation_articles == ["4"]


@pytest.mark.parametrize(
    "flag,ref",
    [
        ("subliminal_or_deceptive_manipulation", "Art 5(1)(a)"),
        ("exploits_vulnerabilities", "Art 5(1)(b)"),
        ("social_scoring", "Art 5(1)(c)"),
        ("crime_risk_by_profiling_only", "Art 5(1)(d)"),
        ("untargeted_face_scraping", "Art 5(1)(e)"),
        ("emotion_inference_work_or_education", "Art 5(1)(f)"),
        ("biometric_categorisation_sensitive", "Art 5(1)(g)"),
        ("realtime_remote_biometric_id_law_enforcement", "Art 5(1)(h)"),
    ],
)
def test_each_prohibited_practice(flag, ref):
    c = cl(**{flag: True})
    assert c.tier is Tier.PROHIBITED
    assert ref in c.references


def test_prohibited_beats_high_risk():
    c = cl(social_scoring=True, annex_iii_use_case="5(b)")
    assert c.tier is Tier.PROHIBITED


def test_rbi_exception_note():
    c = cl(realtime_remote_biometric_id_law_enforcement=True)
    assert any("exceptions" in n for n in c.notes)


def test_creditworthiness_is_high_risk():
    c = cl(annex_iii_use_case="5(b)", performs_profiling_of_natural_persons=True)
    assert c.tier is Tier.HIGH
    assert "Annex III 5(b)" in c.references
    assert "27" in c.obligation_articles  # Art 27(1) names points 5(b) and (c)


def test_fraud_detection_carve_out():
    c = cl(annex_iii_use_case="5(b)", used_only_for_fraud_detection=True)
    assert c.tier is Tier.MINIMAL
    assert any("fraud" in n for n in c.notes)


def test_life_health_insurance_high_but_not_other_insurance():
    assert cl(annex_iii_use_case="5(c)").tier is Tier.HIGH
    assert cl(performs_profiling_of_natural_persons=True).tier is Tier.MINIMAL  # e.g. motor pricing


def test_art6_3_derogation_applies_without_profiling():
    c = cl(annex_iii_use_case="4(a)", narrow_procedural_task=True)
    assert c.tier is Tier.MINIMAL
    assert any("Art 6(4)" in n for n in c.notes)


def test_art6_3_derogation_void_with_profiling():
    c = cl(
        annex_iii_use_case="4(a)", preparatory_task_only=True,
        performs_profiling_of_natural_persons=True,
    )  # fmt: skip
    assert c.tier is Tier.HIGH
    assert "Art 6(3)" in c.references


def test_unknown_annex_point_rejected():
    with pytest.raises(ValueError):
        cl(annex_iii_use_case="9(z)")


def test_annex_i_needs_both_conditions():
    only_safety = cl(safety_component_of_annex_i_product=True)
    assert only_safety.tier is Tier.MINIMAL
    both = cl(
        safety_component_of_annex_i_product=True,
        third_party_conformity_assessment_required=True,
    )  # fmt: skip
    assert both.tier is Tier.HIGH
    assert any("2 August 2028" in n for n in both.notes)


def test_transparency_limited():
    c = cl(interacts_directly_with_natural_persons=True)
    assert c.tier is Tier.LIMITED
    assert "Art 50" in c.references
    assert any("obvious" in n for n in c.notes)


@pytest.mark.parametrize(
    "flag",
    [
        "generates_synthetic_content",
        "emotion_recognition_or_biometric_categorisation",
        "generates_deepfake_content",
    ],
)
def test_other_transparency_triggers(flag):
    assert cl(**{flag: True}).tier is Tier.LIMITED


def test_high_risk_also_notes_transparency():
    c = cl(annex_iii_use_case="4(a)", generates_synthetic_content=True)
    assert c.tier is Tier.HIGH
    assert any("Art 50" in n for n in c.notes)


def test_role_changes_obligations():
    dep = cl(annex_iii_use_case="4(a)", role="deployer")
    prov = cl(annex_iii_use_case="4(a)", role="provider")
    assert "26" in dep.obligation_articles and "9" not in dep.obligation_articles
    assert "9" in prov.obligation_articles and "26" not in prov.obligation_articles
    assert "27" not in dep.obligation_articles  # 4(a) is not named in Art 27(1)


def test_example_inventory_tiers():
    tiers = {s.id: classify(s).tier for s in load_inventory().systems}
    assert tiers["AI-001"] is Tier.MINIMAL  # fraud carve-out
    assert tiers["AI-002"] is Tier.HIGH
    assert tiers["AI-005"] is Tier.LIMITED
    assert tiers["AI-009"] is Tier.HIGH
    assert tiers["AI-012"] is Tier.PROHIBITED
