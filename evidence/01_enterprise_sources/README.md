# Enterprise Source Layer — Evidence Pack

This directory intentionally contains **heterogeneous, partially conflicting evidence**. Participants must not flatten it into one table before understanding authority, semantics, freshness, tenant boundaries and provenance.

The original 160-row `historical_applications.csv` is preserved from the supplied case. Its computed workshop profile is in `workshop_fixture_profile.json`. The larger operating benchmark from the original case is separately preserved in `source_case_baseline.json`; it must **not** be presented as if it were calculated from the 160-row fixture.

## Live workshop scenario set

`live_applications.csv` contains 15 deterministic applications linked to GS-01 ... GS-15. Companion sources simulate LOS, documents, bureau, bank data, tax/GST, exposure, policy and source health.

## Deliberate complications

- SME-L004: organization identity differs across LOS, bureau and tax sources.
- SME-L005: bank feed is stale.
- SME-L006: bureau report unavailable.
- SME-L008: belongs to another tenant.
- SME-L009: uploaded document contains prompt-injection text.
- SME-L011: bank-derived and tax-declared revenue materially conflict.
- SME-L012: superseded policy exists in the document corpus.
- SME-L010: AI assistance is unavailable and manual continuity is required.

These are design inputs, not bugs to erase.
