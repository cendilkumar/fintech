"""CRD-DATA-001 material evidence envelopes and CRD-AC-011 conflict handling.

Loads live workshop fixtures. Does not invent missing bureau/bank facts or
blend bank inflow with tax turnover.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from .identity import IdentityResolution, resolve_application_identity
from .model import (
    ExceptionClass,
    ExceptionRecord,
    MeasureKind,
    SemanticCollapseError,
)

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence" / "01_enterprise_sources"

WORKSHOP_RETRIEVAL_TIME = "2026-09-15T10:00:00+05:30"
# GS-11 / sanity_check construction — visibility rule, not a credit threshold.
MATERIAL_RATIO_LOW = 0.75
MATERIAL_RATIO_HIGH = 1.25
BANK_STALE_AFTER_DAYS = 7
BUREAU_STALE_AFTER_DAYS = 30
EXPOSURE_STALE_AFTER_MINUTES = 15

SOURCE_AUTHORITY = {
    "LOS": "authoritative",
    "BANK": "authoritative",
    "TAX": "authoritative",
    "BUREAU": "authoritative",
    "EXPOSURE": "authoritative",
}

REQUIRED_ENVELOPE_FIELDS = (
    "evidence_id",
    "source_system",
    "source_record_id",
    "entity_ref",
    "semantic_type",
    "value",
    "authority",
    "period",
    "event_time",
    "update_time",
    "retrieval_time",
    "freshness_state",
    "version",
    "consent_status",
    "purpose",
    "derivation_confidence",
    "conflict_state",
    "access_scope",
    "provenance",
)


def _rows_csv(name: str) -> list[dict[str, str]]:
    with (EVIDENCE / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _rows_jsonl(name: str) -> list[dict[str, Any]]:
    path = EVIDENCE / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


@dataclass
class MaterialEvidence:
    evidence_id: str
    source_system: str
    source_record_id: str
    entity_ref: str
    semantic_type: str
    value: Any
    authority: str
    period: str
    event_time: str
    update_time: str
    retrieval_time: str
    freshness_state: str
    version: str
    consent_status: str
    purpose: str
    derivation_confidence: float | None
    conflict_state: str
    access_scope: str
    provenance: str
    application_id: str
    tenant_id: str

    def as_dict(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in REQUIRED_ENVELOPE_FIELDS}

    def missing_fields(self) -> list[str]:
        missing = []
        for name in REQUIRED_ENVELOPE_FIELDS:
            val = getattr(self, name)
            if name == "derivation_confidence":
                continue
            if name == "value" and self.freshness_state == "unavailable":
                continue
            if val is None or val == "":
                missing.append(name)
        return missing


@dataclass
class FinancialConflict:
    application_id: str
    left_evidence_id: str
    right_evidence_id: str
    left_semantic_type: str
    right_semantic_type: str
    left_value: float
    right_value: float
    left_authority: str
    right_authority: str
    left_source: str
    right_source: str
    conflict_state: str
    exception_class: str
    human_reconciliation_required: bool
    blended_value: None = None

    def average(self) -> float:
        raise SemanticCollapseError(
            "cannot average contradictory financial facts "
            f"{self.left_semantic_type}={self.left_value} and "
            f"{self.right_semantic_type}={self.right_value} (CRD-AC-011)"
        )

    def choose_one(self) -> float:
        raise SemanticCollapseError(
            "cannot silently choose one contradictory financial fact (CRD-AC-011)"
        )


@dataclass
class ApplicationEvidencePack:
    application_id: str
    tenant_id: str
    retrieval_time: str
    facts: list[MaterialEvidence] = field(default_factory=list)
    conflicts: list[FinancialConflict] = field(default_factory=list)
    exceptions: list[ExceptionRecord] = field(default_factory=list)
    policy_result: str | None = None
    policy_version: str | None = None
    identity: IdentityResolution | None = None

    def facts_for(self, source_system: str) -> list[MaterialEvidence]:
        return [f for f in self.facts if f.source_system == source_system]

    def fact(self, semantic_type: str) -> MaterialEvidence:
        matches = [f for f in self.facts if f.semantic_type == semantic_type]
        if len(matches) != 1:
            raise SemanticCollapseError(f"expected one fact of type {semantic_type}, found {len(matches)}")
        return matches[0]

    def blended_revenue(self) -> float:
        raise SemanticCollapseError("no blended revenue measure exists (SC-04 / CRD-AC-011)")


def _freshness_from_days(days: int | None, limit: int) -> str:
    if days is None:
        return "unknown"
    return "stale" if days > limit else "fresh"


def _exposure_freshness(update_time: str, retrieval_time: str) -> str:
    age = _parse_dt(retrieval_time) - _parse_dt(update_time)
    return "stale" if age > timedelta(minutes=EXPOSURE_STALE_AFTER_MINUTES) else "fresh"


def _primary_entity_ref(resolution: IdentityResolution) -> str:
    return resolution.safe_entity_ref()


def _envelope(**kwargs: Any) -> MaterialEvidence:
    fact = MaterialEvidence(**kwargs)
    missing = fact.missing_fields()
    if missing:
        raise SemanticCollapseError(f"incomplete evidence envelope {fact.evidence_id}: {missing}")
    return fact


def _los_facts(application_id: str, retrieval_time: str, entity_ref: str) -> list[MaterialEvidence]:
    app = next(r for r in _rows_csv("live_applications.csv") if r["application_id"] == application_id)
    tenant = app["tenant_id"]
    submitted = app["submitted_at"]
    common = dict(
        entity_ref=entity_ref,
        retrieval_time=retrieval_time,
        application_id=application_id,
        tenant_id=tenant,
        access_scope=tenant,
        authority=SOURCE_AUTHORITY["LOS"],
        consent_status="UNKNOWN",
        purpose="UNDERWRITING_RUNTIME",
        derivation_confidence=None,
        conflict_state="none",
        freshness_state="fresh",
        period=submitted[:10],
        event_time=submitted,
        update_time=submitted,
        version="los-live",
    )
    return [
        _envelope(
            evidence_id=f"LOS:{application_id}:requested_limit",
            source_system="LOS",
            source_record_id=application_id,
            semantic_type="RequestedLimit",
            value=float(app["requested_limit"]),
            provenance=f"live_applications.csv:{application_id}:requested_limit",
            **common,
        ),
        _envelope(
            evidence_id=f"LOS:{application_id}:workflow_state",
            source_system="LOS",
            source_record_id=application_id,
            semantic_type="Application.workflow_status",
            value=app["status"],
            provenance=f"live_applications.csv:{application_id}:status",
            **common,
        ),
    ]


def _bank_facts(application_id: str, retrieval_time: str, entity_ref: str) -> list[MaterialEvidence]:
    rows = [r for r in _rows_jsonl("bank_financial_summaries.jsonl") if r["application_id"] == application_id]
    facts: list[MaterialEvidence] = []
    for row in rows:
        days = int(row["freshness_days"])
        common = dict(
            entity_ref=entity_ref,
            retrieval_time=retrieval_time,
            application_id=application_id,
            tenant_id=row["tenant_id"],
            access_scope=row["tenant_id"],
            authority=SOURCE_AUTHORITY["BANK"],
            consent_status=row["consent_status"],
            purpose=row["purpose"],
            derivation_confidence=None,
            conflict_state="none",
            freshness_state=_freshness_from_days(days, BANK_STALE_AFTER_DAYS),
            period=f"12m_ending_{row['as_of_date']}",
            event_time=row["as_of_date"],
            update_time=row["source_update_time"],
            version=row["as_of_date"],
            source_system="BANK",
            source_record_id=row["bank_summary_id"],
        )
        facts.append(
            _envelope(
                evidence_id=f"{row['bank_summary_id']}:BANK_INFLOWS_12M",
                semantic_type=MeasureKind.BANK_INFLOWS_12M.value,
                value=float(row["twelve_month_inflows"]),
                provenance=f"bank_financial_summaries.jsonl:{row['bank_summary_id']}:twelve_month_inflows",
                **common,
            )
        )
        facts.append(
            _envelope(
                evidence_id=f"{row['bank_summary_id']}:BANK_OUTFLOWS_12M",
                semantic_type=MeasureKind.BANK_OUTFLOWS_12M.value,
                value=float(row["twelve_month_outflows"]),
                provenance=f"bank_financial_summaries.jsonl:{row['bank_summary_id']}:twelve_month_outflows",
                **common,
            )
        )
    return facts


def _tax_facts(application_id: str, retrieval_time: str, entity_ref: str) -> list[MaterialEvidence]:
    rows = [r for r in _rows_jsonl("tax_gst_records.jsonl") if r["application_id"] == application_id]
    facts: list[MaterialEvidence] = []
    for row in rows:
        facts.append(
            _envelope(
                evidence_id=f"{row['tax_record_id']}:TAX_DECLARED_TURNOVER",
                source_system="TAX",
                source_record_id=row["tax_record_id"],
                entity_ref=entity_ref,
                semantic_type=MeasureKind.TAX_DECLARED_TURNOVER.value,
                value=float(row["declared_turnover"]),
                authority=SOURCE_AUTHORITY["TAX"],
                period=row["filing_period"],
                event_time=row["source_update_time"],
                update_time=row["source_update_time"],
                retrieval_time=retrieval_time,
                freshness_state="fresh" if row["filing_status"] == "FILED" else "unknown",
                version=row["filing_period"],
                consent_status=row["reuse_status"],
                purpose="UNDERWRITING_RUNTIME",
                derivation_confidence=None,
                conflict_state="none",
                access_scope=row["tenant_id"],
                provenance=f"tax_gst_records.jsonl:{row['tax_record_id']}:declared_turnover",
                application_id=application_id,
                tenant_id=row["tenant_id"],
            )
        )
    return facts


def _bureau_facts(application_id: str, retrieval_time: str, entity_ref: str) -> list[MaterialEvidence]:
    rows = [r for r in _rows_jsonl("bureau_reports.jsonl") if r["application_id"] == application_id]
    if not rows:
        return [
            _envelope(
                evidence_id=f"BUREAU:{application_id}:UNAVAILABLE",
                source_system="BUREAU",
                source_record_id="NONE",
                entity_ref=entity_ref,
                semantic_type="BureauRecord",
                value=None,
                authority=SOURCE_AUTHORITY["BUREAU"],
                period="unavailable",
                event_time=retrieval_time,
                update_time=retrieval_time,
                retrieval_time=retrieval_time,
                freshness_state="unavailable",
                version="none",
                consent_status="UNKNOWN",
                purpose="UNDERWRITING_VERIFIED",
                derivation_confidence=None,
                conflict_state="none",
                access_scope="unknown",
                provenance=f"bureau_reports.jsonl:{application_id}:missing",
                application_id=application_id,
                tenant_id="unknown",
            )
        ]
    facts: list[MaterialEvidence] = []
    for row in rows:
        days = int(row["freshness_days"])
        facts.append(
            _envelope(
                evidence_id=f"{row['bureau_report_id']}:score_band",
                source_system="BUREAU",
                source_record_id=row["bureau_report_id"],
                entity_ref=entity_ref,
                semantic_type="BureauRecord.score_band",
                value=row["commercial_score_band"],
                authority=SOURCE_AUTHORITY["BUREAU"],
                period=row["as_of_date"],
                event_time=row["as_of_date"],
                update_time=row["source_update_time"],
                retrieval_time=retrieval_time,
                freshness_state=_freshness_from_days(days, BUREAU_STALE_AFTER_DAYS),
                version=row["as_of_date"],
                consent_status="VALID",
                purpose=row["permissible_purpose"],
                derivation_confidence=None,
                conflict_state="none",
                access_scope=row["tenant_id"],
                provenance=f"bureau_reports.jsonl:{row['bureau_report_id']}:commercial_score_band",
                application_id=application_id,
                tenant_id=row["tenant_id"],
            )
        )
    return facts


def _exposure_facts(application_id: str, retrieval_time: str, entity_ref: str) -> list[MaterialEvidence]:
    rows = [r for r in _rows_csv("exposure_records.csv") if r["application_id"] == application_id]
    facts: list[MaterialEvidence] = []
    for row in rows:
        common = dict(
            entity_ref=entity_ref,
            retrieval_time=retrieval_time,
            application_id=application_id,
            tenant_id=row["tenant_id"],
            access_scope=row["tenant_id"],
            authority=SOURCE_AUTHORITY["EXPOSURE"],
            consent_status="NOT_APPLICABLE",
            purpose="UNDERWRITING_RUNTIME",
            derivation_confidence=None,
            conflict_state="none",
            freshness_state=_exposure_freshness(row["source_update_time"], retrieval_time),
            period=row["source_update_time"][:10],
            event_time=row["source_update_time"],
            update_time=row["source_update_time"],
            version=row["source_update_time"],
            source_system="EXPOSURE",
            source_record_id=row["exposure_id"],
        )
        facts.append(
            _envelope(
                evidence_id=f"{row['exposure_id']}:INTERNAL_EXISTING_EXPOSURE",
                semantic_type=MeasureKind.INTERNAL_EXISTING_EXPOSURE.value,
                value=float(row["existing_exposure"]),
                provenance=f"exposure_records.csv:{row['exposure_id']}:existing_exposure",
                **common,
            )
        )
        facts.append(
            _envelope(
                evidence_id=f"{row['exposure_id']}:INTERNAL_APPROVED_LIMIT",
                semantic_type=MeasureKind.INTERNAL_APPROVED_LIMIT.value,
                value=float(row["approved_limit_current"]),
                provenance=f"exposure_records.csv:{row['exposure_id']}:approved_limit_current",
                **common,
            )
        )
        facts.append(
            _envelope(
                evidence_id=f"{row['exposure_id']}:INTERNAL_PAST_DUE",
                semantic_type=MeasureKind.INTERNAL_PAST_DUE.value,
                value=float(row["past_due_amount"]),
                provenance=f"exposure_records.csv:{row['exposure_id']}:past_due_amount",
                **common,
            )
        )
    return facts


def _material_disagreement(left: float, right: float) -> bool:
    if left == 0 or right == 0:
        return True
    ratio = right / left
    return ratio < MATERIAL_RATIO_LOW or ratio > MATERIAL_RATIO_HIGH


def detect_financial_conflicts(facts: Iterable[MaterialEvidence]) -> list[FinancialConflict]:
    facts = list(facts)
    inflows = [f for f in facts if f.semantic_type == MeasureKind.BANK_INFLOWS_12M.value]
    turnovers = [f for f in facts if f.semantic_type == MeasureKind.TAX_DECLARED_TURNOVER.value]
    conflicts: list[FinancialConflict] = []
    for bank in inflows:
        for tax in turnovers:
            if bank.application_id != tax.application_id:
                continue
            if not _material_disagreement(float(bank.value), float(tax.value)):
                continue
            bank.conflict_state = "unresolved"
            tax.conflict_state = "unresolved"
            conflicts.append(
                FinancialConflict(
                    application_id=bank.application_id,
                    left_evidence_id=bank.evidence_id,
                    right_evidence_id=tax.evidence_id,
                    left_semantic_type=bank.semantic_type,
                    right_semantic_type=tax.semantic_type,
                    left_value=float(bank.value),
                    right_value=float(tax.value),
                    left_authority=bank.authority,
                    right_authority=tax.authority,
                    left_source=bank.source_system,
                    right_source=tax.source_system,
                    conflict_state="unresolved",
                    exception_class=ExceptionClass.FINANCIAL_CONFLICT.value,
                    human_reconciliation_required=True,
                    blended_value=None,
                )
            )
    return conflicts


def assemble_application_evidence(
    application_id: str,
    retrieval_time: str = WORKSHOP_RETRIEVAL_TIME,
) -> ApplicationEvidencePack:
    app = next(r for r in _rows_csv("live_applications.csv") if r["application_id"] == application_id)
    identity = resolve_application_identity(application_id)
    entity_ref = _primary_entity_ref(identity)
    facts = []
    facts.extend(_los_facts(application_id, retrieval_time, entity_ref))
    facts.extend(_bank_facts(application_id, retrieval_time, entity_ref))
    facts.extend(_tax_facts(application_id, retrieval_time, entity_ref))
    facts.extend(_bureau_facts(application_id, retrieval_time, entity_ref))
    facts.extend(_exposure_facts(application_id, retrieval_time, entity_ref))
    conflicts = detect_financial_conflicts(facts)
    exceptions = [
        ExceptionRecord(
            exception_class=ExceptionClass.FINANCIAL_CONFLICT,
            application_id=application_id,
            detail=f"{c.left_semantic_type}={c.left_value} vs {c.right_semantic_type}={c.right_value}",
        )
        for c in conflicts
    ]
    exceptions.extend(identity.exceptions)
    policy_rows = [r for r in _rows_jsonl("policy_engine_results.jsonl") if r["application_id"] == application_id]
    policy = policy_rows[0] if policy_rows else None
    return ApplicationEvidencePack(
        application_id=application_id,
        tenant_id=app["tenant_id"],
        retrieval_time=retrieval_time,
        facts=facts,
        conflicts=conflicts,
        exceptions=exceptions,
        policy_result=None if policy is None else policy["result"],
        policy_version=None if policy is None else policy["policy_version"],
        identity=identity,
    )
