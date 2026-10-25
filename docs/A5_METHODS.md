# Assignment 5: exploratory methods, data, and reproducibility

The original approved Assignment 3 proposal remains unchanged. The A5 exploratory tests do not claim a causal policy effect. Execution ownership and personal-review status are recorded separately in `AI_USE.md` and `REVIEW_CHECKLIST.md`.

## Data lineage and analytic unit

The unit for descriptive trajectories is an agency–fiscal year; the unit for independent cross-sectional tests is an **agency**. The authoritative A4 SQLite database `data/processed/scorecards.sqlite` preserves 24 agency identities × FY2020–FY2025, 144 rows and 143 nonmissing achievement observations (USAID FY2025 is source-declared N/A). This analysis reads A4 `panel_agency_year` joined **on agency and fiscal year** to `scorecard_observations` for reported goals and SDVOSB dollars. The frozen source snapshot is from October 11, 2026.

The separately built `data/processed/analysis.sqlite` adds `historical_achievement` for FY2017–FY2025 (216 rows, 215 numeric) and `vendor_counts` for FY2020–FY2025 (144 rows, 143 numeric). It excludes five GW records, checks the frozen source SHA-256 hashes, compares all overlapping historical figures after numeric normalization (384 checks), and verifies 192 vendor prior-year overlaps. It also cross-checks every FY2020–FY2025 achievement value with A4. The two supplemental tables are built twice with identical logical hashes; **the nine graded A4 tables are not changed**. Supplement reads use SQLite read-only connections, and the command rejects an output path that aliases the A4 input database. Note that FY2017 appears in one annual source edition only; it has no independent overlap comparison.

A firm's appearance in two agencies can contribute to both agencies' vendor counts. The vendor series is **not** a government-wide count of distinct firms. The vendor-count ratio divides SDVOSB prime contractor count by all small-business prime contractor count; it is **not** a contracting-dollar share. The denominator for SBA-reported goaling achievement is different again.

## Univariate analysis (rubric: 30-point statistical analysis)

`eda.describe_variables` reports data type, nonmissing/missing rows, range, quartiles, median and mean for achievement, scorecard goal, SDVOSB credited dollars, FY2021–FY2023 baseline, shortfall, SDVOSB contractor counts, count ratio and the extended history. The shortfall distribution chart shows all 24 agencies and explicitly displays the mass at zero (12 agencies). FY2020 and FY2021 HUD negative achievement values are **retained**, not screened as errors.

## Bivariate analysis and documented A5 exploratory test

Define agency-level shortfall `S=max(0,5−mean(Y2021,Y2022,Y2023))` and change `Δ2024 = Y2024 − Y2023` (percentage points), with `Δ2025` separately. The science prediction is more positive change at the 12 agencies with positive shortfall compared with the 12 agencies at zero. The test was documented after an initial feasibility run and is not a blinded pre-analysis commitment. The **primary A5 inferential check** is a two-sided Welch t-test of equal *means*, with Welch–Satterthwaite degrees of freedom and a 95% confidence interval for positive-shortfall minus zero-shortfall difference. Hedges' g describes standardized magnitude. The Mann–Whitney U statistic and rank-biserial effect are a nonparametric sensitivity, not an alternative test selected post-hoc. Shapiro–Wilk per group, Q–Q plots and influence screens assess assumptions; their p-values do not switch the primary test. A Spearman correlation relates continuous shortfall to change. FY2025 tests are secondary and use 23 agencies because USAID FY2025 is absent.

**Critical interpretive limit:** FY2023 appears *both* inside the FY2021–2023 shortfall definition and with a negative sign in the FY2023→FY2024 change. This mathematically couples the quantities, independently of policy. Regression to the mean and the FY2022 methodology change are additional reasons not to equate A5 comparisons with a policy response. Normality diagnostics show a distribution departure in the positive-shortfall FY2024 group, warranting particular caution with the small two-group sample.

**Formal hypotheses and reference level:** H0: the two groups have equal mean change (`mu_positive - mu_zero = 0`). H1: their mean changes differ (`mu_positive - mu_zero != 0`). The scientific expectation is a positive difference, but the executed inferential test is two-sided at alpha = 0.05; no one-sided p-value is substituted after seeing results. The Mann–Whitney sensitivity tests a distribution/rank contrast, not the same null about means without additional distributional assumptions.

**Independence and generalization:** Each agency contributes one change per comparison; agency-years are not treated as independent replicates. Agencies still face common federal shocks and connected procurement decisions, so cross-agency independence is a working assumption, not established by a Shapiro test. These 24 scored agencies are not a random sample of firms or all government buyers. Intervals and p-values are model-based exploratory summaries, not proof of a causal policy effect or broad population generalizability. No multiplicity-adjusted confirmatory family is claimed for the secondary diagnostics.

## Multivariate analysis and A6 comparison specification

The cross-sectional simple OLS is `Δ2024 = a + bS + error` using 24 agencies, HC3 heteroskedasticity-robust standard errors and a t reference distribution. The descriptive multivariate extension is `Δ2024 = a + bS + c log(FY2023 SDVOSB credited dollars in USD millions) + error`, again with HC3. These are **exploratory models**, not controls that remove selection or mean reversion; the log variable is positive for all 24 FY2023 agencies. Model rank is checked. Cook's distance and leverage are reported and no observation is automatically deleted. The Spearman correlation matrix uses pairwise complete cases; the baseline average and `S` are mechanistically related.

The A5 simple OLS is retained for A6's rubric-required comparison. It is **not** the same estimand as the full A6 TWFE interaction: A5's dependent change references FY2023 alone while A6's exposure interactions reference FY2020–FY2023.

## Visualization and business-facing interpretation (rubric: 25 + 20 points)

`eda.figures` saves ten 180-DPI PNGs: all-agency shortfall distribution, 24 small-multiple FY2017–FY2025 trajectories, shortfall-group achievement means, separately labeled FY2024 and FY2025 scatterplots with a dedicated zero-shortfall label lane and short leaders (data points are not jittered), median agency contractor counts, median count ratio, Spearman heatmap, Welch Q–Q plots, and multivariate Cook's-distance diagnostics. Figures use readable titles, measured units, distinct markers/line patterns, and appropriately labeled reference lines. **A statutory goal reference line on achievement charts is not a claim that each agency had an identical negotiated target.** Count plots intentionally have no 5% line.

[`A5_EXECUTIVE_SUMMARY.md`](A5_EXECUTIVE_SUMMARY.md) states the business implications and interpretation limits. Business implications address what SDVOSB firms and agency staff can **explore** in the scorecards; the current evidence cannot justify treating the statutory goal increase as the cause of any difference. Final author review is tracked in the review checklist rather than asserted by a computational check.

## Commands from a clean checkout

Prerequisites: Python 3.11, UV, Poppler `pdftotext` on PATH, and network access **once** to install the existing locked dependencies. Preserve `uv.lock` for reproduction; do not refresh it as part of a routine rerun. The frozen source pipeline itself runs offline once dependencies are installed.

```sh
uv sync --locked
uv run --locked pytest -q
uv run --locked python -m sdvosb_federal_analytics.etl --offline --raw-dir data/raw/20261011T183300Z
uv run --locked python -m sdvosb_federal_analytics.verify_rerun
uv run --locked python -m sdvosb_federal_analytics.supplement
uv run --locked python -m sdvosb_federal_analytics.eda
uv run --locked jupyter lab notebooks/assignment05_eda.ipynb
```

`uv.lock` was refreshed on the integrated repository with `uv add scipy statsmodels matplotlib seaborn`, `uv lock`, and `uv sync --locked` under Python 3.11; the A4 dependency versions are unchanged. The clean-build run on that environment is recorded in `docs/LOCAL_EXECUTION_EVIDENCE.md`, Section A.

Tests build their own A4 inputs in pytest temporary directories and can run before the project pipeline. They do not require an existing `data/processed/scorecards.sqlite` and do not skip the A5 analyses for absent project outputs.

Results: `results/a5_results.json`, `results/a5_agency_changes.csv`, `results/a5_descriptive_summary.csv`, `results/a5_regression_estimates.csv`, `results/a5_influence.csv`, `results/a5_correlations.csv`, and ten `figures/a5_*.png`. `notebooks/assignment05_eda.ipynb` imports the actual reusable code; analyses are not duplicated within cells.
