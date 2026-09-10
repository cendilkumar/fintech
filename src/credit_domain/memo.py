"""CRD-FR-006 / CRD-DATA-014 evidence-grounded credit memo.

Required sections. Material statements cite evidence or are labelled
[INFERENCE]. The memo is assistance, never the final credit decision.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .authority import handoff_recommendation
from .degraded import DegradedMode, assess_degraded_mode, scan_generated_degraded_claims
from .evidence import ApplicationEvidencePack, assemble_application_evidence
from .identity import resolve_application_identity
from .model import CreditMemo, Recommendation, SemanticCollapseError
from .policy import evaluate_application, load_live_application, scan_generated_policy_claims

REQUIRED_SECTIONS = (
    "APPLICANT_CONTEXT",
    "FINANCIAL_EVIDENCE",
    "EXPOSURE",
    "BUREAU",
    "POLICY_APPLICABILITY",
    "CONFLICTS",
    "RISK_FACTORS",
    "MITIGANTS",
    "EXCEPTIONS",
    "MISSING_EVIDENCE",
    "RECOMMENDATION",
    "REQUIRED_AUTHORITY",
)

FINAL_DECISION_RE = re.compile(
    r"\b(this\s+is\s+the\s+final\s+(?:credit\s+)?decision|"
    r"this\s+memo\s+(?:approves|declines)|"
    r"application\s+is\s+(?:approved|declined)|"
    r"human\s+decision\s+is\s+recorded)\b",
    re.I,
)
BLENDED_REVENUE_RE = re.compile(r"\b(averaged|blended)\s+revenue\b", re.I)


class MemoGroundingError(SemanticCollapseError):
    """Raised when a memo invents facts, lacks provenance, or claims decision authority."""


class MemoAssistanceUnavailable(SemanticCollapseError):
    """Raised when AI memo assistance is blocked by degraded mode."""


@dataclass(frozen=True)
class MemoStatement:
    section: str
    text: str
    evidence_ids: tuple[str, ...]
    kind: str

    def rendered(self) -> str:
        cites = ", ".join(self.evidence_ids) if self.evidence_ids else "none"
        if self.kind == "INFERENCE":
            return f"{self.text} [INFERENCE]"
        return f"{self.text} [FACT:{cites}]"


@dataclass
class GroundedCreditMemo:
    memo_id: str
    application_id: str
    statements: list[MemoStatement] = field(default_factory=list)
    recommendation: Recommendation | None = None
    trust_class: str = "ASSISTANCE"
    policy_version: str | None = None
    engine_result: str | None = None

    def statements_for(self, section: str) -> list[MemoStatement]:
        return [s for s in self.statements if s.section == section]

    def sections_present(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(s.section for s in self.statements))

    def rendered_text(self) -> str:
        lines = [
            f"Credit memo assistance {self.memo_id} for {self.application_id}.",
            "This is AI-assisted documentation. It is not the final credit decision.",
        ]
        for section in REQUIRED_SECTIONS:
            lines.append(f"## {section}")
            for stmt in self.statements_for(section):
                lines.append(stmt.rendered())
        return "\n".join(lines)

    def material_statements(self) -> list[MemoStatement]:
        return [s for s in self.statements if s.kind == "FACT"]

    def provenance_coverage(self) -> float:
        material = self.material_statements()
        if not material:
            return 0.0
        grounded = [s for s in material if s.evidence_ids]
        return len(grounded) / len(material)

    def as_domain(self) -> CreditMemo:
        return CreditMemo(
            memo_id=self.memo_id,
            application_id=self.application_id,
            recommendation=self.recommendation,
            trust_class=self.trust_class,
        )

    def as_human_decision(self) -> None:
        self.as_domain().as_human_decision()


def _fact(section: str, text: str, *evidence_ids: str) -> MemoStatement:
    return MemoStatement(section, text, tuple(eid for eid in evidence_ids if eid), "FACT")


def _inference(section: str, text: str) -> MemoStatement:
    return MemoStatement(section, text, (), "INFERENCE")


def _first(pack: ApplicationEvidencePack, semantic_type: str):
    for fact in pack.facts:
        if fact.semantic_type == semantic_type:
            return fact
    return None


def generate_credit_memo(application_id: str) -> GroundedCreditMemo:
    degraded = assess_degraded_mode(application_id)
    if not degraded.ai_assistance_permitted:
        raise MemoAssistanceUnavailable(
            f"memo assistance blocked in mode {degraded.mode.value}"
        )
    pack = assemble_application_evidence(application_id)
    identity = resolve_application_identity(application_id)
    view = evaluate_application(application_id)
    rec = handoff_recommendation(application_id)
    app = load_live_application(application_id)
    statements = _build_statements(pack, identity, view, rec, app, degraded)
    memo = GroundedCreditMemo(
        memo_id=f"MEMO-{application_id}",
        application_id=application_id,
        statements=statements,
        recommendation=rec,
        trust_class="ASSISTANCE",
        policy_version=view.retrieval.controlling_version,
        engine_result=None if view.engine is None else view.engine.result,
    )
    validate_credit_memo(memo)
    return memo


def _build_statements(pack, identity, view, rec, app, degraded):
    application_id = pack.application_id
    los_ref = f"live_applications.csv:{application_id}"
    engine_ref = f"policy_engine_results.jsonl:{application_id}"
    policy_ref = view.retrieval.controlling.source_path if view.retrieval.controlling else engine_ref
    bank = _first(pack, "BANK_INFLOWS_12M")
    tax = _first(pack, "TAX_DECLARED_TURNOVER")
    exposure = _first(pack, "INTERNAL_EXISTING_EXPOSURE")
    past_due = _first(pack, "INTERNAL_PAST_DUE")
    bureau = _first(pack, "BureauRecord.score_band") or _first(pack, "BureauRecord")

    statements = [
        _fact(
            "APPLICANT_CONTEXT",
            f"Applicant {app['applicant_name']} requests {app['product']} "
            f"limit INR {int(app['requested_limit'])} as a {app['applicant_type']}.",
            los_ref,
        ),
        _fact(
            "APPLICANT_CONTEXT",
            f"Identity state is {identity.organization.state.value}; "
            f"entity_ref {identity.safe_entity_ref()}.",
            f"identifier_crosswalk.csv:{application_id}",
        ),
    ]
    if bank is not None:
        statements.append(
            _fact(
                "FINANCIAL_EVIDENCE",
                f"BANK_INFLOWS_12M is {bank.value} with freshness {bank.freshness_state}; "
                f"not presented as interchangeable with tax turnover.",
                bank.evidence_id,
            )
        )
    else:
        statements.append(_fact("FINANCIAL_EVIDENCE", "Bank inflow envelope is not available.", "BANK:UNAVAILABLE"))
    if tax is not None:
        statements.append(
            _fact(
                "FINANCIAL_EVIDENCE",
                f"TAX_DECLARED_TURNOVER is {tax.value} for {tax.period}.",
                tax.evidence_id,
            )
        )
    if exposure is not None:
        statements.append(
            _fact("EXPOSURE", f"INTERNAL_EXISTING_EXPOSURE is {exposure.value}.", exposure.evidence_id)
        )
    if past_due is not None:
        statements.append(
            _fact("EXPOSURE", f"INTERNAL_PAST_DUE is {past_due.value}.", past_due.evidence_id)
        )
    if bureau is not None and bureau.freshness_state != "unavailable" and bureau.value is not None:
        statements.append(
            _fact(
                "BUREAU",
                f"Bureau score band is {bureau.value}; freshness {bureau.freshness_state}.",
                bureau.evidence_id,
            )
        )
    else:
        statements.append(
            _fact(
                "BUREAU",
                "Bureau report is unavailable; no score or band is invented.",
                bureau.evidence_id if bureau is not None else f"BUREAU:{application_id}:UNAVAILABLE",
            )
        )
    engine_result = None if view.engine is None else view.engine.result
    statements.append(
        _fact(
            "POLICY_APPLICABILITY",
            f"Active policy is {view.retrieval.controlling_version}; engine result is {engine_result}. "
            f"PolicyEvaluation.PASS is not HumanDecision.APPROVE.",
            engine_ref,
            policy_ref,
        )
    )
    if pack.conflicts:
        for conflict in pack.conflicts:
            statements.append(
                _fact(
                    "CONFLICTS",
                    f"Unresolved conflict {conflict.left_semantic_type}={conflict.left_value} vs "
                    f"{conflict.right_semantic_type}={conflict.right_value}; "
                    f"human reconciliation required; values are not averaged.",
                    conflict.left_evidence_id,
                    conflict.right_evidence_id,
                )
            )
    else:
        statements.append(
            _fact(
                "CONFLICTS",
                "No material bank-versus-tax conflict is recorded on this application.",
                los_ref,
            )
        )
    if view.engine and view.engine.triggered_rule_ids:
        statements.append(
            _fact(
                "RISK_FACTORS",
                f"Engine-triggered rules: {', '.join(view.engine.triggered_rule_ids)}.",
                engine_ref,
            )
        )
    else:
        statements.append(
            _fact("RISK_FACTORS", "No engine-triggered risk or adverse rules are recorded.", engine_ref)
        )
    statements.append(
        _inference(
            "MITIGANTS",
            "No source-recorded mitigant objects exist in the live fixture; none are invented.",
        )
    )
    if view.exception_class is not None:
        statements.append(
            _fact(
                "EXCEPTIONS",
                f"Exception class is {view.exception_class.value} from engine result {engine_result}.",
                engine_ref,
            )
        )
    else:
        statements.append(
            _fact("EXCEPTIONS", "No policy exception class is raised by the engine.", engine_ref)
        )
    missing_bits = []
    if not degraded.bureau_available:
        missing_bits.append("bureau unavailable")
    if degraded.bank_freshness == "stale":
        missing_bits.append("bank feed stale; refresh requested")
    if missing_bits:
        statements.append(
            _fact("MISSING_EVIDENCE", "Degraded evidence: " + "; ".join(missing_bits) + ".", engine_ref)
        )
    else:
        statements.append(
            _fact(
                "MISSING_EVIDENCE",
                "No unavailable bureau or stale bank is recorded for this application.",
                engine_ref,
            )
        )
    statements.append(
        _fact(
            "RECOMMENDATION",
            f"Assistance stance is {rec.stance.value}. This memo does not approve, decline "
            f"or record a HumanDecision.",
            engine_ref,
        )
    )
    statements.append(
        _fact(
            "REQUIRED_AUTHORITY",
            f"Required human authority is {rec.required_authority.role}; "
            f"AI_AGENT has no final credit decision.",
            engine_ref,
        )
    )
    return statements


def validate_credit_memo(memo: GroundedCreditMemo) -> None:
    present = set(memo.sections_present())
    missing = [s for s in REQUIRED_SECTIONS if s not in present]
    if missing:
        raise MemoGroundingError(f"memo missing required sections: {missing}")
    if memo.trust_class != "ASSISTANCE":
        raise MemoGroundingError("credit memo trust_class must be ASSISTANCE")
    if memo.provenance_coverage() < 1.0:
        raise MemoGroundingError("material-factor provenance coverage is below 100% (HG-03)")
    for stmt in memo.material_statements():
        if not stmt.evidence_ids:
            raise MemoGroundingError(f"material statement lacks evidence: {stmt.text}")
    validate_memo_text(memo.rendered_text(), memo.application_id)


def validate_memo_text(text: str, application_id: str) -> None:
    if FINAL_DECISION_RE.search(text):
        raise MemoGroundingError("memo must not represent itself as the final credit decision")
    if BLENDED_REVENUE_RE.search(text):
        raise MemoGroundingError("memo must not emit blended or averaged revenue")
    scan_generated_policy_claims(text, application_id=application_id)
    assessment = assess_degraded_mode(application_id)
    scan_generated_degraded_claims(text, assessment)
    if assessment.mode is DegradedMode.AI_ASSISTANCE_UNAVAILABLE:
        raise MemoAssistanceUnavailable("cannot accept a generated memo while AI assist is unavailable")
