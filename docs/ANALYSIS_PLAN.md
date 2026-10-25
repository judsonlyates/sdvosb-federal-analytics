# Analysis Plan Addendum (Assignments 5–6)

**Project:** Agency-level SDVOSB goaling achievement around the FY2024 goal increase
**Author:** Judson L. Yates
**Prepared:** October 14, 2026. **Scope authorization:** October 14, 2026; targeted A5 corrections authorized October 24, 2026. Subsequent pre-push corrections do not change A3's exposure, hypothesis, or primary model.
**Status of this document:** An addendum to the graded Assignment 3 proposal (`docs/proposal.md`, graded September 29, 2026), prepared after Lambert's Assignment 4 feedback. It is **not a prospective or blind preregistration**. The original A3 hypothesis and primary model predate the October 14 exploratory feasibility run. Preliminary group comparisons, model and placebo estimates were computed and displayed in the conversation **before this plan was approved**; my receiving the messages is not treated as proof that I personally studied each result. The extended sensitivity list and numerical fallback conventions are subsequent analysis-plan choices, not independently precommitted findings. Git records the actual commit date, not a backdated research commitment.

---

## 1. What this addendum changes and what it does not

**Unchanged from the approved proposal:**

- The research question, unit of analysis (agency × fiscal year), and primary hypothesis H1: "Greater distance below the 5% benchmark, measured using average FY2021–FY2023 achievement, is associated with larger increases in SBA-reported SDVOSB achievement in FY2024 and FY2025, evaluated separately."
- The exposure definition, `S_a = max(0, 5 − mean(FY2021, FY2022, FY2023))` in percentage points.
- The primary model: unweighted two-way fixed-effects OLS with separate FY2024 and FY2025 interactions.
- The year-by-year decision rule and the associational (not causal) scope.
- The inclusion rule and the data (the frozen October 11, 2026 SBA snapshot; 143 of 144 agency-year observations complete, USAID FY2025 missing at source).

**Added by this addendum:**

1. A precise statement of the outcome construct (Section 2).
2. The Assignment 5 descriptive and exploratory analyses, including one documented exploratory hypothesis test (Section 3).
3. Two supplementary descriptive series drawn from the same frozen source files (Section 4).
4. The extended Assignment 6 diagnostic and sensitivity set, refined after an initial feasibility run (Section 5).
5. The rule for when the project reports descriptive trajectories instead of a policy-response association (Section 6).
6. How the Assignment 5 results serve as the comparison specification Assignment 6 requires (Section 7).

Nothing in this addendum revises the graded Assignment 4 database. Supplementary data are built into a separate file (Section 4).

---

## 2. Outcome construct

The outcome is **SBA-reported SDVOSB prime-contracting goaling achievement**, in percentage points, as displayed on each agency's annual SBA Small Business Procurement Scorecard and stored in `scorecard_observations.sdvosb_prime_achievement_pct`.

This is SBA's goaling-credit measure. It is not the number of SDVOSB firms, their bids, contract awards, or an unadjusted dollar share. It includes double credit for certain local-area and territory awards, DOE's M&O first-tier subcontracts in at least FY2021–FY2023, and whatever denominator SBA applied in each year (the VA FY2023 figure of 27.16% differs from a CRS figure of 16.7% drawn from SAM data; the scorecard value is retained and the discrepancy is documented in `DATA_QUALITY.md`).

The working title is therefore revised going forward to **"Agency-Level SDVOSB Goaling Achievement Around the FY2024 Goal Increase."** The graded proposal is not edited; the revision applies to the README, Assignment 5–7 documents, and the dashboard.

A secondary, descriptive measure closer to literal participation is added in Section 4 (the count of SDVOSB prime contractors). It is not part of H1 and no confirmatory test is attached to it.

---

## 3. Assignment 5: descriptive and exploratory analyses

All A5 analyses read `panel_agency_year` from the A4 database (`data/processed/scorecards.sqlite`) and the supplementary file in Section 4. Static Matplotlib/Seaborn figures use consistent styles. Achievement comparison charts carry a clearly labeled government-wide reference benchmark where legible (3% through FY2023; 5% from FY2024), not a claim about negotiated agency-specific goals; change charts carry a zero line; count charts carry neither.

### 3.1 Univariate

For achievement, goal, dollars, baseline average, shortfall, and the supplementary series: type, range, missingness, and distribution. Agency identifiers, inclusion flags, and interaction terms are described in the data dictionary but not plotted. The **distribution of `S_a` across all 24 agencies** is the first figure, as requested in the A4 feedback.

### 3.2 Bivariate

- Agency trajectories FY2020–FY2025 (and FY2017–FY2025 using the supplementary series), colored by whether `S_a > 0`.
- FY2023→FY2024 change and FY2023→FY2025 change against `S_a`, as scatterplots with agency labels.
- Both post-policy years are always shown separately. They are never pooled.

### 3.3 Multivariate

- Correlation matrix (Spearman) among baseline average, shortfall, FY2024 change, FY2025 change, log of FY2023 SDVOSB dollars, and SDVOSB contractor count.
- One descriptive OLS: FY2023→FY2024 change on `S_a` and log FY2023 dollars, n = 24, with HC3 standard errors and an influence check (Cook's distance). Reported as descriptive; no hypothesis is attached to the dollars term.

### 3.4 The Assignment 5 exploratory hypothesis test (documented after the feasibility run)

- **Question:** Did agencies with positive baseline shortfall change more from FY2023 to FY2024 than agencies with zero shortfall?
- **H0:** The mean FY2023→FY2024 change in achievement is equal in the two groups. **H1 for the executed two-sided test:** The mean changes differ. The separate scientific directional prediction is a larger change in the positive-shortfall group; it does not convert the reported p-value to a one-sided test.
- **Primary test:** Welch's two-sample t-test (unequal variances), two-sided 95% confidence interval on the difference in means, Hedges' g as the effect size. Groups: 12 positive-shortfall and 12 zero-shortfall agencies.
- **Assumption checks reported:** Shapiro-Wilk and Q-Q plots per group, and an influence check. The normality check does **not** decide which test is reported; Welch remains primary.
- **Sensitivity:** Mann-Whitney U with the rank-biserial effect size, reported alongside. The same comparison for FY2023→FY2025 (n = 23, USAID missing) is reported as a secondary result.
- **Companion statistic:** Spearman correlation between `S_a` and the FY2023→FY2024 change across all 24 agencies.
- **Interpretation rule:** An interval excluding zero in the predicted direction is exploratory support; an interval including zero is inconclusive; an interval excluding zero in the opposite direction is exploratory evidence against. None of these is a policy-response finding.
- **Known limitation, stated in the write-up:** FY2023 appears in both the exposure (as one third of the baseline mean) and the outcome (as the subtrahend). An unusually low FY2023 value raises `S_a` and the subsequent change together, with no policy response required. This mechanical coupling, together with regression to the mean, is the reason the A5 test is exploratory and the reason Sections 5.2–5.3 exist.

---

## 4. Supplementary descriptive data

Two series are extracted from the same frozen FY2021–FY2025 JSON files already in `data/raw/20261011T183300Z/`. No new source documents are collected.

| Series | Source fields | Coverage | Notes |
|---|---|---|---|
| Historical SDVOSB achievement | `prime_sdvosb_pfy4_achievement` … `prime_sdvosb_pfy_achievement`, `prime_sdvosb_cfy_achievement` | FY2017–FY2025 | FY2017 appears in one edition only (FY2021 file, `pfy4`); FY2018 in two; FY2019 in three. Overlaps are checked for restatements; the most recent edition is used where editions agree, and any disagreement is reported, not resolved silently. |
| SDVOSB prime contractor count | `category_sdvosb_cfy_vendor_count`, `category_sdvosb_pfy_vendor_count`; `category_sb_cfy_vendor_count` for the ratio | FY2020–FY2025 | Count of SDVOSB prime contractors per agency-year, and its ratio to all small-business prime contractors. Descriptive only. |

Rules:

- The `GW` (government-wide) row present in each JSON file is excluded; the 24 scored agencies are matched to `agencies.agency_id` through the existing crosswalk.
- Missing values are stored as NULL, never zero. USAID FY2025 stays missing.
- The series are written to a separate `data/processed/analysis.sqlite` by one documented command that runs after the A4 build. The nine graded A4 tables and their two-run verification are not modified. The A5 module joins the two databases on `agency_id` and `observation_fy`.
- The extraction module has its own tests and its own two-run check.

---

## 5. Assignment 6: estimation, diagnostics, and sensitivity (documented after technical feasibility run)

### 5.1 Primary specification (unchanged)

`Y_at = α_a + γ_t + β₂₀₂₄ (S_a × 1[t = 2024]) + β₂₀₂₅ (S_a × 1[t = 2025]) + ε_at`

Panel FY2020–FY2025, 143 observations, 24 agencies, unweighted OLS, agency and fiscal-year fixed effects. **Estimand:** the differential change in SBA-reported SDVOSB goaling achievement, in percentage points per percentage point of pre-policy shortfall, in each post-policy year relative to FY2020–FY2023. It is an association, not a causal effect of the goal increase.

**Uncertainty:** standard errors clustered by agency with the finite-sample correction and a t reference distribution with G − 1 = 23 degrees of freedom. With 24 clusters, inference is provisional; a wild-cluster bootstrap is reported in addition if implementable in the course window, and its absence is stated otherwise.

### 5.2 Diagnostics (run before interpreting 5.1)

| Diagnostic | What it checks | What would reduce confidence |
|---|---|---|
| Pre-period event-study: add `S_a × 1[t = 2020]` with FY2021–FY2023 omitted (the proposal's check 1) | A limited pre-period difference | A FY2020 coefficient of the same sign and comparable magnitude to the post coefficients |
| Historical trajectories FY2017–FY2023 by shortfall group (Section 4 data) | Whether low-baseline agencies were already rising before FY2024 | Visibly steeper pre-period slopes for the positive-shortfall group |
| **Placebo:** exposure redefined as `max(0, 5 − mean(FY2018, FY2019, FY2020))`, "post" set to FY2021, estimated on FY2017–FY2021 | Regression to the mean under a false policy date | A placebo coefficient as large as the FY2024 or FY2025 estimate |
| Scatter of FY2020→FY2023 change against FY2020 level | Mean reversion in the baseline window itself | A strong negative relationship |

### 5.3 Sensitivity set (report all; documented after preliminary feasibility output)

1. Exposure from FY2023 only (proposal check 2).
2. Exposure from FY2021–FY2022 only (removes FY2023 from the exposure; addresses the coupling in 3.4).
3. Exposure from FY2022–FY2023 only (post-dates the FY2022 deobligation-method change).
4. Drop DOE (M&O subcontract treatment).
5. Drop VA (denominator discrepancy; largest achievement values).
6. Drop HUD (FY2020–FY2021 negatives; straddles the FY2022 break).
7. Drop SBA.
8. Drop DOE, VA, HUD, and SBA together.
9. Leave-one-agency-out for all 24 agencies, reported as a table of β₂₀₂₄ and β₂₀₂₅ with intervals.
10. Secondary outcome: the same primary specification with `log1p(SDVOSB prime contractor count)` as the dependent variable (zero permitted, missing left missing), reported as descriptive and not directly comparable in units to achievement.

### 5.4 Comparison specification (required by the A6 rubric)

The A5 simple OLS of FY2023→FY2024 change on `S_a` (Section 3.3 without the dollars term) and the A5 Welch comparison are the simpler specifications against which the fixed-effects estimates are compared. The comparison reports whether the sign, magnitude, and interval of β₂₀₂₄ agree with the cross-sectional slope, and explains any difference.

### 5.5 Reporting

A single results table (`results/a6_estimates.csv`) with the primary estimates, every diagnostic, every sensitivity, and the comparison specification; the event-study and leave-one-out figures; and a written interpretation that states the estimand, the substantive magnitude in percentage points, and the inferential boundary.

---

## 6. Fallback rule: when to report trajectories, not an association

The project will report descriptive trajectories as its main finding, while still presenting the pre-approved fixed-effects estimates with their uncertainty, if **any** of the following is met. These deliberately conservative numeric thresholds are **interpretive screening conventions**, not standard statistical validity tests; they were finalized after a preliminary feasibility run.

- The placebo coefficient (5.2, row 3) is of the same sign as, and at least half the magnitude of, the corresponding post-policy estimate.
- The FY2020 pre-period coefficient (5.2, row 1) is of the same sign as the post-policy estimates and its interval overlaps theirs.
- The sign of β₂₀₂₄ or β₂₀₂₅ reverses in any of sensitivity checks 1–8, or in more than two of the 24 leave-one-out fits.
- The FY2024 and FY2025 estimates disagree in sign with intervals that each exclude zero.

If none holds, the association is reported with its interval and the limitations in Section 2 and Section 3.4, still as an association. A result that is inconclusive (intervals including zero) is reported as inconclusive. Under the course policy and the proposal's reporting commitment, a null, inconclusive, or fallback outcome is a valid pilot result.

---

## 7. Chaining the assignments

| Assignment | Produces | Used by |
|---|---|---|
| A5 | Distributions, trajectories, the Welch comparison, the simple OLS, the supplementary series, one plot style | A6 comparison specification; A7 figures |
| A6 | Primary estimates, diagnostics, sensitivity table, interpretation, saved results | A7 dashboard reads `results/` and never recomputes |
| A7 | Dashboard presenting trajectories, the shortfall distribution, and the estimates with intervals, labeled as associations | Final presentation |

---

## 8. Provenance, scope approval, and AI assistance

- Lambert's October 14, 2026 A4 feedback (GitHub issue #3) prompted a clearer outcome construct, differential FY2024/FY2025 interpretation, regression-to-the-mean diagnostics and influential-agency review.
- Claude drafted the initial plan from that feedback and the A3 proposal; ChatGPT reviewed the plan, prepared a runnable preliminary analysis, and subsequently built the local A5 implementation presented here. Claude independently reran preliminary model checks. Those activities precede the final course submissions.
- Exploratory coefficient and comparison outputs were **generated and surfaced** on October 14 before this addendum was approved. I clarified that receiving AI messages does not mean I personally studied their statistical results. The research chronology does not assert otherwise.
- I authorized the A5/A6 scope and **local implementation only** on October 14, 2026. Subsequent corrections address reproducibility, documentation, and the rubric; they do not authorize a commit, push, or submission. Current author-review and submission status is recorded in `REVIEW_CHECKLIST.md`.
- The initial A3 exposure, hypothesis, and TWFE specification are unchanged. The extended diagnostics and fallback conventions are **post-feasibility additions**, not claimed as blind pre-analysis commitments.
