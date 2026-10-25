# Assignment 5 execution evidence

This file records what was actually run, where, and with what result, so the review checklist and the AI-use disclosure can point to it. It is updated whenever the status changes.

## Section A. Clean-build verification on the integrated repository (October 14, 2026)

Performed by Claude in a Linux container on a checkout of the graded Assignment 4 commit `ccdc34dc` with the Assignment 5 files added. No commit or push was made; this section describes the working tree presented for the student's review.

**Preservation of the graded A4 implementation.** No tracked A4 file was modified except `pyproject.toml` (four analysis libraries added), `uv.lock` (refreshed accordingly), and `README.md` (an Assignment 5 section added). `etl.py`, `schema.sql`, `panel.py`, `verify_rerun.py`, the A4 tests, the frozen source snapshot, and the A4 documentation are byte-identical to the graded commit.

**Environment.** Python 3.11.17 under UV with the refreshed lockfile; pandas 3.0.5, NumPy 2.4.6, SciPy 1.17.1, statsmodels 0.15.0, Matplotlib 3.11.2, Seaborn 0.13.2; Poppler `pdftotext` 24.02.0.

**Procedure and results.** All generated outputs (`data/processed/`, `figures/`, `results/`) were deleted first, so every result below was rebuilt from the frozen sources.

| Step | Command | Result |
|---|---|---|
| Dependencies | `uv add scipy statsmodels matplotlib seaborn`, `uv lock`, `uv sync --locked` | Resolved 124 packages; A4 dependency versions unchanged |
| Full A5 build | `uv run --locked python scripts/run_portfolio.py --through a5` | Completed: A4 ETL (144 rows, 143 complete, database replaced), A4 two-run verifier (`status: pass`, identical logical records and counts), supplement (216 historical rows, 144 vendor-count rows, 5 GW rows excluded, 384 historical and 192 vendor-count overlap checks passed), EDA (10 figures, 6 result files) |
| A4 database untouched by A5 stages | SHA-256 of `data/processed/scorecards.sqlite` before and after re-running `supplement` and `eda` | Identical (`fa3ea19cb9a6b048…`) |
| A4 verifier after the A5 build | `uv run --locked python -m sdvosb_federal_analytics.verify_rerun` | `status: pass` |
| A4 feasibility script | `uv run --locked python scripts/feasibility_check.py data/processed/sba_scorecard_sdvosb.csv` | 24 agencies; 12 positive / 12 zero shortfall; 2 negative achievements retained and flagged |
| Test suite | `uv run --locked pytest -q` | 50 passed, 5 subtests passed (40 A4 + 10 A5) |
| Notebook | `jupyter nbconvert --to notebook --execute notebooks/assignment05_eda.ipynb` | Executed top to bottom with no cell errors |
| Separate database | Table listing of both SQLite files | A4: the nine graded tables only. A5: `historical_achievement`, `vendor_counts`; no `GW` rows |

**Key A5 statistics reproduced in this run.** FY2023→FY2024 Welch p = 0.644 (24 agencies); FY2023→FY2025 Welch p = 0.520 (23 agencies, USAID FY2025 missing). These match the October 14 exploratory run recorded in `docs/ANALYSIS_PLAN.md`, Section 8.

## Section B. Student verification (not yet recorded)

The following personal actions are not recorded in this artifact. Add the actual
date, commands, and outcomes only after completing them; assistant-run results
must not be relabeled as student execution. A personal local run is a useful
verification step, not a new physical-computer requirement added to the rubric.

- [ ] Ran the documented A4/A5 build on my own computer and checked row counts and results.
- [ ] Ran the test suite and A4 two-run verifier personally.
- [ ] Read the code, notebook, and every figure.
- [ ] Traced NASA FY2023 and reviewed DOE FY2023's M&O caveat from original source through SQLite to shortfall.
- [ ] Adopted or revised the executive-summary interpretation in my own judgment.
- [ ] Reviewed and adopted the truthful A5 disclosure; updated actual personal verification status.

## Section C. Corrected review package (October 24, 2026)

Performed by the OpenAI assistant in a separate cloud working copy of the
original A5 ZIP. This is not a student-computer run. No commit or push was made.

**Environment:** Python 3.11.17; pandas 3.0.5; NumPy 2.4.6; SciPy 1.17.1;
statsmodels 0.15.0; Matplotlib 3.11.2; Seaborn 0.13.2; pytest 9.1.1.
`uv sync --locked` succeeded without changing `pyproject.toml` or `uv.lock`.

| Check | October 24 result |
|---|---|
| Full offline `scripts/run_portfolio.py --through a5` | Passed: 144 A4 agency-years, 143 numeric achievements; 216 history and 144 vendor rows; ten figures and six result files |
| Final `pytest -q` | 58 passed, 5 subtests passed, including eight added regression cases |
| Frozen sources | All 55 hash/byte-size checks passed; source bytes unchanged |
| A4 logical data | All nine tables match archived A4 row counts and logical hashes |
| A5 preservation | A4 database physical hash unchanged before/after supplement and EDA |
| Numerical results | All six result files byte-identical to original ZIP |
| Plot review | All ten PNGs viewed; 24/23 scatter labels checked for geometry and unchanged point coordinates |
| Fresh-kernel `nbconvert --execute` | Not verified: local kernel sockets blocked; elevated launch also failed before execution |
| In-process notebook execution | All five actual code cells passed in order under IPython/Python 3.11.17; rich outputs saved and method labeled in notebook metadata |

The normal notebook command still needs an independent fresh-kernel check.
The included fallback runner does not claim to be that check. A4 core source,
schema, original tests, sample, proposal, and dependency lock are unchanged.
Supplement read-only/path guards, chart layout, documentation, and regression
tests are the targeted edits. Evidence is in `validation/a5_revision_2026-10-24/`.

## Section D. Pre-push correction and clean-copy validation

Performed by the OpenAI assistant, at Judson's request, in a separate working
copy of the corrected October 24 review ZIP. No commit, push, or submission
was made. These are assistant-run checks, not a student-computer execution.

**Environment:** locked Python 3.11.17; pandas 3.0.5; NumPy 2.4.6;
SciPy 1.17.1; statsmodels 0.15.0; Matplotlib 3.11.2; Seaborn 0.13.2;
pytest 9.1.1. The dependency specification and lockfile were not changed.

| Check | Actual result |
|---|---|
| Original tests-first defect | Independently reproduced 45 passed, 13 errors, 5 subtests passed before correcting the fixture |
| Corrected suite before build | 60 tests and 5 subtests passed with no project-output A4 database present; no tests skipped |
| Output isolation | The tests left `data/processed/scorecards.sqlite` absent; A4/A5 test fixtures used temporary directories |
| Full offline pipeline | Passed: 144 A4 rows, 143 numerical achievements; 216 historical rows and 144 vendor rows; ten figures and six numerical result files |
| Corrected suite after build | 60 tests and 5 subtests passed |
| Preserved source/data | All 55 frozen sources, nine A4 logical tables, and six A5 numerical result hashes match archived evidence |
| A4 source preservation | A4 pipeline modules, schema, original tests, A3 proposal/sample, dependency specification/lock, and pre-A5 AI disclosure match the input review ZIP |
| Numerical recomputation | Independent database/SciPy calculations reproduce both Welch tests, intervals, group sizes/means, Shapiro, Mann–Whitney, rank effects, and Spearman results; explicit HC3 design matrices reproduce all saved regression coefficients, SEs, p-values and intervals |
| Original-source trace | NASA/DOE FY2021–FY2023 JSON values agree with A4 and the derived baseline/shortfall |
| Plot preservation and inspection | Nine PNGs unchanged; only FY2025 scatter footer changed to explain missing USAID. All ten figures viewed; scatter coordinate/label tests pass |
| Notebook | All five actual code cells pass in-process; outputs and honest execution metadata saved. A4 database hash unchanged by notebook EDA |
| Fresh Jupyter kernel | Not certified here: this runner's kernel launch is permission-blocked. Claude separately reported a successful fresh-kernel run on the preceding corrected package; the report is not claimed as an OpenAI or student run |
| Active links and code documentation | No broken links in the active README/A5 document set; reusable A5 functions and orchestration functions have docstrings |

Exact logs and structured checks are in `validation/a5_pre_push/`:
`pytest_before_build.log`, `pytest_after_build.log`, `full_pipeline.log`,
`preservation.log`, `feasibility.log`, `notebook_cells.log`,
`clean_validation.json`, and `independent_checks.json`.

The A5 source fix is confined to test setup, its regression tests, documentation,
and one chart footer. Formal hypotheses were clarified to match the existing
two-sided test; no data, exposure, estimator, p-value, or confidence interval
was changed. Author review and separate push approval remain recorded in
`REVIEW_CHECKLIST.md`.
