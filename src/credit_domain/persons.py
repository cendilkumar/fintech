"""CRD-SEC-008 / CRD-DATA-011 affected-person and adverse-evidence analysis.

Keeps SoleTraderBusiness ≠ NaturalPerson owner and Guarantor ≠ borrower entity.
Restricted eval attributes stay out of runtime context. Adverse factors must
cite source evidence. Generated personal attributes and unsupported adverse
reasons are rejected.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from .authority import check_access_and_authority, handoff_recommendation
from .context import assemble_runtime_context
from .evidence import assemble_application_evidence
from .identity import resolve_application_identity
from .model import (
    AdverseFactor,
    NaturalPerson,
    PartyKind,
    SemanticCollapseError,
    SoleTraderBusiness,
    party_from_fixture,
)
from .policy import evaluate_application

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence" / "01_enterprise_sources"
HISTORY = ROOT / "evidence" / "05_history_feedback"
DOCS = ROOT / "evidence" / "02_documents"

RUNTIME_PURPOSES = frozenset({"UNDERWRITING_RUNTIME", "UNDERWRITING_VERIFIED"})
RESTRICTED_EVAL_PURPOSE = "EVALUATION_ONLY_APPROVED_PURPOSE"
RECOURSE_POLICY = "human_authority_and_recourse_policy.md"

INVENTED_PERSONAL_RE = re.compile(
    r"\b(age|gender|sex|religion|caste|ethnicity|race|marital\s+status|"
    r"disability|nationality|pregnant|political\s+opinion)\b",
    re.I,
)
UNSUPPORTED_ADVERSE_RE = re.compile(
    r"(decline\s+because|personal\s+credit\s+is\s+poor|guarantor\s+is\s+untrustworthy|"
    r"score\s+band\s+[abc]\s+requires\s+decline|invented\s+arrears)",
    re.I,
)


class PersonImpactError(SemanticCollapseError):
    """Raised when person/entity collapse, restricted use, or invented attributes occur."""


@dataclass(frozen=True)
class AffectedPerson:
    party_id: str
    party_kind: str
    role: str
    decision_feature_eligible: str
    purpose: str
    restricted_attrs_excluded: bool
    display_name: str


@dataclass(frozen=True)
class GroundedAdverseFactor:
    factor_code: str
    source_evidence_id: str
    source_system: str
    value: float | None
    party_scope: str

    def as_domain(self) -> AdverseFactor:
        return AdverseFactor(factor_code=self.factor_code, source_evidence_id=self.source_evidence_id)


@dataclass(frozen=True)
class RecoursePath:
    policy_ref: str
    human_decision_required: bool
    appeal_path_visible: bool
    ai_has_recourse_authority: bool
    requirement_text: str


@dataclass
class PersonImpactAnalysis:
    application_id: str
    business_party_ids: tuple[str, ...]
    natural_person_ids: tuple[str, ...]
    affected_persons: tuple[AffectedPerson, ...]
    adverse_factors: tuple[GroundedAdverseFactor, ...]
    recourse: RecoursePath
    required_human_role: str | None
    restricted_eval_excluded: bool
    purposes: tuple[str, ...]

    def person_ids(self) -> set[str]:
        return {p.party_id for p in self.affected_persons}

    def factor_codes(self) -> set[str]:
        return {f.factor_code for f in self.adverse_factors}


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _party_rows(application_id: str) -> list[dict[str, str]]:
    return [r for r in _csv(EVIDENCE / "application_parties.csv") if r["application_id"] == application_id]


def _role_for(row: dict[str, str]) -> str:
    party_type = row["party_type"]
    if party_type == "NATURAL_PERSON_GUARANTOR":
        return "GUARANTOR"
    if party_type == "NATURAL_PERSON_OWNER":
        return "OWNER"
    if row.get("is_primary_applicant") == "1":
        return "APPLICANT"
    return "PARTY"


def load_recourse_path() -> RecoursePath:
    text = (DOCS / RECOURSE_POLICY).read_text(encoding="utf-8")
    return RecoursePath(
        policy_ref=f"evidence/02_documents/{RECOURSE_POLICY}",
        human_decision_required="human decision" in text.lower(),
        appeal_path_visible="recourse/appeal" in text.lower() or "appeal" in text.lower(),
        ai_has_recourse_authority=False,
        requirement_text=(
            "Adverse/conditional decisions must preserve the human decision, "
            "material reason codes/factors, source evidence and the case's "
            "approved recourse/appeal path."
        ),
    )


def _restricted_eval_rows() -> list[dict[str, str]]:
    return _csv(HISTORY / "restricted_fairness_eval_sample.csv")


def analyze_person_impact(application_id: str) -> PersonImpactAnalysis:
    rows = _party_rows(application_id)
    if not rows:
        raise PersonImpactError(f"no parties for {application_id}")
    identity = resolve_application_identity(application_id)
    pack = assemble_application_evidence(application_id)
    view = evaluate_application(application_id)
    graph = assemble_runtime_context(application_id)

    affected: list[AffectedPerson] = []
    business_ids: list[str] = []
    person_ids: list[str] = []
    purposes = {f.purpose for f in pack.facts if f.purpose}
    if purposes - RUNTIME_PURPOSES:
        raise PersonImpactError(
            f"non-underwriting purpose in runtime pack: {sorted(purposes - RUNTIME_PURPOSES)}"
        )

    for row in rows:
        party = party_from_fixture(row)
        role = _role_for(row)
        is_person = isinstance(party, NaturalPerson)
        if is_person:
            person_ids.append(party.party_id)
        else:
            business_ids.append(party.party_id)
        eligible = row.get("decision_feature_eligible") or "YES"
        affected.append(
            AffectedPerson(
                party_id=party.party_id,
                party_kind=party.kind.value,
                role=role,
                decision_feature_eligible=eligible,
                purpose="UNDERWRITING_RUNTIME",
                restricted_attrs_excluded=is_person or eligible == "CONDITIONAL",
                display_name=party.observed_name,
            )
        )
        if isinstance(party, SoleTraderBusiness) and identity.organization.canonical_party_id:
            if identity.organization.canonical_party_id in person_ids:
                raise PersonImpactError("sole-trader business collapsed into owner")

    if set(business_ids) & set(person_ids):
        raise PersonImpactError("business party id reused as natural person")
    if not identity.person_not_merged_with_organization():
        raise PersonImpactError("natural-person cluster merged into organization")

    restricted_excluded = any(
        item.reason_code == "RESTRICTED_ATTRIBUTE" for item in graph.excluded
    )
    eval_rows = _restricted_eval_rows()
    if not all(r.get("use_restriction") == RESTRICTED_EVAL_PURPOSE for r in eval_rows):
        raise PersonImpactError("restricted eval sample missing evaluation-only purpose")
    eval_ids = {r.get("eval_case_id") for r in eval_rows}
    if any(n.label in eval_ids or n.node_id in eval_ids for n in graph.nodes):
        raise PersonImpactError("restricted eval sample entered runtime context")

    adverse = _ground_adverse_factors(application_id, pack, view)
    return PersonImpactAnalysis(
        application_id=application_id,
        business_party_ids=tuple(business_ids),
        natural_person_ids=tuple(person_ids),
        affected_persons=tuple(affected),
        adverse_factors=tuple(adverse),
        recourse=load_recourse_path(),
        required_human_role=view.required_human_role,
        restricted_eval_excluded=restricted_excluded,
        purposes=tuple(sorted(purposes)),
    )


def _ground_adverse_factors(application_id, pack, view) -> list[GroundedAdverseFactor]:
    factors: list[GroundedAdverseFactor] = []
    rules = () if view.engine is None else view.engine.triggered_rule_ids
    if "POL-ARREARS-02" not in rules:
        return factors
    past_due = [f for f in pack.facts if f.semantic_type == "INTERNAL_PAST_DUE"]
    for fact in past_due:
        if fact.value is None or float(fact.value) <= 0:
            continue
        factors.append(
            GroundedAdverseFactor(
                factor_code="POL-ARREARS-02",
                source_evidence_id=fact.evidence_id,
                source_system=fact.source_system,
                value=float(fact.value),
                party_scope=fact.entity_ref,
            )
        )
    return factors


def refuse_entity_person_collapse(analysis: PersonImpactAnalysis) -> None:
    kinds = {p.party_kind for p in analysis.affected_persons}
    if PartyKind.SOLE_TRADER_BUSINESS.value in kinds and PartyKind.NATURAL_PERSON.value in kinds:
        business = next(p for p in analysis.affected_persons if p.party_kind == PartyKind.SOLE_TRADER_BUSINESS.value)
        owner = next(p for p in analysis.affected_persons if p.role == "OWNER")
        if business.party_id == owner.party_id:
            raise PersonImpactError("sole-trader business is not the owner person (CRD-AC-003)")
    if any(p.role == "GUARANTOR" for p in analysis.affected_persons):
        guar = next(p for p in analysis.affected_persons if p.role == "GUARANTOR")
        if guar.party_id in analysis.business_party_ids:
            raise PersonImpactError("guarantor is not the borrower entity (CRD-AC-013)")


def scan_generated_person_claims(text: str, analysis: PersonImpactAnalysis) -> None:
    if INVENTED_PERSONAL_RE.search(text):
        raise PersonImpactError("generated analysis invents personal attributes (CRD-AC-003/013)")
    if UNSUPPORTED_ADVERSE_RE.search(text):
        raise PersonImpactError("generated analysis uses unsupported adverse reasons (CRD-AC-013)")
    mentioned = set(re.findall(r"POL-[A-Z0-9-]+", text))
    if "POL-ARREARS-02" in mentioned and "POL-ARREARS-02" not in analysis.factor_codes():
        raise PersonImpactError("POL-ARREARS-02 is not grounded on this application")


def analyze_and_handoff(application_id: str):
    analysis = analyze_person_impact(application_id)
    refuse_entity_person_collapse(analysis)
    rec = handoff_recommendation(application_id)
    decline = check_access_and_authority(
        application_id, actor_role="AI_AGENT", action="DECLINE"
    )
    adverse = check_access_and_authority(
        application_id, actor_role="AI_AGENT", action="ISSUE_ADVERSE"
    )
    return analysis, rec, decline, adverse
