#!/usr/bin/env python3
from pathlib import Path
import csv,json,sys,statistics
import yaml
ROOT=Path(__file__).resolve().parents[1]
checks=[]; errors=[]; warnings=[]
def ok(name,cond,detail=''):
    checks.append((name,bool(cond),detail))
    if not cond: errors.append(f'{name}: {detail}')
def csvrows(p):
    with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def jsonl(p): return [json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
# required files
required=['README.md','START_HERE.md','Participant_Case_Study_Context_Aware_AI_FDE.md','Participant_Case_Study_Context_Aware_AI_FDE.docx','Participant_Runbook.md','Learning_Objectives_and_Expected_Deliverables.md','google_ai_build/01_PRD_GENERATION_PROMPT.md','google_ai_build/02_GOOGLE_AI_BUILD_MASTER_PROMPT.md','google_ai_build/06_app_fixture_bundle.json','evidence/06_evaluations/golden_scenarios.json']
for f in required: ok('required:'+f,(ROOT/f).exists(),f+' missing')
# evidence counts
live=csvrows(ROOT/'evidence/01_enterprise_sources/live_applications.csv'); ok('live_app_count',len(live)==15,str(len(live)))
ids={r['application_id'] for r in live}; ok('unique_live_apps',len(ids)==15,'duplicate IDs')
gs=json.loads((ROOT/'evidence/06_evaluations/golden_scenarios.json').read_text()); ok('golden_count',len(gs)==15,str(len(gs)))
ok('golden_ids',[x['scenario_id'] for x in gs]==[f'GS-{i:02d}' for i in range(1,16)],'scenario sequence mismatch')
ok('golden_apps',all(x['application_id'] in ids for x in gs),'unknown application in golden scenarios')
ok('concrete_behaviors',all('Participants must define' not in x['expected_behavior'] and len(x['expected_behavior'])>60 for x in gs),'placeholder expected behavior remains')
# source fixture traps
bank=jsonl(ROOT/'evidence/01_enterprise_sources/bank_financial_summaries.jsonl')
ok('GS05_stale_bank',any(x['application_id']=='SME-L005' and int(x['freshness_days'])==12 for x in bank),'stale bank trap missing')
bur=jsonl(ROOT/'evidence/01_enterprise_sources/bureau_reports.jsonl')
ok('GS06_no_bureau',not any(x['application_id']=='SME-L006' for x in bur),'SME-L006 should have no bureau record')
docs=jsonl(ROOT/'evidence/01_enterprise_sources/documents_received.jsonl')
ok('GS09_prompt_injection',any(x['application_id']=='SME-L009' and 'Ignore previous policies' in x['text_excerpt'] for x in docs),'prompt injection text missing')
tax=jsonl(ROOT/'evidence/01_enterprise_sources/tax_gst_records.jsonl')
b11=next(x for x in bank if x['application_id']=='SME-L011'); t11=next(x for x in tax if x['application_id']=='SME-L011')
ratio=float(t11['declared_turnover'])/float(b11['twelve_month_inflows']); ok('GS11_financial_conflict',ratio < 0.75 or ratio > 1.25,f'conflict ratio={ratio:.3f} not material')
health=jsonl(ROOT/'evidence/01_enterprise_sources/source_health_events.jsonl')
ok('GS10_ai_outage',any(x['application_id']=='SME-L010' and x['source']=='AI_ASSIST' and x['state']=='UNAVAILABLE' for x in health),'AI outage missing')
# policy invariants
cons=yaml.safe_load((ROOT/'evidence/04_policy_authority/decision_constraints.yaml').read_text())
rules=' '.join(x['rule'] for x in cons['constraints']).lower()
for phrase,key in [('autonomously approve','credit authority'),('active credit policy','policy'),('cross-tenant','tenant'),('protected or sensitive','sensitive'),('stale or unavailable','freshness'),('untrusted document','prompt injection'),('manual underwriting','fallback'),('automatically rewrite','feedback')]: ok('constraint:'+key,phrase in rules,'missing '+phrase)
roles=csvrows(ROOT/'evidence/04_policy_authority/role_authorization_matrix.csv'); ai=next(x for x in roles if x['role']=='AI_AGENT'); ok('AI_no_final_decision',ai['final_credit_decision']=='NO','AI final decision must be NO'); ok('AI_no_policy_override',ai['override_policy']=='NO','AI policy override must be NO')
# active/superseded
active=(ROOT/'evidence/02_documents/credit_underwriting_policy_v3_2.md').read_text(); old=(ROOT/'evidence/02_documents/superseded_credit_policy_v2_9_REFERENCE_ONLY.md').read_text()
ok('active_policy_status','**Status:** ACTIVE' in active,'active status missing'); ok('superseded_status','**Status:** SUPERSEDED' in old,'superseded status missing')
# original fixture reconciliation
hist=csvrows(ROOT/'evidence/01_enterprise_sources/historical_applications.csv'); stored=json.loads((ROOT/'evidence/01_enterprise_sources/workshop_fixture_profile.json').read_text())
def iv(n): return [int(r[n]) for r in hist]
computed={'rows':len(hist),'median_tat_minutes':statistics.median(iv('tat_minutes')),'p90_tat_minutes':round(sorted(iv('tat_minutes'))[int(0.9*(len(hist)-1))],1),'document_rework_pct':round(100*sum(int(r['document_rework'])==1 for r in hist)/len(hist),3),'manual_lookups_gt3_pct':round(100*sum(int(r['manual_lookups'])>3 for r in hist)/len(hist),3),'median_memo_minutes':statistics.median(iv('memo_minutes')),'policy_exception_pct':round(100*sum(int(r['policy_exception'])==1 for r in hist)/len(hist),3),'source_reference_missing_pct':round(100*sum(int(r['source_reference_missing'])==1 for r in hist)/len(hist),3),'bank_feed_stale_pct':round(100*sum(int(r['bank_feed_stale'])==1 for r in hist)/len(hist),3)}
for k,v in computed.items(): ok('fixture_profile:'+k,stored[k]==v,f'stored={stored[k]} computed={v}')
bench=json.loads((ROOT/'evidence/01_enterprise_sources/source_case_baseline.json').read_text()); ok('benchmark_median_142',bench['median_end_to_end_uncomplicated_case_tat_minutes']==142,'wrong source benchmark'); ok('benchmark_target_30',bench['business_target_uncomplicated_case_tat_minutes_lt']==30,'wrong target')
# no mandatory qwen
for f in ['README.md','START_HERE.md','Participant_Runbook.md','Participant_Case_Study_Context_Aware_AI_FDE.md','google_ai_build/01_PRD_GENERATION_PROMPT.md']:
    ok('no_qwen:'+f,'qwen' not in (ROOT/f).read_text(encoding='utf-8').lower(),'Qwen remains in mandatory core workflow')
# templates
for i in range(1,16): ok(f'template_{i:02d}',any((ROOT/'participant_templates').glob(f'{i:02d}_*')),f'template {i} missing')
# bundle
bundle=json.loads((ROOT/'google_ai_build/06_app_fixture_bundle.json').read_text()); ok('bundle_live_apps',len(bundle['enterprise_sources']['live_applications'])==15,'bundle live mismatch'); ok('bundle_golden',len(bundle['evaluation']['golden_scenarios'])==15,'bundle golden mismatch')
# trace schema
trace=json.loads((ROOT/'participant_templates/10_decision_trace_template.json').read_text());
for fld in ['trace_id','task','application_id','actor','context_snapshot','retrievals','source_evidence','policy_checks','versions','recommendation','concise_rationale','human_decision','outcome']: ok('trace:'+fld,fld in trace,'missing '+fld)
# critical case tokens
case=(ROOT/'Participant_Case_Study_Context_Aware_AI_FDE.md').read_text()
for tok in ['142-minute','648-minute','31.2%','57%','38-minute','8.4%','13.7%','SME-L011','SME-L009','SME-L008','The LLM is not the architecture']:
    ok('case_token:'+tok,tok in case,'missing '+tok)
print(f'Checks: {len(checks)} | Passed: {sum(v for _,v,_ in checks)} | Failed: {len(errors)} | Warnings: {len(warnings)}')
for n,s,d in checks:
    if not s: print('FAIL',n,d)
for x in warnings: print('WARN',x)
if errors:
    print('ERRORS:'); [print('-',e) for e in errors]; sys.exit(1)
print('SANITY CHECK PASSED')
