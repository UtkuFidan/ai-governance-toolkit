"""Rules-based EU AI Act triage. Reference text: Regulation (EU) 2024/1689.

This is a screening aid for an internal register. It is NOT legal advice and does not replace
a legal assessment. Article numbers follow the official text of Regulation (EU) 2024/1689
(CELEX 32024R1689), as amended by Regulation (EU) 2026/1744. Obligations listed are only pointers
to articles; this module does not paraphrase their content beyond the article title.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from .schema import AISystem, Questionnaire, Role

DISCLAIMER = (
    "Screening aid, not legal advice. Classification depends on facts and on the final "
    "legal reading of Regulation (EU) 2024/1689 and later amendments or guidelines; "
    "have counsel confirm any tier that matters."
)


class Tier(StrEnum):
    PROHIBITED = "prohibited"
    HIGH = "high-risk"
    LIMITED = "limited-risk (transparency)"
    MINIMAL = "minimal"

    @property
    def rank(self) -> int:
        return list(Tier).index(self)


ARTICLE_TITLES = {
    "4": "AI literacy",
    "5": "Prohibited AI practices",
    "6": "Classification rules for high-risk AI systems",
    "9": "Risk management system",
    "10": "Data and data governance",
    "11": "Technical documentation",
    "12": "Record-keeping",
    "13": "Transparency and provision of information to deployers",
    "14": "Human oversight",
    "15": "Accuracy, robustness and cybersecurity",
    "16": "Obligations of providers of high-risk AI systems",
    "17": "Quality management system",
    "26": "Obligations of deployers of high-risk AI systems",
    "27": "Fundamental rights impact assessment for high-risk AI systems",
    "43": "Conformity assessment",
    "49": "Registration",
    "50": "Transparency obligations for providers and deployers of certain AI systems",
    "72": "Post-market monitoring by providers and post-market monitoring plan",
    "73": "Reporting of serious incidents",
    "86": "Right to explanation of individual decision-making",
}

# Annex III points (short labels; see the Regulation for the full wording).
ANNEX_III = {
    "1(a)": "Remote biometric identification",
    "1(b)": "Biometric categorisation by sensitive or protected attributes",
    "1(c)": "Emotion recognition",
    "2": "Safety components of critical infrastructure (digital, road traffic, water, gas, heating, electricity)",
    "3(a)": "Education: access, admission or assignment",
    "3(b)": "Education: evaluation of learning outcomes",
    "3(c)": "Education: assessing the appropriate level of education",
    "3(d)": "Education: monitoring prohibited behaviour during tests",
    "4(a)": "Employment: recruitment or selection",
    "4(b)": "Employment: decisions on work terms, promotion, termination, task allocation, monitoring",
    "5(a)": "Public assistance benefits and services: eligibility",
    "5(b)": "Creditworthiness of natural persons or credit scoring (fraud detection excepted)",
    "5(c)": "Risk assessment and pricing for natural persons in life and health insurance",
    "5(d)": "Emergency calls, dispatch and triage",
    "6(a)": "Law enforcement: risk of becoming a victim",
    "6(b)": "Law enforcement: polygraphs or similar",
    "6(c)": "Law enforcement: reliability of evidence",
    "6(d)": "Law enforcement: risk of offending or re-offending",
    "6(e)": "Law enforcement: profiling in criminal investigations",
    "7(a)": "Migration and border control: polygraphs or similar",
    "7(b)": "Migration and border control: risk assessment",
    "7(c)": "Migration and border control: examination of asylum, visa or residence applications",
    "7(d)": "Migration and border control: detection, recognition or identification of persons",
    "8(a)": "Administration of justice: assisting a judicial authority",
    "8(b)": "Democratic processes: influencing elections or referenda",
}

PROHIBITED_FLAGS = {
    "subliminal_or_deceptive_manipulation": (
        "5(1)(a)",
        "subliminal or purposefully manipulative or deceptive techniques",
    ),
    "exploits_vulnerabilities": (
        "5(1)(b)",
        "exploitation of vulnerabilities due to age, disability or social or economic situation",
    ),
    "social_scoring": ("5(1)(c)", "social scoring leading to detrimental treatment"),
    "crime_risk_by_profiling_only": (
        "5(1)(d)",
        "criminal-offence risk assessment based solely on profiling or personality traits",
    ),
    "untargeted_face_scraping": (
        "5(1)(e)",
        "untargeted scraping of facial images to build recognition databases",
    ),
    "emotion_inference_work_or_education": (
        "5(1)(f)",
        "emotion inference in the workplace or education",
    ),
    "biometric_categorisation_sensitive": (
        "5(1)(g)",
        "biometric categorisation to infer sensitive characteristics",
    ),
    "realtime_remote_biometric_id_law_enforcement": (
        "5(1)(h)",
        "real-time remote biometric identification in public spaces for law enforcement",
    ),
}

PROVIDER_HIGH_RISK = [
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "43",
    "49",
    "72",
    "73",
]
DEPLOYER_HIGH_RISK = ["26", "86"]


@dataclass
class Classification:
    system_id: str
    tier: Tier
    references: list[str]
    rationale: list[str]
    obligation_articles: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def obligations(self) -> list[str]:
        return [
            f"Art {a}: {ARTICLE_TITLES.get(a, '')}".rstrip(": ") for a in self.obligation_articles
        ]


def _high_obligations(q: Questionnaire) -> list[str]:
    arts: list[str] = []
    if q.role in (Role.PROVIDER, Role.BOTH):
        arts += PROVIDER_HIGH_RISK
    if q.role in (Role.DEPLOYER, Role.BOTH):
        arts += DEPLOYER_HIGH_RISK
        if q.annex_iii_use_case in ("5(b)", "5(c)"):
            arts.append("27")  # Art 27(1) names Annex III points 5(b) and (c)
    return sorted(set(arts), key=int)


def classify_answers(system_id: str, q: Questionnaire) -> Classification:
    """Apply the rules in order: Art 5, Art 6(1), Art 6(2)/(3) with Annex III, Art 50, minimal."""
    # 1. Prohibited practices (Art 5(1))
    hits = [(ref, why) for flag, (ref, why) in PROHIBITED_FLAGS.items() if getattr(q, flag)]
    if hits:
        notes = []
        if q.realtime_remote_biometric_id_law_enforcement:
            notes.append(
                "Art 5(1)(h) contains narrow exceptions (objectives (i) to (iii) and Art 5(2) to (7)); check whether one applies."
            )
        return Classification(
            system_id,
            Tier.PROHIBITED,
            [f"Art {r}" for r, _ in hits],
            [f"Answers indicate {why} (Art {r})." for r, why in hits],
            ["5"],
            notes,
        )

    refs: list[str] = []
    why: list[str] = []
    notes: list[str] = []
    high = False

    # 2. Art 6(1): safety component / product under Annex I legislation
    if q.safety_component_of_annex_i_product and q.third_party_conformity_assessment_required:
        high = True
        refs.append("Art 6(1)")
        why.append(
            "Safety component of (or itself) a product under Annex I legislation that needs third-party conformity assessment (Art 6(1)(a) and (b))."
        )
        notes.append(
            "Art 113(c): Art 6(1) and its obligations apply from 2 August 2028 (originally 2 August 2027; moved by Regulation (EU) 2026/1744)."
        )
    elif q.safety_component_of_annex_i_product:
        notes.append(
            "Annex I safety component without a third-party conformity assessment requirement: Art 6(1)(b) not met."
        )

    # 3. Art 6(2) / Annex III with the Art 6(3) derogation
    uc = q.annex_iii_use_case.strip()
    if uc:
        if uc not in ANNEX_III:
            raise ValueError(f"unknown Annex III point {uc!r}; known: {sorted(ANNEX_III)}")
        label = ANNEX_III[uc]
        if uc == "5(b)" and q.used_only_for_fraud_detection:
            refs.append("Annex III 5(b) fraud carve-out")
            notes.append(
                "Annex III 5(b) excludes AI systems used for the purpose of detecting financial fraud; this route to high-risk does not apply."
            )
        else:
            derog = [
                n
                for n, f in [
                    ("(a) narrow procedural task", q.narrow_procedural_task),
                    (
                        "(b) improves the result of a completed human activity",
                        q.improves_prior_human_activity,
                    ),
                    (
                        "(c) detects decision patterns without replacing human review",
                        q.detects_patterns_without_replacing_human_review,
                    ),
                    ("(d) preparatory task", q.preparatory_task_only),
                ]
                if f
            ]
            if derog and q.performs_profiling_of_natural_persons:
                high = True
                refs += [f"Annex III {uc}", "Art 6(2)", "Art 6(3)"]
                why.append(
                    f"Annex III {uc} ({label}). Art 6(3) derogation conditions claimed ({'; '.join(derog)}) but the system profiles natural persons, so it is always high-risk (Art 6(3), last subparagraph)."
                )
            elif derog:
                refs += [f"Annex III {uc}", "Art 6(3)", "Art 6(4)"]
                notes.append(
                    f"Annex III {uc} ({label}) matches, but Art 6(3) derogation claimed: {'; '.join(derog)}. Not high-risk only if it poses no significant risk of harm; the assessment must be documented (Art 6(4)) and registered (Art 49(2))."
                )
            else:
                high = True
                refs += [f"Annex III {uc}", "Art 6(2)"]
                why.append(f"Annex III point {uc}: {label}.")

    if high:
        extra = _transparency(q)
        if extra:
            notes.append("Also within Art 50 transparency: " + "; ".join(extra))
        return Classification(
            system_id, Tier.HIGH, sorted(set(refs)), why, _high_obligations(q), notes
        )

    # 4. Art 50 transparency
    tr = _transparency(q)
    if tr:
        if q.interacts_directly_with_natural_persons:
            notes.append(
                "Art 50(1) has an exception where the AI interaction is obvious to a reasonably well-informed person; check context."
            )
        return Classification(
            system_id,
            Tier.LIMITED,
            sorted({*refs, "Art 50"}),
            [f"Transparency duty indicated: {t}." for t in tr],
            ["50"],
            notes,
        )

    # 5. Minimal: nothing above applies
    why = [
        "No Art 5 practice, Art 6 high-risk route or Art 50 transparency trigger was indicated by the answers."
    ]
    return Classification(
        system_id,
        Tier.MINIMAL,
        refs,
        why,
        ["4"],
        notes + ["Art 4 (AI literacy) applies to providers and deployers of AI systems generally."],
    )


def _transparency(q: Questionnaire) -> list[str]:
    out = []
    if q.interacts_directly_with_natural_persons:
        out.append("system interacts directly with natural persons (Art 50(1))")
    if q.generates_synthetic_content:
        out.append("system generates synthetic audio, image, video or text (Art 50(2))")
    if q.emotion_recognition_or_biometric_categorisation:
        out.append("emotion recognition or biometric categorisation (Art 50(3))")
    if q.generates_deepfake_content:
        out.append("deep-fake content (Art 50(4))")
    return out


def classify(system: AISystem) -> Classification:
    c = classify_answers(system.id, system.questionnaire)
    if not system.uses_personal_data:
        c.notes.append("No personal-data category recorded.")
    return c
