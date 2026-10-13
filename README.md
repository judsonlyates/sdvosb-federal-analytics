# SDVOSB Federal Market Analytics

BUS 751, Python for Business Analytics · Fall 2026 · University of South Alabama
Author: Judson L. Yates

## Project and Assignment 4

This semester-long portfolio examines whether agencies further below the 5% SDVOSB contracting benchmark before the FY2024 goal increase subsequently showed larger increases in SBA-reported achievement. It is an associational pilot, not a causal estimate. The approved proposal remains in [`docs/proposal.md`](docs/proposal.md).

Assignment 4 implements the database and reproducible extract–transform–load pipeline. The frozen public SBA sources yield 144 agency-years (24 agencies, FY2020–FY2025), including 143 complete observations and one explicit USAID FY2025 N/A row. The A3 sample is unchanged: all 48 populated numerical cells reconcile. EDA, regression, and the dashboard remain later assignments.

## Setup

Use Python 3.11 managed by [UV](https://docs.astral.sh/uv/) and the `pdftotext` command supplied by Poppler.

1. Install Git and UV using their official instructions, then clone the existing portfolio:
   ```sh
   git clone https://github.com/judsonlyates/sdvosb-federal-analytics.git
   cd sdvosb-federal-analytics
   ```
2. Install Poppler if `pdftotext -v` is unavailable:
   - macOS with Homebrew: `brew install poppler`
   - Debian/Ubuntu: `sudo apt-get install poppler-utils`
   - Windows: the documented cross-platform route is Ubuntu under WSL with the Debian/Ubuntu command above. Run the remaining commands inside that environment. A native Windows installation must separately provide `pdftotext` on PATH; native Windows was not tested for this submission preparation.
3. Install the locked project environment:
   ```sh
   uv sync --locked
   ```
4. Confirm the external parser is on PATH:
   ```sh
   pdftotext -v
   ```

UV installs the pinned Python version if necessary. `uv.lock` and the existing dependency versions are preserved. Setup downloads require internet access; the frozen pipeline and tests need no internet after setup.

## One command: complete offline pipeline

Run from the repository root:

```sh
uv run --locked python -m sdvosb_federal_analytics.etl --offline --raw-dir data/raw/20261011T183300Z
```

This verifies all 55 source hashes, re-extracts the JSON and original PDFs, validates and reconciles the data, derives the approved exposure/inclusion fields, and builds `data/processed/scorecards.sqlite`. It also writes the full ten-column CSV, derived panel CSV, row provenance, flags, overlap comparisons, sample reconciliation, `validation_summary.json`, and `pipeline.log`.

A malformed or conflicting source produces a nonzero exit and an explicit diagnostic. Invalid batches cannot replace the previous valid database. Missing values declared by the source are retained as NULL, never zero. Source-reported negative achievements/dollars are retained and flagged.

## Automated checks and re-runnability

```sh
uv run --locked pytest -q
uv run --locked python -m sdvosb_federal_analytics.verify_rerun
uv run --locked python scripts/feasibility_check.py data/processed/sba_scorecard_sdvosb.csv
```

The re-runnability command executes the complete pipeline twice against the same output path and compares every table's row count and sorted logical contents, exported CSV hashes, duplicate fact keys, and database integrity checks. Evidence is written to `data/processed/rerun_verification.json`. The committed preparation evidence is in [`docs/validation/`](docs/validation/).

## Evidence map

| Assignment 4 evidence | Location |
|---|---|
| Schema, keys, constraints, indexes | `src/sdvosb_federal_analytics/schema.sql` |
| ERD, normalization rationale, relationships | [`docs/ERD.md`](docs/ERD.md) |
| Every table/field/type/key/source/business rule | [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) |
| Importable extraction/transformation/loading | `src/sdvosb_federal_analytics/etl.py` |
| Proposal-defined derived panel | `src/sdvosb_federal_analytics/panel.py` |
| Validation, logging, failure and refresh behavior | [`docs/PIPELINE.md`](docs/PIPELINE.md) |
| Quality results, explicit missingness/rejections | `docs/validation/validation_summary.json` |
| Two-run row counts and logical hashes | `docs/validation/rerun_verification.json` |
| Tests and execution environment | [`docs/VALIDATION.md`](docs/VALIDATION.md) |
| Source comparability limitations | [`docs/DATA_QUALITY.md`](docs/DATA_QUALITY.md) |
| Student walkthrough and review checklist | [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md) |
| AI use and verification ownership | [`docs/AI_USE.md`](docs/AI_USE.md) |

## Sources and safe review

The repository tracks one small, public SBA snapshot, approximately 5.3 MB across 55 government source documents plus its manifest. These are HTML/JavaScript text, annual JSON, and FY2020 scorecard PDFs. Downloaded JavaScript is inspected only as source text and is never executed. `.gitattributes` preserves the frozen bytes across line-ending conversions. No confidential records, credentials, transaction-level extracts, or personal data are required.

All other raw snapshots and generated databases/exports remain ignored. The original 144-row A3 sample remains tracked at `data/sample/sba_scorecard_sdvosb.csv`; its 18 populated observations are the reconciliation baseline. The frozen sources make the complete offline review reproducible from a fresh clone.

To collect a new official-source snapshot, choose a new, empty folder:

```sh
uv run --locked python -m sdvosb_federal_analytics.etl --raw-dir data/raw/new-snapshot --output-dir data/processed/refreshed
```

A refresh uses only public SBA sources and needs no API key. New data are compared with the original sample; source changes that conflict with it require review. Never overwrite the frozen snapshot. `--json-only` is a reduced diagnostic mode that leaves FY2020 goals/dollars blank; it is not the complete A4 result.

## Interpretation boundaries

Read `docs/DATA_QUALITY.md` before analysis. The FY2021–FY2023 baseline straddles SBA's FY2022 deobligation-methodology change. DOE's later abbreviated footnotes do not establish a change in M&O treatment. VA FY2023 remains the verified SBA value of 27.16%, with a different 16.7% measure flagged rather than substituted. FY2025 certification changes are another comparability caveat. Passing ETL checks does not establish the hypothesis or causality.

## Later course components

A5: exploratory analysis. A6: modeling and robustness. A7: dashboard and deployment. These components are outside the A4 implementation.
