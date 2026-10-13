"""Run the complete frozen pipeline twice and prove stable facts and row counts."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sqlite3

from .etl import ROOT, main as run_pipeline, write_json


def database_evidence(path):
    """Hash sorted logical table contents, independent of SQLite file layout."""
    evidence = {}
    with sqlite3.connect(path) as con:
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        for name in names:
            # Names come only from our reviewed schema, not user input.
            rows = sorted(con.execute(f'SELECT * FROM "{name}"').fetchall(), key=repr)
            payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
            evidence[name] = {"row_count": len(rows), "logical_sha256": hashlib.sha256(payload.encode()).hexdigest()}
        duplicates = con.execute("SELECT COUNT(*) FROM (SELECT agency_id, observation_fy FROM scorecard_observations GROUP BY agency_id, observation_fy HAVING COUNT(*) > 1)").fetchone()[0]
        checks = {"integrity": con.execute("PRAGMA integrity_check").fetchone()[0],
                  "foreign_key_violations": len(con.execute("PRAGMA foreign_key_check").fetchall()),
                  "duplicate_fact_keys": duplicates}
    return {"tables": evidence, "checks": checks}


def main(argv=None):
    """Rebuild the same database path twice; report failure if any fact changes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data/raw/20261011T183300Z")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed")
    args = parser.parse_args(argv)
    results = []
    for _ in range(2):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = run_pipeline(["--offline", "--raw-dir", str(args.raw_dir), "--output-dir", str(args.output_dir)])
        if rc:
            return rc
        evidence = database_evidence(args.output_dir / "scorecards.sqlite")
        evidence["exports"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(args.output_dir.glob("*.csv"))}
        results.append(evidence)
    stable = results[0] == results[1]
    report = {"status": "pass" if stable else "fail", "same_database_path": True,
              "identical_logical_records_and_counts": stable,
              "first_run": results[0], "second_run": results[1]}
    write_json(args.output_dir / "rerun_verification.json", report)
    print(json.dumps(report, indent=2))
    return 0 if stable else 1


if __name__ == "__main__":
    raise SystemExit(main())
