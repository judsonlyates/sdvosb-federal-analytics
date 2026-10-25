"""Read-only verification of source integrity and preserved A4/A5 results.

Run after the documented offline build from the project root:
    uv run --locked python docs/validation/a5_revision_2026-10-24/check_preserved_results.py
The original-package hashes are evidence, not a substitute for checking the
original ZIP or graded GitHub commit independently.
"""
from pathlib import Path
import hashlib
import json
from sdvosb_federal_analytics.verify_rerun import database_evidence


def main():
    """Compare all frozen sources, nine logical tables, and six result hashes."""
    root=Path(__file__).resolve().parents[3]
    evidence=Path(__file__).resolve().parent
    original=json.loads((evidence/'original_package_file_hashes.json').read_text())
    raw=root/'data/raw/20261011T183300Z'
    docs=json.loads((raw/'manifest.json').read_text())['documents']
    for doc in docs:
        data=(raw/doc['filename']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==doc['sha256'],doc['filename']
        assert len(data)==doc['bytes'],doc['filename']
    actual=database_evidence(root/'data/processed/scorecards.sqlite')
    expected=json.loads((root/'docs/validation/rerun_verification.json').read_text())['first_run']
    assert actual['tables']==expected['tables'],'A4 logical tables differ'
    results=sorted((root/'results').glob('a5_*'))
    assert len(results)==6,'Expected six A5 result files'
    for p in results:
        assert hashlib.sha256(p.read_bytes()).hexdigest()==original[str(p.relative_to(root))],p.name
    print(json.dumps({'status':'pass','frozen_sources':len(docs),'preserved_A4_tables':len(actual['tables']),'unchanged_A5_result_files':len(results)},indent=2))


if __name__=='__main__':
    main()
