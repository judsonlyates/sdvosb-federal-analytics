# Assignment 4 validation record

Two AI-run check records are kept here, in order. Section A is the preparation run (OpenAI Codex, October 12, 2026, against base commit `d45388d1a5a7ada3bc2960efc19ab697665d0a51`). Section B is the independent Claude review and the final build that produced the evidence files now in `docs/validation/`. Neither asserts that the student ran these commands; the student's own review is recorded in `AI_USE.md`.

## A. Preparation run (October 12, 2026, before the independent review)

### Environment and dependency verification

- Python 3.11.17, installed and selected through UV 0.12.23
- `uv sync --locked`: passed; 103 applicable packages installed
- `uv sync --locked --check`: passed
- pandas 3.0.5, NumPy 2.4.6, pytest 9.1.1, SQLite 3.53.1
- Poppler `pdftotext` 25.03.0
- Original `uv.lock` and dependency requirements remain unchanged

### Commands actually run

```sh
uv sync --locked
uv sync --locked --check
uv run --locked pytest -q
uv run --locked python -m sdvosb_federal_analytics.verify_rerun
uv run --locked python scripts/feasibility_check.py data/processed/sba_scorecard_sdvosb.csv
```

The two-run verifier calls the same end-to-end offline ETL entry point documented in the README. Every command above passed in the stated environment. The writable UV cache/Python-install directories used for this hosted environment are incidental to execution; another student can use UV's normal defaults.

### Automated results

38 tests passed, including 5 parameterized subtests, at that point in preparation (the suite now has 40; see Section B).

Coverage includes numeric parsing, preservation of display units/precision, signed achievement/dollars, N/A versus zero, source-host restrictions, PDF prime-table boundaries, all 55 source hashes, 24-agency/144-key completeness, 143 complete observations, all 48 original sample cells, 336 historical overlap checks, actual goal transitions, aliases, database integrity/NULL behavior, approved baseline/exposure/inclusion logic, invalid constraints, and repeated execution.

Failure tests corrupt a copied JSON snapshot or remove a required agency record, then verify a nonzero result and that the previous database bytes are unchanged. Another test verifies that the collector refuses to overwrite the frozen source directory. No test mutates the committed source fixture.

### Two consecutive complete builds

The pipeline ran twice against the same output database. Every table's sorted logical records and every exported CSV hash matched across runs. Both runs had SQLite integrity `ok`, zero foreign-key violations and zero duplicate fact keys.

| Table | Run 1 rows | Run 2 rows |
|---|---:|---:|
| agencies | 24 | 24 |
| agency_names | 144 | 144 |
| source_documents | 55 | 55 |
| scorecard_observations | 144 | 144 |
| provenance | 144 | 144 |
| quality_flags | 304 | 304 |
| overlap_checks | 336 | 336 |
| sample_reconciliation | 48 | 48 |
| panel_agency_year | 144 | 144 |

Full logical hashes and export hashes are in `validation/rerun_verification.json`. Its equality check is stronger than a row-count check alone.

### Quality and preservation results

- 144 rows, 24 agencies, FY2020–FY2025; 143 complete numerical triples
- USAID FY2025: three source-declared missing cells, retained as SQL NULL
- Zero duplicate records and zero rejected records in the successful frozen build
- All 48 populated numerical sample values match; all 336 historical comparisons match
- 24 agencies have complete FY2021–FY2023 baselines and at least one post year; 143 observation rows qualify for subsequent analysis
- 12 agencies have positive shortfall; 12 have zero shortfall
- HUD negative achievement/dollars are retained; comparability flags remain
- Original A3 sample, proposal and lockfile verified byte-identical to the base copy
- Integrated ten-column CSV equals the prior verified collector output exactly

Machine-readable missingness and action details are in `validation/validation_summary.json`; the feasibility output is in `validation/feasibility.log`.

### Limits and submission status

The assembled online refresh was not rerun against live servers during this integration. The October 11 collector had live source downloads and a simulated-transport full-flow check, while this integration directly re-parsed the frozen sources offline. The earlier collector was independently checked using PDF table geometry; that was AI-assisted verification, not a human audit.

This run tested Linux/Python 3.11.17. Native Windows/macOS execution has not been claimed. Optional R verification has not been run. No other model's agreement is assumed. Passing code/data tests does not resolve measurement comparability, establish a causal effect, or certify a grade.

The working changes still require student review, honest AI-use finalization, real descriptive commits, and an authorized push to the existing repository. No development history was fabricated or backdated.

## B. Independent Claude review and final build (October 12, 2026)

An independent review was run by Claude, which received only the review package (the repository snapshot, the rubric, and the review prompt) and had not seen the preparation audit until after forming its own findings. It extracted the archive into a clean directory and executed everything below in a disposable copy.

### Environment

- Linux; UV 0.11.32; Python 3.11.17 selected by `uv.lock`
- pandas 3.0.5, NumPy 2.4.6, pytest 9.1.1, SQLite library 3.45.1
- Poppler `pdftotext` 24.02.0
- R: not available, so the optional R check was not run

### Commands and results

| Command | Result | Exit |
|---|---|---|
| `uv sync --locked` / `uv sync --locked --check` | 103 packages; "Would make no changes" | 0 / 0 |
| `uv run --locked python -m sdvosb_federal_analytics.etl --offline --raw-dir data/raw/20261011T183300Z` | status `success`; 144 rows, 143 complete, 0 duplicates, 0 rejected, 336/0 overlap conflicts, 48/0 sample conflicts | 0 |
| `uv run --locked pytest -q` | 38 passed + 5 subtests before the fixes below; 40 passed + 5 subtests after | 0 |
| `uv run --locked python -m sdvosb_federal_analytics.verify_rerun` | `pass`; both runs identical | 0 |
| `uv run --locked python scripts/feasibility_check.py data/processed/sba_scorecard_sdvosb.csv` | 24 agencies qualify; 12 positive / 12 zero shortfall | 0 |

Parity: all six regenerated CSV hashes and all nine logical table hashes matched the preparation evidence exactly. The SQLite file bytes differ between SQLite library versions, which is why the two-run check compares logical content rather than file bytes.

### Independent recomputation and probes

- A separate script with no project code parsed the five raw JSON files and the 24 FY2020 PDFs (`pdftotext -raw`) and recomputed baseline mean, shortfall, counts, inclusion flags, year indicators, and interactions: 144 rows × 11 fields compared with `panel_agency_year.csv`, 0 mismatches.
- All 24 FY2020 PDF achievements equal the FY2021 prior-year column. The HUD page shows the column order "2019 Achievement | 2020 Goal | 2020 Achievement (dollars)", so the parser's assignment is correct; −5.04% and ($-50.6 M) are on the page.
- Database probes with foreign keys enabled: duplicate agency-year, unknown agency, out-of-range year, deleting a referenced agency, invalid overlap status, out-of-range panel flags, invalid provenance JSON, and out-of-range document edition are all rejected. All nine tables and five declared indexes exist.
- Fault injections on mutated snapshot copies (overlap conflict, unknown agency, malformed percentage, negative goal, missing FY2020 PDF, duplicate stable agency via alias, sample conflict, missing FY2025 JSON): every case returned a nonzero exit and left the previous database bytes unchanged.
- A scratch `git init` confirmed the frozen snapshot (57 files, 5.2 MB) is tracked and `data/processed/` outputs are not.

### Defects found and fixed before submission

All were low severity and none affected the data. The fixes were applied after the review and are covered by the two added tests.

1. `etl.main()` always logged "previous valid database is not replaced" even when the failure occurred after the validated database had already been replaced (reproduced by making an export path unwritable). The log and `validation_summary.json` now distinguish the two cases (`database_replaced`).
2. A rejected batch caused by a missing FY2020 PDF reported `rejected_record_count: 0`; the fallback row is now counted.
3. The `own_year_pdf` flag text claimed the FY2021 cross-check ran even when the prior-year value was unavailable; the wording is now conditional.
4. A raw-text prime/subcontracting guard in `parse_2020_pdf_text()` could never fire (every page header contains "Prime Contracting"); it was removed and the docstring now states that the layout pass is the authoritative boundary check.
5. The `sdvosb-federal-analytics` console script still printed the A2 "Hello" placeholder; it now runs `etl.main`.

### Final build evidence

The files in `docs/validation/` were regenerated from the final tree in the Section B environment after the fixes: `pytest.log`, `pipeline_execution.log`, `rerun_execution.log`, `rerun_verification.json`, `validation_summary.json`, and `feasibility.log`. The logical table hashes are unchanged from Section A because the fixes do not alter any extracted value or flag text in the frozen build.

### Not verified by either record

Live collection against sba.gov, native Windows/macOS execution, the optional R check, and the measurement comparability questions in `DATA_QUALITY.md`.
