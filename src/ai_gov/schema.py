"""Inventory schema (pydantic v2). Every example entry is illustrative, not a real system."""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class DataCategory(StrEnum):
    TRANSACTIONAL = "transactional"
    CUSTOMER_PROFILE = "customer_profile"
    PERSONAL_IDENTIFIERS = "personal_identifiers"
    FINANCIAL_PERSONAL = "financial_personal"
    SPECIAL_CATEGORY = "special_category"
    PUBLIC_TEXT = "public_text"
    INTERNAL_DOCUMENTS = "internal_documents"
    SENSOR_TELEMETRY = "sensor_telemetry"
    SYNTHETIC = "synthetic"


PERSONAL_CATEGORIES = {
    DataCategory.CUSTOMER_PROFILE,
    DataCategory.PERSONAL_IDENTIFIERS,
    DataCategory.FINANCIAL_PERSONAL,
    DataCategory.SPECIAL_CATEGORY,
}


class Provenance(StrEnum):
    IN_HOUSE = "in_house"
    OPEN_SOURCE = "open_source"
    VENDOR = "vendor"


class Deployment(StrEnum):
    ON_PREM = "on_prem"
    LOCAL_WORKSTATION = "local_workstation"
    PRIVATE_CLOUD = "private_cloud"
    PUBLIC_CLOUD = "public_cloud"
    VENDOR_SAAS = "vendor_saas"


class OversightMode(StrEnum):
    NONE = "none"
    POST_HOC = "post_hoc_sampling"
    ON_THE_LOOP = "human_on_the_loop"
    IN_THE_LOOP = "human_in_the_loop"


class Status(StrEnum):
    PROPOSED = "proposed"
    PILOT = "pilot"
    PRODUCTION = "production"
    RETIRED = "retired"
    REJECTED = "rejected"


class Role(StrEnum):
    PROVIDER = "provider"
    DEPLOYER = "deployer"
    BOTH = "provider_and_deployer"


class Oversight(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: OversightMode
    description: str = ""
    can_override: bool = False


class Monitoring(BaseModel):
    model_config = ConfigDict(extra="forbid")
    frequency: str = Field(description="e.g. monthly, quarterly, none")
    metrics: list[str] = Field(default_factory=list)
    thresholds_defined: bool = False
    last_review: date | None = None


class Incident(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date: date
    severity: str = Field(pattern="^(low|medium|high)$")
    summary: str
    resolved: bool = True


class Questionnaire(BaseModel):
    """Answers for the EU AI Act triage. Defaults mean 'no'."""

    model_config = ConfigDict(extra="forbid")
    # Article 5(1) practices
    subliminal_or_deceptive_manipulation: bool = False  # 5(1)(a)
    exploits_vulnerabilities: bool = False  # 5(1)(b)
    social_scoring: bool = False  # 5(1)(c)
    crime_risk_by_profiling_only: bool = False  # 5(1)(d)
    untargeted_face_scraping: bool = False  # 5(1)(e)
    emotion_inference_work_or_education: bool = False  # 5(1)(f)
    biometric_categorisation_sensitive: bool = False  # 5(1)(g)
    realtime_remote_biometric_id_law_enforcement: bool = False  # 5(1)(h)
    # Article 6(1) / Annex I
    safety_component_of_annex_i_product: bool = False
    third_party_conformity_assessment_required: bool = False
    # Article 6(2) / Annex III, e.g. "5(b)"; empty when no Annex III use case applies
    annex_iii_use_case: str = ""
    used_only_for_fraud_detection: bool = False  # carve-out in Annex III point 5(b)
    performs_profiling_of_natural_persons: bool = False  # Art 6(3), last subparagraph
    # Art 6(3) derogation conditions (a) to (d), only relevant with an Annex III use case
    narrow_procedural_task: bool = False
    improves_prior_human_activity: bool = False
    detects_patterns_without_replacing_human_review: bool = False
    preparatory_task_only: bool = False
    # Article 50 transparency
    interacts_directly_with_natural_persons: bool = False
    generates_synthetic_content: bool = False
    emotion_recognition_or_biometric_categorisation: bool = False
    generates_deepfake_content: bool = False
    # Role under the Regulation
    role: Role = Role.DEPLOYER


class AISystem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(pattern=r"^AI-\d{3}$")
    name: str
    illustrative: bool = True
    status: Status
    owner: str = Field(description="Accountable role, never a named person")
    purpose: str
    users: list[str] = Field(min_length=1)
    affected_persons: str = ""
    data_categories: list[DataCategory] = Field(min_length=1)
    model_type: str
    provenance: Provenance
    vendor_or_source: str = ""
    deployment: Deployment
    human_oversight: Oversight
    monitoring: Monitoring
    last_validation: date | None = None
    independent_validation: bool = False
    documentation: list[str] = Field(default_factory=list)
    incidents: list[Incident] = Field(default_factory=list)
    questionnaire: Questionnaire = Field(default_factory=Questionnaire)
    related_project: str = ""

    @property
    def uses_personal_data(self) -> bool:
        return any(c in PERSONAL_CATEGORIES for c in self.data_categories)

    @model_validator(mode="after")
    def _consistency(self) -> AISystem:
        if self.provenance is Provenance.VENDOR and not self.vendor_or_source:
            raise ValueError("vendor systems need vendor_or_source")
        if self.status is Status.REJECTED and self.incidents:
            raise ValueError("rejected systems cannot have incidents")
        return self


class Inventory(BaseModel):
    model_config = ConfigDict(extra="forbid")
    disclaimer: str
    systems: list[AISystem]

    @model_validator(mode="after")
    def _unique_ids(self) -> Inventory:
        ids = [s.id for s in self.systems]
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            raise ValueError(f"duplicate ids: {sorted(dup)}")
        return self


DEFAULT_INVENTORY = Path(__file__).parent / "data" / "inventory.yaml"


def load_inventory(path: Path | str | None = None) -> Inventory:
    p = Path(path) if path else DEFAULT_INVENTORY
    return Inventory.model_validate(yaml.safe_load(p.read_text()))


def json_schema() -> dict:
    return Inventory.model_json_schema()
