# ADR-001 — Use Specs-Driven Development as the Cursor Engineering Contract
**Status:** Accepted for workshop conversion

## Context
The original repository is a rich domain/architecture case. Direct prompting can cause Cursor to infer requirements, collapse ambiguity or optimize for a demo rather than the case's hard controls.

## Decision
Use version-controlled `CRD` requirements, Given/When/Then acceptance criteria, traceability, Cursor project rules, reusable commands and evidence gates. Preserve all original domain artifacts and fixtures.

## Consequences
- More deliberate work before code generation.
- Clear requirement-to-evidence lineage.
- Easier review of AI-generated diffs.
- Intent changes require explicit specification change control.
- The original case remains teachable independently of the SDD layer.
