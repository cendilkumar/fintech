#!/usr/bin/env python3
import csv, json, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'evidence/01_enterprise_sources/historical_applications.csv'
with P.open(newline='',encoding='utf-8') as f: rows=list(csv.DictReader(f))
def iv(n): return [int(r[n]) for r in rows]
metrics={
 'rows':len(rows),
 'median_tat_minutes':statistics.median(iv('tat_minutes')),
 'p90_tat_minutes':round(sorted(iv('tat_minutes'))[int(0.9*(len(rows)-1))],1),
 'document_rework_pct':round(100*sum(int(r['document_rework'])==1 for r in rows)/len(rows),3),
 'manual_lookups_gt3_pct':round(100*sum(int(r['manual_lookups'])>3 for r in rows)/len(rows),3),
 'median_memo_minutes':statistics.median(iv('memo_minutes')),
 'policy_exception_pct':round(100*sum(int(r['policy_exception'])==1 for r in rows)/len(rows),3),
 'source_reference_missing_pct':round(100*sum(int(r['source_reference_missing'])==1 for r in rows)/len(rows),3),
 'bank_feed_stale_pct':round(100*sum(int(r['bank_feed_stale'])==1 for r in rows)/len(rows),3),
}
print(json.dumps(metrics,indent=2))
