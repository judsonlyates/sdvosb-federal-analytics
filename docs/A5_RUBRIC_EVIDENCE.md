# Assignment 5 rubric evidence map

The maximum points below reproduce the included assignment rubric. They are
not awarded or predicted grades. The assignment specification is retained at
`validation/a5_revision_2026-10-24/reference/Assignment05_Exploratory_Analysis.md`.

| Criterion | Maximum | Evidence and verification |
|---|---:|---|
| Statistical analysis | 30 | `eda.describe_variables`, `agency_changes`, `welch_analysis`, `run_regressions`, and `correlation_matrix`; eight univariate summaries, two separate annual change comparisons, two-sided Welch hypotheses/CI/effect size, Shapiro/Q–Q checks, Mann–Whitney sensitivity, HC3 multivariate OLS and influence diagnostics. See `A5_METHODS.md` and `results/a5_results.json`. |
| Data visualization | 25 | Ten static Matplotlib/Seaborn figures with titles, units, agency labels, distinct baseline-group markers/line styles and colorblind-safe group colors. Scatter geometry is automatically tested; the zero-shortfall cluster is labeled without jittering data. See `figures/a5_01` through `a5_10` and the notebook. |
| Code architecture | 25 | Importable, documented `eda.py` and `supplement.py`; the five-code-cell notebook imports functions rather than defining duplicate analytics. `scripts/run_portfolio.py` orchestrates offline reproduction. A5 tests build independent temporary inputs and run both before and after the main build. |
| Business insights | 20 | `A5_EXECUTIVE_SUMMARY.md` answers the approved A3 question and gives bounded implications for SDVOSB firms, agency offices, and the next research stage. It separates an inconclusive difference from equality and association from policy causation. The author must understand/adopt the interpretation. |
| Total available | 100 | Current execution evidence and personal-review ownership are separate in `LOCAL_EXECUTION_EVIDENCE.md` and `AI_USE.md`. |

## Deliverables to open

1. `A5_EXECUTIVE_SUMMARY.md`: nontechnical question, findings, decisions and limits.
2. `A5_METHODS.md`: data lineage, formal hypotheses, assumption checks and limits.
3. `../notebooks/assignment05_eda.ipynb`: reusable workflow, outputs and conclusion.
4. `../src/sdvosb_federal_analytics/eda.py` and `supplement.py`: implementation.
5. `../results/`: six machine-readable result files.
6. `../figures/`: ten exported charts.
7. `AI_USE.md`: material AI assistance, student decisions and verification ownership.

## Figure index

| File | Purpose |
|---|---|
| `a5_01_shortfall_distribution.png` | All-agency baseline exposure, including the twelve zero values |
| `a5_02_historical_agency_trajectories.png` | Each agency's nine-year history; panel scales vary, so compare patterns rather than line height across panels |
| `a5_03_group_trends.png` | Descriptive group means and the 3%-to-5% reference step |
| `a5_04_shortfall_vs_change_2024.png` | FY2024 change, labeled agencies and unchanged data coordinates |
| `a5_05_shortfall_vs_change_2025.png` | FY2025 change; source-declared missing USAID is explicit |
| `a5_06_vendor_counts.png` | Median agency contractor breadth, not unduplicated firms government-wide |
| `a5_07_vendor_ratio.png` | Contractor-count ratio with the correct denominator |
| `a5_08_spearman_correlations.png` | Multivariate descriptive rank associations |
| `a5_09_qq_welch_assumptions.png` | Group-specific distribution diagnostics |
| `a5_10_multivariable_influence.png` | Cook's-distance screen; no automatic agency deletion |

## Interpretation guardrails

- The 24 agencies are the cross-sectional units, not 144 independent units.
- Twelve agencies have positive shortfall based on the FY2021–FY2023 mean;
  fourteen exceeded or reached 5% in FY2023 itself. These are different facts.
- FY2024 and FY2025 Welch intervals include zero. This is inconclusive, not
  evidence of equal groups, policy failure, or a causal policy effect.
- Shared FY2023 terms, differing pre-trends, common shocks and source-definition
  changes limit the design; the sensitivity tests do not erase those limits.
- A5 is the exploratory stage. A6 model estimation and A7 interactive deployment
  are not missing A5 requirements and have not been added to inflate this work.
