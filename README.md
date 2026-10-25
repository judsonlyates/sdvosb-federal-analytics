# SDVOSB Federal Market Analytics

BUS 751, Python for Business Analytics · Fall 2026 · University of South Alabama
Author: Judson L. Yates

Assignment 5 adds a reproducible exploratory analysis to the preserved Assignment 4 database. Start with the setup below, the [A5 evidence map](docs/A5_RUBRIC_EVIDENCE.md), and the [executive summary](docs/A5_EXECUTIVE_SUMMARY.md).

## Project and Assignment 4

This semester-long portfolio examines whether agencies further below the 5% SDVOSB contracting benchmark before the FY2024 goal increase subsequently showed larger increases in SBA-reported achievement. It is an associational pilot, not a causal estimate. The approved proposal remains in [`docs/proposal.md`](docs/proposal.md).

Assignment 5 adds the exploratory data analysis module on top of that database; see [Assignment 5](#assignment-5-exploratory-data-analysis) below. Assignment 4 implements the database and reproducible extract–transform–load pipeline. The frozen public SBA sources yield 144 agency-years (24 agencies, FY2020–FY2025), including 143 complete observations and one explicit USAID FY2025 N/A row. The A3 sample is unchanged: all 48 populated numerical cells reconcile. A5 implements EDA; the A6 modeling extension and A7 dashboard remain later assignments.

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

UV installs the pinned Python version if necessary. The locked environment includes the Assignment 5 analysis libraries (SciPy, Statsmodels, Matplotlib, Seaborn) alongside the original A4 dependencies; the A4 dependency versions are unchanged. Setup downloads require internet access; the frozen pipeline and tests need no internet after setup.

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

The test suite also works immediately after `uv sync --locked`, before any project build. Its A5 fixtures build the required A4 input and supplementary tables in pytest's temporary directories; no tests are skipped for a missing prebuilt database, and tests do not create or overwrite `data/processed/scorecards.sqlite`.

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

## Assignment 5: exploratory data analysis

Assignment 5 reads the graded A4 database and adds descriptive statistics, one documented exploratory hypothesis test, and a static figure suite. It does not modify any A4 table. The analysis commitments are recorded in [`docs/ANALYSIS_PLAN.md`](docs/ANALYSIS_PLAN.md), which was refined after the A4 feedback and an initial feasibility run. It is not a blind preregistration.

### One command: A4 database plus A5 analysis

```sh
uv run --locked python scripts/run_portfolio.py --through a5
```

This runs, in order: the A4 offline ETL, the A4 two-run verifier, the A5 supplementary extraction (`sdvosb_federal_analytics.supplement`, which writes `data/processed/analysis.sqlite` from the same frozen JSON files), and the A5 analysis module (`sdvosb_federal_analytics.eda`). Each stage can also be run on its own with `uv run --locked python -m <module>`.

Outputs:

| What | Where |
|---|---|
| Result tables (descriptives, agency changes, test statistics, correlations, regression estimates, influence) | `results/a5_*.csv`, `results/a5_results.json` |
| Ten figures (shortfall distribution, trajectories, group trends, change scatterplots, contractor counts, correlation heatmap, assumption and influence diagnostics) | `figures/a5_*.png` |
| Supplementary database: FY2017–FY2025 historical achievement and FY2020–FY2025 SDVOSB prime-contractor counts | `data/processed/analysis.sqlite` (ignored; rebuilt by the command above) |

### Notebook and documentation

- [`notebooks/assignment05_eda.ipynb`](notebooks/assignment05_eda.ipynb) demonstrates the workflow by importing `sdvosb_federal_analytics.eda`; it defines no analysis functions of its own. Run the command above first so both databases exist, then `uv run --locked jupyter lab`.
- [`docs/A5_METHODS.md`](docs/A5_METHODS.md): methodology, test selection, assumption checks, and figure conventions.
- [`docs/A5_EXECUTIVE_SUMMARY.md`](docs/A5_EXECUTIVE_SUMMARY.md): findings and implications for a non-technical reader.
- [`docs/A5_RUBRIC_EVIDENCE.md`](docs/A5_RUBRIC_EVIDENCE.md): the four rubric categories mapped to exact deliverables and verification.
- [`docs/ANALYSIS_PLAN.md`](docs/ANALYSIS_PLAN.md): the dated analysis-plan addendum covering Assignments 5 and 6.
- [`docs/REVIEW_CHECKLIST.md`](docs/REVIEW_CHECKLIST.md) and [`docs/LOCAL_EXECUTION_EVIDENCE.md`](docs/LOCAL_EXECUTION_EVIDENCE.md): student review steps and recorded execution evidence.

Tests for the A5 module live in `tests/test_eda.py` and run with the same `uv run --locked pytest -q` command as the A4 suite.

## Later course components

A6: modeling and robustness. A7: dashboard and deployment. These components are outside the A4 and A5 implementations.
