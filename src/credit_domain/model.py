"""Executable encoding of CRD-DATA-004 / DOMAIN_MODEL.md.

Construction and mapping raise SemanticCollapseError instead of coercing
legal entity ↔ person, bank inflow ↔ tax turnover, bureau ↔ exposure,
or recommendation ↔ human decision.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Union


class SemanticCollapseError(ValueError):
    """Raised when a construction or mapping would collapse distinct types."""


class PartyKind(str, Enum):
    LEGAL_ENTITY = "LEGAL_ENTITY"
    SOLE_TRADER_BUSINESS = "SOLE_TRADER_BUSINESS"
    NATURAL_PERSON = "NATURAL_PERSON"


class MeasureKind(str, Enum):
    BANK_INFLOWS_12M = "BANK_INFLOWS_12M"
    BANK_OUTFLOWS_12M = "BANK_OUTFLOWS_12M"
    TAX_DECLARED_TURNOVER = "TAX_DECLARED_TURNOVER"
    STATEMENT_RECOGNIZED_REVENUE = "STATEMENT_RECOGNIZED_REVENUE"
    INTERNAL_EXISTING_EXPOSURE = "INTERNAL_EXISTING_EXPOSURE"
    INTERNAL_APPROVED_LIMIT = "INTERNAL_APPROVED_LIMIT"
    INTERNAL_PAST_DUE = "INTERNAL_PAST_DUE"


FORBIDDEN_MEASURE_ALIASES = frozenset({"revenue", "turnover", "income", "sales"})

PARTY_TYPE_MAP = {
    "ORGANIZATION": PartyKind.LEGAL_ENTITY,
    "SOLE_TRADER_BUSINESS": PartyKind.SOLE_TRADER_BUSINESS,
    "NATURAL_PERSON_OWNER": PartyKind.NATURAL_PERSON,
    "NATURAL_PERSON_GUARANTOR": PartyKind.NATURAL_PERSON,
}


class ResolutionState(str, Enum):
    MATCHED = "MATCHED"
    AMBIGUOUS = "AMBIGUOUS"
    UNRESOLVED = "UNRESOLVED"


class ExceptionClass(str, Enum):
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    POLICY_EXCEPTION = "POLICY_EXCEPTION"
    IDENTITY = "IDENTITY"
    FINANCIAL_CONFLICT = "FINANCIAL_CONFLICT"
    FRESHNESS = "FRESHNESS"
    ADVERSE = "ADVERSE"


class RecommendationStance(str, Enum):
    PROPOSE_APPROVE = "PROPOSE_APPROVE"
    PROPOSE_DECLINE = "PROPOSE_DECLINE"
    PROPOSE_CONDITION = "PROPOSE_CONDITION"
    REFER = "REFER"
    ABSTAIN = "ABSTAIN"


class DecisionOutcome(str, Enum):
    APPROVE = "APPROVE"
    DECLINE = "DECLINE"
    CONDITION = "CONDITION"
    REFER = "REFER"
    ESCALATE = "ESCALATE"


def _kind_from_token(token: str) -> MeasureKind:
    raw = (token or "").strip()
    if raw.lower() in FORBIDDEN_MEASURE_ALIASES:
        raise SemanticCollapseError(
            f"measure_kind {token!r} is not a canonical measure; "
            "bank inflow, tax turnover and statement revenue must stay distinct (SC-04/SC-05)"
        )
    try:
        return MeasureKind(raw)
    except ValueError as exc:
        raise SemanticCollapseError(
            f"unknown measure_kind {token!r}; generic revenue/turnover aliases are forbidden"
        ) from exc


@dataclass(frozen=True)
class LegalEntity:
    party_id: str
    observed_name: str
    source_record_id: str
    tax_token: str | None = None
    kind: PartyKind = PartyKind.LEGAL_ENTITY

    def __post_init__(self) -> None:
        if self.kind is not PartyKind.LEGAL_ENTITY:
            raise SemanticCollapseError("LegalEntity.kind must be LEGAL_ENTITY (SC-01)")


@dataclass(frozen=True)
class SoleTraderBusiness:
    party_id: str
    observed_name: str
    source_record_id: str
    tax_token: str | None = None
    kind: PartyKind = PartyKind.SOLE_TRADER_BUSINESS

    def __post_init__(self) -> None:
        if self.kind is not PartyKind.SOLE_TRADER_BUSINESS:
            raise SemanticCollapseError("SoleTraderBusiness is not a NaturalPerson or LegalEntity (SC-01)")


@dataclass(frozen=True)
class NaturalPerson:
    party_id: str
    observed_name: str
    source_record_id: str
    tax_token: str | None = None
    kind: PartyKind = PartyKind.NATURAL_PERSON
    restricted_attrs_excluded: bool = True

    def __post_init__(self) -> None:
        if self.kind is not PartyKind.NATURAL_PERSON:
            raise SemanticCollapseError("NaturalPerson.kind must be NATURAL_PERSON (SC-01)")


Party = Union[LegalEntity, SoleTraderBusiness, NaturalPerson]


def party_from_fixture(row: Mapping[str, str]) -> Party:
    raw_type = row["party_type"]
    kind = PARTY_TYPE_MAP.get(raw_type)
    if kind is None:
        raise SemanticCollapseError(f"unknown fixture party_type {raw_type!r}")
    common = dict(
        party_id=row["party_id"],
        observed_name=row["display_name"],
        source_record_id=row["source_identifier"],
        tax_token=row.get("tax_identifier_token"),
    )
    if kind is PartyKind.LEGAL_ENTITY:
        return LegalEntity(**common)
    if kind is PartyKind.SOLE_TRADER_BUSINESS:
        return SoleTraderBusiness(**common)
    return NaturalPerson(**common)


@dataclass(frozen=True)
class Applicant:
    """Role: who is requesting the facility. Not a party kind (SC-02)."""

    application_id: str
    played_by: Party
    is_primary: bool = True


@dataclass(frozen=True)
class Guarantor:
    """Role: typically a NaturalPerson. Not an Applicant or LegalEntity (SC-03)."""

    application_id: str
    played_by: Party
    decision_feature_eligible: str = "CONDITIONAL"

    def __post_init__(self) -> None:
        if isinstance(self.played_by, (LegalEntity, SoleTraderBusiness)):
            # Workshop fixtures use natural-person guarantors; do not silently
            # treat the borrower entity as the guarantor.
            raise SemanticCollapseError(
                "workshop Guarantor is not the applicant LegalEntity/SoleTraderBusiness (SC-03)"
            )


@dataclass(frozen=True)
class Application:
    application_id: str
    tenant_id: str
    workflow_status: str
    stage: str


@dataclass(frozen=True)
class RequestedLimit:
    amount: float
    as_of: str | None = None
    currency: str = "INR"


@dataclass(frozen=True)
class Facility:
    product: str
    requested_limit: RequestedLimit


@dataclass(frozen=True)
class Exposure:
    existing_exposure: float
    approved_limit: float
    past_due: float
    source_update_time: str
    source_system: str = "EXPOSURE"


@dataclass(frozen=True)
class BankTransaction:
    account_ref: str
    event_time: str
    amount: float


@dataclass(frozen=True)
class FinancialMetric:
    measure_kind: MeasureKind
    value: float
    source_system: str
    period: str | None = None
    source_record_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.measure_kind, MeasureKind):
            object.__setattr__(self, "measure_kind", _kind_from_token(str(self.measure_kind)))
        if self.measure_kind is MeasureKind.BANK_INFLOWS_12M and self.source_system != "BANK":
            raise SemanticCollapseError("BANK_INFLOWS_12M must originate from BANK (SC-04)")
        if self.measure_kind is MeasureKind.TAX_DECLARED_TURNOVER and self.source_system != "TAX":
            raise SemanticCollapseError("TAX_DECLARED_TURNOVER must originate from TAX (SC-04)")
        if self.measure_kind in {
            MeasureKind.INTERNAL_EXISTING_EXPOSURE,
            MeasureKind.INTERNAL_APPROVED_LIMIT,
            MeasureKind.INTERNAL_PAST_DUE,
        } and self.source_system != "EXPOSURE":
            raise SemanticCollapseError("internal exposure measures must originate from EXPOSURE (SC-06)")


@dataclass(frozen=True)
class TaxFiling:
    tax_record_id: str
    filing_period: str
    declared_turnover: float
    reuse_status: str
    reported_name: str

    def as_metric(self) -> FinancialMetric:
        return FinancialMetric(
            measure_kind=MeasureKind.TAX_DECLARED_TURNOVER,
            value=self.declared_turnover,
            source_system="TAX",
            period=self.filing_period,
            source_record_id=self.tax_record_id,
        )


@dataclass(frozen=True)
class BureauRecord:
    bureau_report_id: str
    reported_name: str
    score_band: str | None
    provider_status: str
    permissible_purpose: str
    source_system: str = "BUREAU"

    def __post_init__(self) -> None:
        if self.source_system != "BUREAU":
            raise SemanticCollapseError("BureauRecord cannot be sourced from EXPOSURE (SC-06)")


@dataclass(frozen=True)
class Policy:
    version: str
    status: str

    def __post_init__(self) -> None:
        if self.status == "SUPERSEDED" and self.version == "CREDIT-POLICY-3.2":
            raise SemanticCollapseError("active workshop policy CREDIT-POLICY-3.2 cannot be SUPERSEDED (SEM-09)")


@dataclass(frozen=True)
class PolicyRule:
    rule_id: str


@dataclass(frozen=True)
class PolicyEvaluation:
    result: str
    policy_version: str
    required_human_role: str
    triggered_rule_ids: tuple[str, ...] = ()

    @property
    def is_human_approval(self) -> bool:
        return False


@dataclass(frozen=True)
class ExceptionRecord:
    exception_class: ExceptionClass
    application_id: str
    detail: str = ""


@dataclass(frozen=True)
class AdverseFactor:
    factor_code: str
    source_evidence_id: str


@dataclass(frozen=True)
class Consent:
    purpose: str
    status: str
    source_system: str


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    source_system: str
    semantic_type: str
    source_record_id: str
    freshness_state: str = "unknown"
    conflict_state: str = "none"
    extraction_confidence: float | None = None

    def as_creditworthiness_confidence(self) -> float:
        raise SemanticCollapseError(
            "OCR/extraction_confidence is not creditworthiness confidence (SC-10)"
        )


@dataclass(frozen=True)
class Authority:
    role: str
    final_credit_decision: str

    def __post_init__(self) -> None:
        if self.role == "AI_AGENT" and self.final_credit_decision != "NO":
            raise SemanticCollapseError("AI_AGENT cannot hold final credit authority (SC-07)")


@dataclass(frozen=True)
class Recommendation:
    stance: RecommendationStance
    required_authority: Authority
    application_id: str

    def as_human_decision(self) -> "HumanDecision":
        raise SemanticCollapseError("Recommendation cannot be persisted as HumanDecision (SC-07)")


@dataclass(frozen=True)
class HumanDecision:
    outcome: DecisionOutcome
    actor_role: str
    policy_version: str
    application_id: str

    def __post_init__(self) -> None:
        if self.actor_role == "AI_AGENT":
            raise SemanticCollapseError("HumanDecision cannot be taken by AI_AGENT (SC-07)")


@dataclass(frozen=True)
class CreditMemo:
    memo_id: str
    application_id: str
    recommendation: Recommendation | None = None
    trust_class: str = "ASSISTANCE"

    def as_human_decision(self) -> HumanDecision:
        raise SemanticCollapseError("CreditMemo is not a HumanDecision or active Policy (SC-09)")


@dataclass(frozen=True)
class IdentityObservation:
    application_id: str
    source: str
    observed_name: str
    tax_token: str
    source_id: str
    canonical_candidate: str | None
    resolution_state: ResolutionState

    def __post_init__(self) -> None:
        if self.resolution_state is ResolutionState.MATCHED and self.source != "ADJUDICATION":
            # Crosswalk candidate is a hypothesis, not a match.
            raise SemanticCollapseError(
                "identifier_crosswalk canonical_candidate is not MATCHED (SC / SEM-08)"
            )


def assert_distinct_metrics(left: FinancialMetric, right: FinancialMetric) -> None:
    if left.measure_kind != right.measure_kind:
        return
    raise SemanticCollapseError("expected two different measure kinds")


def refuse_average(left: FinancialMetric, right: FinancialMetric) -> None:
    if left.measure_kind is not right.measure_kind:
        raise SemanticCollapseError(
            f"cannot average {left.measure_kind.value} with {right.measure_kind.value} (SC-04)"
        )


def refuse_policy_pass_as_approve(evaluation: PolicyEvaluation) -> None:
    if evaluation.result == "PASS":
        raise SemanticCollapseError("PolicyEvaluation.PASS is not HumanDecision.APPROVE (SC-08)")


def map_source_field(source: str, physical_field: str, value: Any, **meta: Any) -> Any:
    """Map a physical source field to a canonical object. Refuses collapse aliases."""
    src = source.upper()
    field = physical_field
    if src == "BANK" and field == "twelve_month_inflows":
        return FinancialMetric(
            measure_kind=MeasureKind.BANK_INFLOWS_12M,
            value=float(value),
            source_system="BANK",
            source_record_id=meta.get("source_record_id"),
            period=meta.get("period"),
        )
    if src == "TAX" and field == "declared_turnover":
        return FinancialMetric(
            measure_kind=MeasureKind.TAX_DECLARED_TURNOVER,
            value=float(value),
            source_system="TAX",
            source_record_id=meta.get("source_record_id"),
            period=meta.get("period"),
        )
    if src in {"BANK", "TAX"} and field.lower() in FORBIDDEN_MEASURE_ALIASES:
        raise SemanticCollapseError(
            f"{src}.{field} cannot map to a generic revenue measure (SC-04/SC-05)"
        )
    if src == "BUREAU" and field in {"commercial_score_band", "reported_name"}:
        return BureauRecord(
            bureau_report_id=meta.get("source_record_id") or "UNKNOWN",
            reported_name=str(value) if field == "reported_name" else meta.get("reported_name", ""),
            score_band=str(value) if field == "commercial_score_band" else meta.get("score_band"),
            provider_status=meta.get("provider_status", "AVAILABLE"),
            permissible_purpose=meta.get("permissible_purpose", "UNDERWRITING_VERIFIED"),
        )
    if src == "EXPOSURE" and field == "existing_exposure":
        return FinancialMetric(
            measure_kind=MeasureKind.INTERNAL_EXISTING_EXPOSURE,
            value=float(value),
            source_system="EXPOSURE",
            source_record_id=meta.get("source_record_id"),
        )
    if src == "POLICY" and field == "result":
        return PolicyEvaluation(
            result=str(value),
            policy_version=meta.get("policy_version", "CREDIT-POLICY-3.2"),
            required_human_role=meta.get("required_human_role", "CREDIT_ANALYST"),
        )
    if src == "DOCS" and field == "ocr_confidence":
        return Evidence(
            evidence_id=meta.get("evidence_id", "DOC"),
            source_system="DOCS",
            semantic_type="Evidence",
            source_record_id=meta.get("source_record_id", "DOC"),
            extraction_confidence=float(value),
        )
    if src == "CASE" and field == "decision":
        return HumanDecision(
            outcome=DecisionOutcome(str(value)),
            actor_role=meta.get("actor_role", "CREDIT_ANALYST"),
            policy_version=meta.get("policy_version", "CREDIT-POLICY-3.2"),
            application_id=meta.get("application_id", ""),
        )
    raise SemanticCollapseError(f"no canonical mapping for {src}.{field}")
