from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['AGENTS.md', 'SDD_START_HERE.md', 'SPEC_DRIVEN_DEVELOPMENT.md', 'CURSOR_WORKFLOW.md', 'DEFINITION_OF_READY.md', 'DEFINITION_OF_DONE.md', 'CHANGE_CONTROL.md', '.cursor/rules/00-sdd-core.mdc', '.cursor/rules/10-domain-guardrails.mdc', '.cursor/rules/20-evidence-testing.mdc', '.cursor/rules/30-context-and-change.mdc', '.cursor/commands/sdd-discover.md', '.cursor/commands/sdd-spec.md', '.cursor/commands/sdd-plan.md', '.cursor/commands/sdd-implement.md', '.cursor/commands/sdd-verify.md', '.cursor/commands/sdd-change.md', '.cursor/commands/sdd-review.md', 'specs/00_product/PRD.md', 'specs/01_system/SYSTEM_REQUIREMENTS.md', 'specs/02_features/FEATURE_SPECS.md', 'specs/03_non_functional/NFR.md', 'specs/04_security_privacy/SECURITY_GOVERNANCE.md', 'specs/05_data_contracts/DATA_CONTRACTS.md', 'specs/05_data_contracts/DOMAIN_MODEL.md', 'specs/06_api_contracts/TOOL_CONTRACTS.md', 'specs/07_acceptance/ACCEPTANCE_CRITERIA.md', 'specs/08_traceability/TRACEABILITY_MATRIX.md', 'specs/09_change_requests/CR_TEMPLATE.md', 'tasks/backlog/TASK-001-domain-context.md', 'evidence/sdd/README.md', 'scripts/sdd_validate.py']
PREFIX='CRD'
missing=[p for p in REQUIRED if not (ROOT/p).exists()]
errors=[]
if missing: errors.append('Missing: '+', '.join(missing))
for p in (ROOT/'.cursor/rules').glob('*'):
    if p.is_file() and p.suffix != '.mdc': errors.append(f'Cursor rule must use .mdc: {p.name}')
trace=(ROOT/'specs/08_traceability/TRACEABILITY_MATRIX.md').read_text(encoding='utf-8')
sysreq=(ROOT/'specs/01_system/SYSTEM_REQUIREMENTS.md').read_text(encoding='utf-8')
acc=(ROOT/'specs/07_acceptance/ACCEPTANCE_CRITERIA.md').read_text(encoding='utf-8')
fr=set(re.findall(rf'{PREFIX}-FR-\d{{3}}',sysreq))
ac=set(re.findall(rf'{PREFIX}-AC-\d{{3}}',acc))
for rid in sorted(fr):
    if rid not in trace: errors.append('Traceability missing '+rid)
if len(ac) < 15: errors.append(f'Expected at least 15 acceptance IDs, found {len(ac)}')
legacy=ROOT/'.cursorrules'
if legacy.exists(): errors.append('Legacy .cursorrules present; use .cursor/rules/*.mdc')
if errors:
    print('SDD VALIDATION: FAIL')
    for e in errors: print('-',e)
    sys.exit(1)
print(f'SDD VALIDATION: PASS | files={len(REQUIRED)} | functional_requirements={len(fr)} | acceptance_criteria={len(ac)}')
