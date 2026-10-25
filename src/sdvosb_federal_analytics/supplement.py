"""Build a separate, reproducible SQLite supplement from the frozen SBA snapshot.

This module does not mutate any table or byte of the graded A4 database.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile

from .etl import ROOT, ALIASES

MISSING = {'', 'n/a', 'na', 'none', 'null', 'not available', '--', '—'}


def number(value: object, *, integer: bool = False) -> float | int | None:
    """Normalize SBA display numbers, keeping missing different from zero."""
    if value is None or str(value).strip().lower() in MISSING:
        return None
    s = str(value).strip().replace(',', '').removesuffix('%').strip()
    try:
        n = Decimal(s)
    except InvalidOperation as exc:
        raise ValueError(f'Unrecognized SBA number: {value!r}') from exc
    if not n.is_finite():
        raise ValueError(f'Nonfinite SBA number: {value!r}')
    if integer:
        if n != n.to_integral_value() or n < 0:
            raise ValueError(f'Invalid contractor count: {value!r}')
        return int(n)
    return float(n)


def _source_manifest(raw_dir: Path) -> dict[str, dict]:
    """Load the frozen-source manifest and verify every annual JSON file against it.

    Each FY2021-FY2025 scorecard file is re-hashed and compared with the SHA-256
    recorded in ``manifest.json``; a mismatch raises ``ValueError`` so the
    supplementary tables can never be built from an altered source.
    """
    manifest = json.loads((raw_dir / 'manifest.json').read_text(encoding='utf-8'))
    docs = {x['filename']: x for x in manifest['documents']}
    for year in range(2021, 2026):
        filename = f'agency-scorecards-{year}.json'
        doc = docs[filename]
        contents = (raw_dir / filename).read_bytes()
        if hashlib.sha256(contents).hexdigest() != doc['sha256']:
            raise ValueError(f'Frozen source hash mismatch: {filename}')
    return docs


def _load_agencies(a4_db: Path) -> set[str]:
    """Return the 24 agency identifiers from the graded A4 database after sanity checks.

    Refuses to proceed if the database fails ``PRAGMA integrity_check`` or does
    not hold the approved 24-agency, 144-row panel, so the supplement is always
    keyed to the same agency set Lambert graded.
    """
    with sqlite3.connect(f'file:{a4_db.resolve()}?mode=ro',uri=True) as db:
        agencies = {r[0] for r in db.execute('SELECT agency_id FROM agencies')}
        count = db.execute('SELECT COUNT(*) FROM scorecard_observations').fetchone()[0]
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('A4 database fails integrity check')
    if len(agencies) != 24 or count != 144:
        raise ValueError('A4 database is not the approved 24-agency, six-year panel')
    return agencies


def extract(raw_dir: Path, a4_db: Path) -> tuple[list[dict], list[dict], dict]:
    """Extract all five historical editions with cross-edition checks and traceability."""
    docs = _source_manifest(raw_dir)
    agencies = _load_agencies(a4_db)
    old = defaultdict(list)
    current = defaultdict(list)
    excluded_gw = 0
    for edition in range(2021, 2026):
        filename = f'agency-scorecards-{edition}.json'
        records = json.loads((raw_dir / filename).read_text(encoding='utf-8'))
        found = set()
        for item in records:
            ident = item['department_acronym']
            if ident == 'GW':
                excluded_gw += 1
                continue
            ident = ALIASES.get(ident, ident)
            if ident not in agencies:
                raise ValueError(f'Unknown SBA agency in {filename}: {ident}')
            if ident in found:
                raise ValueError(f'Duplicate agency in {filename}: {ident}')
            found.add(ident)
            for delta in range(5):
                field = 'prime_sdvosb_cfy_achievement' if delta == 0 else (
                    'prime_sdvosb_pfy_achievement' if delta == 1 else f'prime_sdvosb_pfy{delta}_achievement'
                )
                fy = edition - delta
                old[ident, fy].append(dict(source_fy=edition, value=number(item[field]),
                                           source_field=field, source_sha256=docs[filename]['sha256']))
            counts = {'sdvosb':number(item['category_sdvosb_cfy_vendor_count'],integer=True),
                      'all_small':number(item['category_sb_cfy_vendor_count'],integer=True)}
            if edition == 2021:
                prior = {'sdvosb':number(item['category_sdvosb_pfy_vendor_count'],integer=True),
                         'all_small':number(item['category_sb_pfy_vendor_count'],integer=True)}
                current[ident, 2020].append(dict(source_fy=edition, source_field='pfy',source_sha256=docs[filename]['sha256'],**prior))
            current[ident, edition].append(dict(source_fy=edition, source_field='cfy',source_sha256=docs[filename]['sha256'],**counts))
        if found != agencies:
            raise ValueError(f'Missing agency in {filename}: {agencies-found}')
    if excluded_gw != 5:
        raise ValueError(f'Expected exactly 5 excluded government-wide rows; got {excluded_gw}')
    hist = []
    checks = 0
    for (ident,fy), series in sorted(old.items()):
        if fy < 2017 or fy > 2025:
            continue
        values = {r['value'] for r in series}
        if len(values) != 1:
            raise ValueError(f'SBA historical restatement conflict: {ident} {fy}: {series}')
        chosen = max(series, key=lambda d:d['source_fy'])
        checks += len(series)-1
        hist.append(dict(agency_id=ident,observation_fy=fy,achievement_pct=chosen['value'],
                         source_fy=chosen['source_fy'],source_field=chosen['source_field'],
                         source_sha256=chosen['source_sha256'],edition_count=len(series)))
    vendors=[]
    for (ident,fy), series in sorted(current.items()):
        if len(series)!=1:
            raise ValueError(f'Expected exactly one current-count source for {ident} {fy}')
        r=series[0]
        a,b=r['sdvosb'],r['all_small']
        if a is not None and b is not None and a>b:
            raise ValueError(f'SDVOSB count exceeds all small-business count: {ident} {fy}')
        if (a is None) != (b is None):
            raise ValueError(f'Partial missingness in vendor counts for {ident} {fy}')
        vendors.append(dict(agency_id=ident,observation_fy=fy,sdvosb_prime_contractor_count=a,
                            all_small_business_prime_contractor_count=b,
                            sdvosb_to_small_business_ratio=a/b if b else None,
                            source_fy=r['source_fy'],source_field=r['source_field'],
                            source_sha256=r['source_sha256']))
    # Cross-check all overlapping vendor prior-year counts against original current-year series.
    by_vendor={(r['agency_id'],r['observation_fy']):r for r in vendors}
    vendor_checks=0
    for edition in range(2022,2026):
        records=json.loads((raw_dir / f'agency-scorecards-{edition}.json').read_text(encoding='utf-8'))
        for item in records:
            ident=ALIASES.get(item['department_acronym'],item['department_acronym'])
            if ident=='GW':continue
            r=by_vendor[ident,edition-1]
            for key,field in [('sdvosb_prime_contractor_count','category_sdvosb_pfy_vendor_count'),
                              ('all_small_business_prime_contractor_count','category_sb_pfy_vendor_count')]:
                if r[key]!=number(item[field],integer=True):
                    raise ValueError(f'Historical vendor count mismatch: {ident} FY{edition-1} {field}')
                vendor_checks+=1
    # Numerical parity for all years already present in approved A4 database.
    with sqlite3.connect(f'file:{a4_db.resolve()}?mode=ro',uri=True) as db:
        current_y={(a,y):value for a,y,value in db.execute(
            'SELECT agency_id,observation_fy,sdvosb_prime_achievement_pct FROM scorecard_observations')}
    for r in hist:
        key=(r['agency_id'],r['observation_fy'])
        if key in current_y and current_y[key]!=r['achievement_pct']:
            raise ValueError(f'Supplement/A4 disagreement in achievement: {key}')
    if len(hist)!=216 or len(vendors)!=144:
        raise ValueError(f'Unexpected historical/vendor coverage: {len(hist)}, {len(vendors)}')
    report={'historical_rows':len(hist),'historical_numeric_count':sum(x['achievement_pct'] is not None for x in hist),
            'vendor_rows':len(vendors),'vendor_numeric_count':sum(x['sdvosb_prime_contractor_count'] is not None for x in vendors),
            'historical_overlap_checks':checks,'vendor_overlap_checks':vendor_checks,'excluded_gw_rows':excluded_gw,
            'source_sha256s':{f'agency-scorecards-{y}.json': docs[f'agency-scorecards-{y}.json']['sha256'] for y in range(2021,2026)}}
    return hist,vendors,report


def write_database(destination: Path, hist: list[dict], vendors: list[dict]) -> None:
    """Atomically publish an independent SQLite supplement with provenance FKs."""
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix='a5-',suffix='.sqlite',dir=destination.parent,delete=False) as fh:
        temporary=Path(fh.name)
    try:
        with sqlite3.connect(temporary) as db:
            db.execute('PRAGMA foreign_keys=ON')
            db.executescript('''
                CREATE TABLE historical_achievement (
                    agency_id TEXT NOT NULL,observation_fy INTEGER NOT NULL,
                    achievement_pct REAL,source_fy INTEGER NOT NULL,
                    source_field TEXT NOT NULL,source_sha256 TEXT NOT NULL,
                    edition_count INTEGER NOT NULL CHECK(edition_count >= 1),
                    PRIMARY KEY(agency_id,observation_fy),
                    CHECK(observation_fy BETWEEN 2017 AND 2025));
                CREATE TABLE vendor_counts (
                    agency_id TEXT NOT NULL,observation_fy INTEGER NOT NULL,
                    sdvosb_prime_contractor_count INTEGER CHECK(sdvosb_prime_contractor_count >= 0),
                    all_small_business_prime_contractor_count INTEGER CHECK(all_small_business_prime_contractor_count >= 0),
                    sdvosb_to_small_business_ratio REAL CHECK(sdvosb_to_small_business_ratio BETWEEN 0 AND 1),
                    source_fy INTEGER NOT NULL,source_field TEXT NOT NULL,source_sha256 TEXT NOT NULL,
                    PRIMARY KEY(agency_id,observation_fy),
                    CHECK(observation_fy BETWEEN 2020 AND 2025));
            ''')
            db.executemany('INSERT INTO historical_achievement VALUES (?,?,?,?,?,?,?)',[
                (r['agency_id'],r['observation_fy'],r['achievement_pct'],r['source_fy'],r['source_field'],r['source_sha256'],r['edition_count']) for r in hist])
            db.executemany('INSERT INTO vendor_counts VALUES (?,?,?,?,?,?,?,?)',[
                (r['agency_id'],r['observation_fy'],r['sdvosb_prime_contractor_count'],r['all_small_business_prime_contractor_count'],
                r['sdvosb_to_small_business_ratio'],r['source_fy'],r['source_field'],r['source_sha256']) for r in vendors])
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
                raise ValueError('Supplement database integrity failure')
            db.commit()
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def logical_hashes(database: Path) -> dict:
    """Hash sorted table records so SQLite engine and physical layout do not matter."""
    result={}
    with sqlite3.connect(database) as db:
        for table in ('historical_achievement','vendor_counts'):
            all_rows=sorted(db.execute(f'SELECT * FROM {table}').fetchall(),key=repr)
            payload=json.dumps(all_rows,ensure_ascii=False,separators=(',',':')).encode()
            result[table]={'rows':len(all_rows),'sha256':hashlib.sha256(payload).hexdigest()}
    return result


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point: build ``analysis.sqlite`` from the frozen JSON files.

    Extracts the FY2017-FY2025 historical achievement series and the FY2020-FY2025
    SDVOSB prime-contractor counts, validates them, and writes them to a separate
    database so the graded A4 database is never modified. Returns an exit code.
    """
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw-dir',type=Path,default=ROOT/'data/raw/20261011T183300Z')
    ap.add_argument('--a4-db',type=Path,default=ROOT/'data/processed/scorecards.sqlite')
    ap.add_argument('--output',type=Path,default=ROOT/'data/processed/analysis.sqlite')
    args=ap.parse_args(argv)
    report_path=args.output.parent/'a5_supplement_validation.json'
    paths=(args.a4_db,args.output,report_path)
    for i,left in enumerate(paths):
        for right in paths[i+1:]:
            if left.resolve()==right.resolve() or (left.exists() and right.exists() and left.samefile(right)):
                raise ValueError('A4 input, supplement output, and validation report must differ')
    hist, vendors, report=extract(args.raw_dir,args.a4_db)
    outputs=[]
    for i in range(2):
        write_database(args.output,hist,vendors)
        outputs.append(logical_hashes(args.output))
    report.update(two_run_identical=outputs[0]==outputs[1],logical_table_hashes=outputs[0])
    if not report['two_run_identical']:
        raise RuntimeError('Analysis supplement rerun mismatch')
    report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='source_sha256s'},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
