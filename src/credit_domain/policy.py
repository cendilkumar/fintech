"""CRD-FR-005 / CRD-DATA-007 / CRD-TOOL-004 policy-as-authority.

Active CREDIT-POLICY-3.2 is selected by version, status and as-of date.
Similarity cannot choose the controlling bundle. Policy Engine rows are
authoritative. Generated thresholds, exception criteria, delegated-authority
cut-overs and adverse-action rationale that are not in the active catalog
are rejected. Missing active policy or missing engine result → abstain.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping

from .model import (
    ExceptionClass,
    Policy,
    PolicyEvaluation,
    RecommendationStance,
    SemanticCollapseError,
    refuse_policy_pass_as_approve,
)

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "evidence" / "02_documents"
EVIDENCE = ROOT / "evidence" / "01_enterprise_sources"

WORKSHOP_AS_OF = date(2026, 9, 15)
ACTIVE_VERSION = "CREDIT-POLICY-3.2"
SUPERSEDED_VERSION = "CREDIT-POLICY-2.9"

POLICY_DOCUMENTS = {
    ACTIVE_VERSION: DOCS / "credit_underwriting_policy_v3_2.md",
    SUPERSEDED_VERSION: DOCS / "superseded_credit_policy_v2_9_REFERENCE_ONLY.md",
}

# Bindings stated in CREDIT-POLICY-3.2 text and CRD-DATA-007. No other
# numeric credit thresholds exist in the workshop bundle.
KNOWN_RULE_BINDINGS = {
    "AUTH-LIMIT-01": {
        "kind": "requested_limit_above_inr",
        "amount_inr": 5_000_000,
        "required_human_role": "CREDIT_AUTHORITY",
    },
    "DATA-FRESHNESS-BANK": {
        "kind": "bank_stale_after_days",
        "days": 7,
    },
}

MISSING_DATA_RESULTS = frozenset({"INSUFFICIENT_EVIDENCE"})
POLICY_EXCEPTION_RESULTS = frozenset({"EXCEPTION_REVIEW"})
AUTHORITY_RESULTS = frozenset({"REQUIRES_CREDIT_AUTHORITY"})
ADVERSE_RESULTS = frozenset({"ADVERSE_FACTORS_REVIEW"})

_STATUS_RE = re.compile(r"\*\*Status:\*\*\s*(.+)")
_EFFECTIVE_RE = re.compile(r"\*\*Effective:\*\*\s*(\d{4}-\d{2}-\d{2})")
_INR_RE = re.compile(r"INR\s*([0-9][0-9,]*)")
_DAYS_RE = re.compile(r"older than\s+(\d+)\s+days", re.I)
_MONEY_RE = re.compile(
    r"(?:INR\s*)?([0-9]{1,3}(?:,[0-9]{2,3})+|[0-9]{5,9})(?:\s*(lakh|lac|crore|million))?",
    re.I,
)
_THRESHOLD_CLAIM_RE = re.compile(
    r"(threshold|cut[- ]?off|delegated|automatically\s+approve|approve\s+if|"
    r"policy\s+requires|escalat|authority\s+is|minimum\s+limit|maximum\s+limit|"
    r"below\s+inr|under\s+inr|above\s+inr|decline\s+if|exception\s+(?:if|when|criteria))",
    re.I,
)
_INVENTED_EXCEPTION_RE = re.compile(
    r"POL-EXC-07.{0,80}(?:when|if|criteria|fires|applies when)|"
    r"exception\s+(?:criteria|rule)\s+(?:is|when|if)",
    re.I,
)
_INVENTED_ADVERSE_RE = re.compile(
    r"policy\s+requires\s+(?:a\s+)?(?:decline|adverse)|"
    r"decline\s+when\s+(?:commercial\s+)?score|"
    r"adverse[- ]action\s+rationale",
    re.I,
)


class PolicyFidelityError(SemanticCollapseError):
    """Raised when generated text invents policy or a non-active bundle is applied."""


class PolicyUnavailable(SemanticCollapseError):
    """Raised when no authoritative active policy or engine result can be used."""


@dataclass(frozen=True)
class PolicyLiteral:
    kind: str
    amount_inr: int | None = None
    days: int | None = None
    required_human_role: str | None = None


@dataclass(frozen=True)
class PolicyBundle:
    version: str
    status: str
    effective_date: date | None
    source_path: str
    controlling: bool
    known_inr_amounts: tuple[int, ...]
    known_day_limits: tuple[int, ...]
    known_rule_ids: tuple[str, ...]
    body: str

    def as_policy(self) -> Policy:
        return Policy(version=self.version, status=self.status)


@dataclass(frozen=True)
class PolicyDocumentHit:
    version: str
    score: float
    controlling: bool
    status: str


@dataclass(frozen=True)
class PolicyRetrieval:
    as_of: date
    controlling: PolicyBundle | None
    historical: tuple[PolicyBundle, ...]
    abstain: bool
    abstain_reason: str | None = None

    @property
    def controlling_version(self) -> str | None:
        return None if self.controlling is None else self.controlling.version


@dataclass(frozen=True)
class ApplicationPolicyView:
    application_id: str
    requested_limit: int
    los_assigned_role: str
    retrieval: PolicyRetrieval
    engine: PolicyEvaluation | None
    exception_class: ExceptionClass | None
    stance: RecommendationStance
    required_human_role: str | None
    notes: tuple[str, ...]

    def require_engine(self) -> PolicyEvaluation:
        if self.engine is None:
            raise PolicyUnavailable(
                f"no authoritative engine result for {self.application_id}; abstain"
            )
        return self.engine

    def refuse_pass_as_approve(self) -> None:
        if self.engine is not None:
            refuse_policy_pass_as_approve(self.engine)


def _jsonl(name: str) -> list[dict[str, Any]]:
    path = EVIDENCE / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _csv(name: str) -> list[dict[str, str]]:
    with (EVIDENCE / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _parse_as_of(value: date | datetime | str | None) -> date:
    if value is None:
        return WORKSHOP_AS_OF
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if "T" in text:
        return datetime.fromisoformat(text).date()
    return date.fromisoformat(text[:10])


def _normalize_status(raw: str) -> str:
    token = raw.strip().split("/")[0].strip().upper()
    if "SUPERSEDED" in token:
        return "SUPERSEDED"
    if token == "ACTIVE":
        return "ACTIVE"
    return token


def _inr_amounts_from_text(text: str) -> tuple[int, ...]:
    found = []
    for match in _INR_RE.finditer(text):
        found.append(int(match.group(1).replace(",", "")))
    return tuple(found)


def _day_limits_from_text(text: str) -> tuple[int, ...]:
    return tuple(int(m.group(1)) for m in _DAYS_RE.finditer(text))


def load_policy_catalog() -> dict[str, PolicyBundle]:
    catalog: dict[str, PolicyBundle] = {}
    for version, path in POLICY_DOCUMENTS.items():
        text = path.read_text(encoding="utf-8")
        status_m = _STATUS_RE.search(text)
        if not status_m:
            raise PolicyUnavailable(f"policy document {path.name} has no Status header")
        status = _normalize_status(status_m.group(1))
        effective_m = _EFFECTIVE_RE.search(text)
        effective = date.fromisoformat(effective_m.group(1)) if effective_m else None
        known_inr = _inr_amounts_from_text(text) if status == "ACTIVE" else ()
        known_days = _day_limits_from_text(text) if status == "ACTIVE" else ()
        known_rules = tuple(KNOWN_RULE_BINDINGS) if status == "ACTIVE" else ()
        catalog[version] = PolicyBundle(
            version=version,
            status=status,
            effective_date=effective,
            source_path=str(path.relative_to(ROOT)).replace("\\", "/"),
            controlling=False,
            known_inr_amounts=known_inr,
            known_day_limits=known_days,
            known_rule_ids=known_rules,
            body=text,
        )
    return catalog


def _with_controlling(bundle: PolicyBundle, controlling: bool) -> PolicyBundle:
    return PolicyBundle(
        version=bundle.version,
        status=bundle.status,
        effective_date=bundle.effective_date,
        source_path=bundle.source_path,
        controlling=controlling,
        known_inr_amounts=bundle.known_inr_amounts,
        known_day_limits=bundle.known_day_limits,
        known_rule_ids=bundle.known_rule_ids,
        body=bundle.body,
    )


def retrieve_active_policy(
    as_of: date | datetime | str | None = None,
    *,
    version: str | None = None,
    context: Mapping[str, Any] | None = None,
) -> PolicyRetrieval:
    """Deterministic CRD-TOOL-004 retrieval. Similarity is not an input."""
    del context  # context may carry application_id for callers; it cannot choose the bundle
    when = _parse_as_of(as_of)
    catalog = load_policy_catalog()

    if version == SUPERSEDED_VERSION:
        historical = (_with_controlling(catalog[SUPERSEDED_VERSION], False),)
        active = _select_active(catalog, when)
        if active is None:
            return PolicyRetrieval(
                as_of=when,
                controlling=None,
                historical=historical,
                abstain=True,
                abstain_reason="requested bundle is SUPERSEDED and no ACTIVE policy applies",
            )
        return PolicyRetrieval(
            as_of=when,
            controlling=active,
            historical=historical,
            abstain=False,
        )

    active = _select_active(catalog, when)
    if active is None:
        return PolicyRetrieval(
            as_of=when,
            controlling=None,
            historical=(_with_controlling(catalog[SUPERSEDED_VERSION], False),),
            abstain=True,
            abstain_reason="no ACTIVE policy applies for as-of date; do not invent or apply v2.9",
        )
    if version and version != active.version:
        requested = catalog.get(version)
        if requested is None or requested.status != "ACTIVE":
            return PolicyRetrieval(
                as_of=when,
                controlling=active,
                historical=(_with_controlling(requested, False),) if requested else (),
                abstain=False,
            )
    return PolicyRetrieval(
        as_of=when,
        controlling=active,
        historical=(_with_controlling(catalog[SUPERSEDED_VERSION], False),),
        abstain=False,
    )


def _select_active(catalog: Mapping[str, PolicyBundle], when: date) -> PolicyBundle | None:
    candidate = catalog.get(ACTIVE_VERSION)
    if candidate is None or candidate.status != "ACTIVE":
        return None
    if candidate.effective_date is None or when < candidate.effective_date:
        return None
    return _with_controlling(candidate, True)


def require_active_policy(
    as_of: date | datetime | str | None = None,
    **kwargs: Any,
) -> PolicyBundle:
    retrieval = retrieve_active_policy(as_of, **kwargs)
    if retrieval.abstain or retrieval.controlling is None:
        raise PolicyUnavailable(retrieval.abstain_reason or "active policy unavailable")
    return retrieval.controlling


def rank_policy_documents(query: str) -> list[PolicyDocumentHit]:
    """Lexical overlap only. MUST NOT be used as authority (CRD-AC-012)."""
    catalog = load_policy_catalog()
    tokens = {t for t in re.findall(r"[a-z0-9.]+", query.lower()) if len(t) > 2}
    hits: list[PolicyDocumentHit] = []
    for bundle in catalog.values():
        body_tokens = set(re.findall(r"[a-z0-9.]+", bundle.body.lower()))
        score = float(len(tokens & body_tokens))
        hits.append(
            PolicyDocumentHit(
                version=bundle.version,
                score=score,
                controlling=False,
                status=bundle.status,
            )
        )
    hits.sort(key=lambda h: (-h.score, h.version))
    return hits


def use_similarity_hit_as_authority(query: str) -> PolicyBundle:
    """Forbidden authority path. Always raises."""
    hits = rank_policy_documents(query)
    top = hits[0].version if hits else "unknown"
    raise PolicyFidelityError(
        f"similarity cannot choose policy authority (top hit {top}); "
        "use retrieve_active_policy"
    )


def apply_bundle_as_controlling(bundle: PolicyBundle) -> PolicyBundle:
    if not bundle.controlling or bundle.status != "ACTIVE":
        raise PolicyFidelityError(
            f"{bundle.version} status={bundle.status} cannot control a decision"
        )
    return bundle


def load_engine_result(application_id: str) -> PolicyEvaluation | None:
    for row in _jsonl("policy_engine_results.jsonl"):
        if row.get("application_id") != application_id:
            continue
        if not row.get("authoritative", False):
            continue
        return PolicyEvaluation(
            result=str(row["result"]),
            policy_version=str(row["policy_version"]),
            required_human_role=str(row["required_human_role"]),
            triggered_rule_ids=tuple(row.get("triggered_rule_ids") or ()),
        )
    return None


def load_live_application(application_id: str) -> dict[str, str]:
    for row in _csv("live_applications.csv"):
        if row.get("application_id") == application_id:
            return row
    raise PolicyUnavailable(f"unknown application {application_id}")


def _exception_class_for(result: str) -> ExceptionClass | None:
    if result in MISSING_DATA_RESULTS:
        return ExceptionClass.MISSING_EVIDENCE
    if result in POLICY_EXCEPTION_RESULTS:
        return ExceptionClass.POLICY_EXCEPTION
    if result in ADVERSE_RESULTS:
        return ExceptionClass.ADVERSE
    return None


def bureau_available(application_id: str) -> bool:
    for row in _jsonl("bureau_reports.jsonl"):
        if row.get("application_id") == application_id:
            return str(row.get("provider_status", "")).upper() == "AVAILABLE"
    for row in _jsonl("source_health_events.jsonl"):
        if row.get("application_id") == application_id and row.get("source") == "CREDIT_BUREAU":
            return str(row.get("state", "")).upper() == "HEALTHY"
    return False


def evaluate_application(
    application_id: str,
    *,
    as_of: date | datetime | str | None = None,
) -> ApplicationPolicyView:
    retrieval = retrieve_active_policy(as_of, context={"application_id": application_id})
    app = load_live_application(application_id)
    requested_limit = int(app["requested_limit"])
    los_role = app["assigned_role"]
    engine = load_engine_result(application_id)

    if retrieval.abstain or retrieval.controlling is None:
        return ApplicationPolicyView(
            application_id=application_id,
            requested_limit=requested_limit,
            los_assigned_role=los_role,
            retrieval=retrieval,
            engine=None,
            exception_class=None,
            stance=RecommendationStance.ABSTAIN,
            required_human_role=None,
            notes=(retrieval.abstain_reason or "active policy unavailable",),
        )
    if engine is None:
        return ApplicationPolicyView(
            application_id=application_id,
            requested_limit=requested_limit,
            los_assigned_role=los_role,
            retrieval=retrieval,
            engine=None,
            exception_class=None,
            stance=RecommendationStance.ABSTAIN,
            required_human_role=None,
            notes=("authoritative policy engine result unavailable; abstain",),
        )
    if engine.policy_version != retrieval.controlling.version:
        raise PolicyFidelityError(
            f"engine version {engine.policy_version} is not the controlling "
            f"{retrieval.controlling.version}"
        )

    notes = [
        f"controlling_policy={retrieval.controlling.version}",
        f"engine_result={engine.result}",
        f"engine_role={engine.required_human_role}",
        f"los_assigned_role={los_role}",
    ]
    if requested_limit > KNOWN_RULE_BINDINGS["AUTH-LIMIT-01"]["amount_inr"]:
        notes.append("AUTH-LIMIT-01 consistency: requested_limit above documented INR 5000000")
    if engine.result == "PASS":
        notes.append("PolicyEvaluation.PASS is not HumanDecision.APPROVE")

    return ApplicationPolicyView(
        application_id=application_id,
        requested_limit=requested_limit,
        los_assigned_role=los_role,
        retrieval=retrieval,
        engine=engine,
        exception_class=_exception_class_for(engine.result),
        stance=RecommendationStance.REFER,
        required_human_role=engine.required_human_role,
        notes=tuple(notes),
    )


def _normalize_money(number: str, unit: str | None) -> int:
    amount = int(number.replace(",", ""))
    if unit is None:
        return amount
    token = unit.lower()
    if token in {"lakh", "lac"}:
        return amount * 100_000
    if token == "crore":
        return amount * 10_000_000
    if token == "million":
        return amount * 1_000_000
    return amount


def scan_generated_policy_claims(
    text: str,
    *,
    as_of: date | datetime | str | None = None,
    application_id: str | None = None,
) -> None:
    """Reject invented thresholds, exception criteria and adverse rationale (CRD-AC-014)."""
    retrieval = retrieve_active_policy(as_of)
    if retrieval.abstain or retrieval.controlling is None:
        raise PolicyUnavailable(retrieval.abstain_reason or "cannot validate claims without active policy")

    allowed_inr = set(retrieval.controlling.known_inr_amounts)
    if application_id:
        allowed_inr.add(int(load_live_application(application_id)["requested_limit"]))

    if _INVENTED_EXCEPTION_RE.search(text):
        raise PolicyFidelityError("invented exception criteria are not in CREDIT-POLICY-3.2")
    if _INVENTED_ADVERSE_RE.search(text):
        raise PolicyFidelityError("invented adverse-action rationale is not in CREDIT-POLICY-3.2")
    if re.search(r"CREDIT-POLICY-2\.9", text, re.I) and _THRESHOLD_CLAIM_RE.search(text):
        raise PolicyFidelityError("superseded v2.9 cannot supply a controlling threshold")

    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if not _THRESHOLD_CLAIM_RE.search(sentence):
            continue
        for match in _MONEY_RE.finditer(sentence):
            amount = _normalize_money(match.group(1), match.group(2))
            if amount in allowed_inr:
                # Application requested-limit facts may be restated, but not as a
                # new approval/delegated-authority cutoff.
                if amount not in retrieval.controlling.known_inr_amounts and re.search(
                    r"(approve|delegated|threshold|cut[- ]?off|authority\s+is)",
                    sentence,
                    re.I,
                ):
                    raise PolicyFidelityError(
                        f"invented credit threshold {amount} is not in CREDIT-POLICY-3.2"
                    )
                continue
            if amount in set(retrieval.controlling.known_day_limits):
                continue
            raise PolicyFidelityError(
                f"invented credit threshold {amount} is not in CREDIT-POLICY-3.2"
            )


def invent_exception_criteria(rule_id: str) -> None:
    raise PolicyFidelityError(
        f"{rule_id} criterion is not stated in CREDIT-POLICY-3.2; do not invent it"
    )


def invent_delegated_authority(amount_inr: int) -> None:
    allowed = KNOWN_RULE_BINDINGS["AUTH-LIMIT-01"]["amount_inr"]
    if amount_inr != allowed:
        raise PolicyFidelityError(
            f"delegated-authority cutoff {amount_inr} is not in CREDIT-POLICY-3.2"
        )
    raise PolicyFidelityError(
        "CREDIT-POLICY-3.2 states CREDIT_AUTHORITY above INR 5000000; "
        "it does not grant AI or analyst delegated approval"
    )
