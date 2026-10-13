#!/usr/bin/env python3
"""Validate the collected panel, retaining source-reported negative achievement."""
from decimal import Decimal
from pathlib import Path
import sys
from sdvosb_federal_analytics.etl import read_csv, parse_pct, DataError, NUMERIC, YEARS


def main(path):
    rows=read_csv(Path(path))
    seen=set()
    for r in rows:
        key=(r['agency_id'],int(r['observation_fy']))
        if key in seen: raise DataError(f'Duplicate agency-year: {key}')
        seen.add(key)
        for field in NUMERIC[:2]:
            r[field]=parse_pct(r[field],goal=(field==NUMERIC[1]))
        if r[NUMERIC[2]]:
            if not Decimal(r[NUMERIC[2]]).is_finite(): raise DataError('Non-finite dollar amount')
        if any(r[f] for f in NUMERIC) and not all(r[f] for f in ('source_url','retrieved_date','scorecard_fy')):
            raise DataError(f'Missing source metadata: {key}')
    print(f'{len(rows)} rows; {len({r["agency_id"] for r in rows})} agencies')
    for y in YEARS:
        yr=[r for r in rows if int(r['observation_fy'])==y]
        print(f'FY{y}: '+', '.join(f'{f}={sum(r[f]!="" for r in yr)}/{len(yr)}' for f in NUMERIC))
    exposures=[]
    for a in dict.fromkeys(r['agency_id'] for r in rows):
        base=[r for r in rows if r['agency_id']==a and int(r['observation_fy']) in (2021,2022,2023)]
        post=[r for r in rows if r['agency_id']==a and int(r['observation_fy']) in (2024,2025) and r[NUMERIC[0]]]
        if len(base)==3 and all(r[NUMERIC[0]] for r in base) and post:
            avg=sum(Decimal(r[NUMERIC[0]]) for r in base)/3
            exposures.append((a,avg,max(Decimal(0),Decimal(5)-avg)))
    print(f'Agencies meeting submitted inclusion rule: {len(exposures)}')
    print(f'Positive baseline shortfall: {sum(s>0 for _,_,s in exposures)}; zero shortfall: {sum(s==0 for _,_,s in exposures)}')
    for a,avg,s in sorted(exposures,key=lambda x:x[2],reverse=True): print(f'{a}: FY2021–23 mean={avg:.4f}%; shortfall={s:.4f} percentage points')
    negatives=[r for r in rows if r[NUMERIC[0]] and Decimal(r[NUMERIC[0]])<0]
    print(f'Negative achievements retained and flagged: {len(negatives)}')
    print('No imputation. This check does not establish causal or cross-year measurement comparability.')

if __name__=='__main__':
    try: main(sys.argv[1])
    except (DataError,ValueError,IndexError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr);sys.exit(1)
