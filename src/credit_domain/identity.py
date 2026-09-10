"""CRD-FR-003 / CRD-DATA-006 identity resolution.

canonical_candidate on the identifier crosswalk is a hypothesis only.
MATCHED requires agreeing LOS + bureau + tax name and a non-placeholder tax token.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .model import (
    ExceptionClass,
    ExceptionRecord,
    PartyKind,
    ResolutionState,
    SemanticCollapseError,
    party_from_fixture,
)

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence" / "01_enterprise_sources"
SEMANTIC = ROOT / "evidence" / "03_semantic_evidence"

PLACEHOLDER_TAX_TOKENS = frozenset({"TAX-***XX", "TAX-***xx", "UNKNOWN", "XX"})
LEGAL_SUFFIXES = (
    (r"\bprivate\s+limited\b", "pvt ltd"),
    (r"\bpvt\.?\s*ltd\.?\b", "pvt ltd"),
    (r"\blimited\b", "ltd"),
)


class UnsafeIdentityUse(SemanticCollapseError):
    """Raised when an unresolved or ambiguous identity is used as a single entity."""


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _jsonl(name: str) -> list[dict]:
    path = EVIDENCE / name
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def normalize_legal_name(name: str) -> str:
    """Casefold and equate registered-form suffixes only. Do not fold Harbor/Harbour."""
    text = " ".join((name or "").casefold().split())
    text = text.replace(",", " ")
    text = re.sub(r"\b(pvt|ltd)\.", r"\1", text)
    for pattern, repl in LEGAL_SUFFIXES:
        text = re.sub(pattern, repl, text)
    return " ".join(text.split())


def is_placeholder_tax(token: str | None) -> bool:
    return not token or token.strip() in PLACEHOLDER_TAX_TOKENS


@dataclass(frozen=True)
class SourceIdentityObservation:
    application_id: str
    source: str
    source_id: str
    observed_name: str
    tax_token: str
    party_kind: PartyKind | None = None
    canonical_candidate: str | None = None
    match_clue: str = ""

    @property
    def normalized_name(self) -> str:
        return normalize_legal_name(self.observed_name)


@dataclass
class IdentityCluster:
    application_id: str
    cluster_kind: str
    state: ResolutionState
    observations: list[SourceIdentityObservation] = field(default_factory=list)
    hypothesized_candidate: str | None = None
    canonical_party_id: str | None = None
    reasons: list[str] = field(default_factory=list)

    def require_matched_party_id(self) -> str:
        if self.state is not ResolutionState.MATCHED or not self.canonical_party_id:
            raise UnsafeIdentityUse(
                f"{self.application_id} identity is {self.state.value}; "
                "cannot use a single canonical party (CRD-AC-004)"
            )
        return self.canonical_party_id

    def merge_observations(self) -> SourceIdentityObservation:
        raise UnsafeIdentityUse(
            f"cannot silently merge {len(self.observations)} identity observations "
            f"for {self.application_id} (CRD-AC-004)"
        )

    def safe_entity_ref(self) -> str:
        if self.state is ResolutionState.MATCHED and self.canonical_party_id:
            return self.canonical_party_id
        return f"{self.state.value}:{self.application_id}"


@dataclass
class IdentityResolution:
    application_id: str
    organization: IdentityCluster
    natural_persons: list[IdentityCluster] = field(default_factory=list)
    exceptions: list[ExceptionRecord] = field(default_factory=list)

    @property
    def state(self) -> ResolutionState:
        return self.organization.state

    def require_matched_party_id(self) -> str:
        return self.organization.require_matched_party_id()

    def safe_entity_ref(self) -> str:
        return self.organization.safe_entity_ref()

    def person_not_merged_with_organization(self) -> bool:
        org_ids = {o.source_id for o in self.organization.observations}
        for cluster in self.natural_persons:
            if any(obs.source_id in org_ids for obs in cluster.observations):
                return False
            if cluster.canonical_party_id and cluster.canonical_party_id == self.organization.canonical_party_id:
                return False
        return True


def _crosswalk_rows(application_id: str) -> list[dict[str, str]]:
    return [r for r in _csv(SEMANTIC / "identifier_crosswalk.csv") if r["application_id"] == application_id]


def _party_rows(application_id: str) -> list[dict[str, str]]:
    return [r for r in _csv(EVIDENCE / "application_parties.csv") if r["application_id"] == application_id]


def _collect_org_observations(application_id: str) -> list[SourceIdentityObservation]:
    observations: list[SourceIdentityObservation] = []
    for row in _party_rows(application_id):
        party = party_from_fixture(row)
        if party.kind is PartyKind.NATURAL_PERSON:
            continue
        observations.append(
            SourceIdentityObservation(
                application_id=application_id,
                source="LOS",
                source_id=row["source_identifier"],
                observed_name=row["display_name"],
                tax_token=row.get("tax_identifier_token") or "",
                party_kind=party.kind,
                canonical_candidate=None,
                match_clue="LOS party record",
            )
        )
    bureau = next((r for r in _jsonl("bureau_reports.jsonl") if r["application_id"] == application_id), None)
    tax = next((r for r in _jsonl("tax_gst_records.jsonl") if r["application_id"] == application_id), None)
    xwalk = {r["source"]: r for r in _crosswalk_rows(application_id)}
    if bureau:
        observations.append(
            SourceIdentityObservation(
                application_id=application_id,
                source="BUREAU",
                source_id=bureau["bureau_report_id"],
                observed_name=bureau["reported_name"],
                tax_token=(xwalk.get("BUREAU") or {}).get("tax_token") or "",
                party_kind=None,
                canonical_candidate=(xwalk.get("BUREAU") or {}).get("canonical_candidate"),
                match_clue=(xwalk.get("BUREAU") or {}).get("match_clue", "bureau report"),
            )
        )
    if tax:
        observations.append(
            SourceIdentityObservation(
                application_id=application_id,
                source="TAX",
                source_id=tax["tax_record_id"],
                observed_name=tax["reported_name"],
                tax_token=(xwalk.get("TAX") or {}).get("tax_token") or "",
                party_kind=None,
                canonical_candidate=(xwalk.get("TAX") or {}).get("canonical_candidate"),
                match_clue=(xwalk.get("TAX") or {}).get("match_clue", "tax record"),
            )
        )
    return observations


def _collect_person_clusters(application_id: str) -> list[IdentityCluster]:
    clusters: list[IdentityCluster] = []
    for row in _party_rows(application_id):
        party = party_from_fixture(row)
        if party.kind is not PartyKind.NATURAL_PERSON:
            continue
        obs = SourceIdentityObservation(
            application_id=application_id,
            source="LOS",
            source_id=row["source_identifier"],
            observed_name=row["display_name"],
            tax_token=row.get("tax_identifier_token") or "",
            party_kind=PartyKind.NATURAL_PERSON,
            match_clue=row["party_type"],
        )
        clusters.append(
            IdentityCluster(
                application_id=application_id,
                cluster_kind=row["party_type"],
                state=ResolutionState.UNRESOLVED,
                observations=[obs],
                hypothesized_candidate=None,
                canonical_party_id=None,
                reasons=["natural-person cluster is not auto-matched to organization identity"],
            )
        )
    return clusters


def _sources(observations: list[SourceIdentityObservation]) -> set[str]:
    return {o.source for o in observations}


def _names_and_tax_agree(observations: list[SourceIdentityObservation]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    names = {o.normalized_name for o in observations}
    tokens = {o.tax_token for o in observations}
    if len(names) > 1:
        reasons.append(f"legal names disagree after suffix-only normalize: {sorted(names)}")
    if any(is_placeholder_tax(o.tax_token) for o in observations):
        reasons.append("placeholder or missing tax token present")
    if len(tokens) > 1:
        reasons.append(f"tax tokens disagree: {sorted(tokens)}")
    return (len(reasons) == 0, reasons)


def resolve_application_identity(application_id: str) -> IdentityResolution:
    org_obs = _collect_org_observations(application_id)
    xwalk = _crosswalk_rows(application_id)
    hypothesized = next((r["canonical_candidate"] for r in xwalk if r.get("canonical_candidate")), None)
    sources = _sources(org_obs)
    reasons: list[str] = []
    state: ResolutionState
    canonical: str | None = None

    if "BUREAU" not in sources:
        state = ResolutionState.UNRESOLVED
        reasons.append("bureau observation unavailable; cannot resolve organization identity")
    elif "TAX" not in sources or "LOS" not in sources:
        state = ResolutionState.UNRESOLVED
        reasons.append(f"required sources missing: have {sorted(sources)}")
    else:
        agree, disagree_reasons = _names_and_tax_agree(org_obs)
        if agree:
            state = ResolutionState.MATCHED
            los = next(o for o in org_obs if o.source == "LOS")
            party_row = next(
                r
                for r in _party_rows(application_id)
                if r["source_identifier"] == los.source_id
            )
            canonical = party_row["party_id"]
            reasons.append("LOS, bureau and tax agree on normalized name and tax token")
        else:
            state = ResolutionState.AMBIGUOUS
            reasons.extend(disagree_reasons)
            reasons.append("canonical_candidate is a hypothesis and is not MATCHED")

    cluster = IdentityCluster(
        application_id=application_id,
        cluster_kind="ORGANIZATION",
        state=state,
        observations=org_obs,
        hypothesized_candidate=hypothesized,
        canonical_party_id=canonical,
        reasons=reasons,
    )
    persons = _collect_person_clusters(application_id)
    exceptions: list[ExceptionRecord] = []
    if state is not ResolutionState.MATCHED:
        exceptions.append(
            ExceptionRecord(
                exception_class=ExceptionClass.IDENTITY,
                application_id=application_id,
                detail="; ".join(reasons),
            )
        )
    return IdentityResolution(
        application_id=application_id,
        organization=cluster,
        natural_persons=persons,
        exceptions=exceptions,
    )


def resolve_from_observations(
    application_id: str,
    observations: list[SourceIdentityObservation],
    hypothesized_candidate: str | None = None,
) -> IdentityCluster:
    """Deterministic cluster resolve for constructed legal-name / tax tests."""
    sources = _sources(observations)
    if not {"LOS", "BUREAU", "TAX"} <= sources:
        return IdentityCluster(
            application_id=application_id,
            cluster_kind="ORGANIZATION",
            state=ResolutionState.UNRESOLVED,
            observations=observations,
            hypothesized_candidate=hypothesized_candidate,
            reasons=["required LOS/bureau/tax observations missing"],
        )
    agree, reasons = _names_and_tax_agree(observations)
    if agree:
        return IdentityCluster(
            application_id=application_id,
            cluster_kind="ORGANIZATION",
            state=ResolutionState.MATCHED,
            observations=observations,
            hypothesized_candidate=hypothesized_candidate,
            canonical_party_id=None,
            reasons=["constructed observations agree"],
        )
    reasons.append("canonical_candidate is a hypothesis and is not MATCHED")
    return IdentityCluster(
        application_id=application_id,
        cluster_kind="ORGANIZATION",
        state=ResolutionState.AMBIGUOUS,
        observations=observations,
        hypothesized_candidate=hypothesized_candidate,
        reasons=reasons,
    )
