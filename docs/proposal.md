# Agency Differences in SDVOSB Contracting Participation Around the FY2024 Goal Increase

**Author:** Judson L. Yates
**Course:** BUS 751 - Python for Business Analytics
**Date:** September 2026
**Pathway:** Research-Oriented Investigation
**Target output:** Empirical pilot supporting a dissertation paper on federal SDVOSB goal changes; a working paper if results warrant

---

## 1. Introduction & Motivation

Federal agencies are expected to award a share of contract dollars to service-disabled veteran-owned small businesses (SDVOSBs). The National Defense Authorization Act for Fiscal Year 2024 (P.L. 118-31, sec. 863) raised the government-wide SDVOSB goal from 3% to 5%. Government-wide SDVOSB prime-contracting achievement had already reached 5.07% in FY2023, before enactment of the higher goal (CRS, 2024). That aggregate figure does not show whether agencies below the new benchmark subsequently changed differently.

The aggregate hides large differences across agencies. In the pilot sample collected for this proposal, the Department of Veterans Affairs averaged 22.46% SDVOSB achievement over FY2021-FY2023, while the Department of Energy averaged 2.03% and NASA 1.80%. The three sampled agencies' displayed prime-contracting goals rose from 3% in FY2021-FY2023 to 5% in FY2024-FY2025; the remaining agencies' goals will be checked in A4.

Missing a goal carries no legal penalty. Agencies that miss a goal must submit a corrective-action report to SBA (CRS, 2024), and prime-contracting achievement across all goal categories makes up 50% of each agency's annual scorecard grade (SBA, n.d.-b). Whether this procedural and reputational pressure is associated with changed outcomes is an open empirical question, relevant to SDVOSB firms deciding where to compete, to SBA, which negotiates agency goals, and to Congress.

**Research question:** Is an agency's distance below the 5% benchmark before the goal increase associated with larger subsequent increases in its SBA-reported SDVOSB achievement?

## 2. Pathway & Target Contribution

- **Pathway:** Research-Oriented Investigation
- **Intended audience / target venue:** Public procurement and small-business policy researchers; the dissertation committee; the SBA and congressional audience that reads procurement scorecards.
- **Contribution:** The pilot will produce estimates, with uncertainty, of whether changes in SBA-reported SDVOSB achievement in FY2024 and FY2025 varied with agencies' pre-policy distance below 5%, and an assessment of whether this agency-year design merits expansion in the dissertation.

## 3. Literature Review & Research Gap

- **What prior work establishes:** Mandatory preference programs change who wins federal contracts. Carril and Guo (2026) study the expansion of VA veteran set-asides following *Kingdomware Technologies, Inc. v. United States* (2016), examining vendor entry, survival, competition, and contract execution. Earlier work examines small-business set-asides' effects on procurement cost (Denes, 1997) and bidding in Japanese public construction auctions (Nakabayashi, 2013). CRS reports document goal attainment at the government-wide level (CRS, 2024, 2026).
- **The specific gap:** A procurement goal differs from a preference program: it is a negotiated, non-binding target. To my knowledge, no published study examines whether agencies' reported SDVOSB achievement changed differently after the FY2024 increase according to how far below the new benchmark they started.
- **How this study addresses it:** It uses cross-agency variation in pre-policy distance below 5%, measured from SBA's own scorecards, and compares subsequent changes in FY2024 and FY2025. The contribution is a preliminary association, not a causal estimate.

## 4. Research Question & Hypotheses

- **Primary research question:** Is an agency's distance below the 5% benchmark, measured before the goal increase, associated with larger increases in its SBA-reported SDVOSB achievement afterward?

- **Expected relationship and reasoning:** Agencies further below the benchmark have more ground to make up. Public scorecards and corrective-action reporting may lead agency leadership to give SDVOSB participation greater attention in procurement planning. Agencies already above 5% may face less pressure to change existing practices.

- **Hypothesis 1 (H1):** Greater distance below the 5% benchmark, measured using average FY2021-FY2023 achievement, is associated with larger increases in SBA-reported SDVOSB achievement in FY2024 and FY2025, evaluated separately.
  - **Null (H0_t):** For each post-policy year t (FY2024, FY2025), beta_t = 0: distance below the benchmark is unrelated to that year's change in achievement.
  - **Decision rule and falsification condition:** H1 predicts beta_t > 0 in each year. I will report each estimate with a two-sided 95% confidence interval. An interval wholly above zero supports that year's prediction; an interval wholly below zero contradicts it; an interval containing zero is inconclusive for that year. Different conclusions across the two years will be reported as mixed evidence. Support for H1 in both years requires positive evidence in both years.

- **Operationalization:**
  - *SDVOSB achievement* (outcome, agency x fiscal year): the SBA-reported SDVOSB prime-contracting achievement percentage from the agency's scorecard for that fiscal year, recorded as displayed (2.42 for 2.42%). This is SBA's goaling measure, not an unadjusted obligation share: it includes double credit for local-area set-asides (and, in some years, Puerto Rico and territory awards) and, for DOE, M&O first-tier subcontracts in at least FY2021-FY2023.
  - *Distance below the benchmark* (exposure, fixed per agency): S_a = max(0, 5 - mean achievement FY2021-FY2023), in percentage points. Pilot values: NASA 3.20, DOE 2.97, VA 0. Agencies with S_a = 0 were also subject to the national change; they are low-exposure, not untreated.
  - *Post-policy years:* separate indicators for FY2024 and FY2025. The NDAA was signed in December 2023, three months into FY2024. The statute requires that, beginning October 1, 2024, contracts counted toward SDVOSB goals be with VetCert-certified firms; SBA's clarification allows self-certification through December 22, 2024 and continued treatment for timely applicants awaiting a decision (SBA, 2024a, 2024b). FY2024 and FY2025 are therefore estimated separately.
  - *Agency goal:* the displayed SDVOSB goal for each scorecard year, recorded to document the target change.
  - *Agency:* a stable identifier (e.g., DOD for the agency now displayed as the Department of War) so display-name changes do not create duplicate agencies.

## 5. Data

| Source | Variables / fields | Frequency | Coverage | Accessibility |
|---|---|---|---|---|
| SBA interactive procurement scorecards, FY2021-FY2025 | SDVOSB prior-year achievement, current goal, current achievement, dollars, footnotes | Annual | 24 scored agencies | Public (SBA, n.d.-a). Each page is addressable by URL, e.g. `sba.gov/certifications/scorecard-details/?agency=DOE&scorecard_year=2021`. Collected into a documented CSV; scripted retrieval evaluated in A4. |
| SBA scorecard PDFs, FY2020 and earlier | Same fields | Annual | 24 agencies | Public legacy SBA site; used only if FY2020 goal values are needed. |
| USAspending.gov contract data (assessed, not used in the pilot) | Obligations, awarding agency, SDVOSB flag, set-aside type, NAICS | Transaction | Reported federal prime-contract award transactions; coverage depends on reporting requirements and extract filters | Public bulk download and API (U.S. Department of the Treasury, n.d.). Reconstructing SBA's goaling definitions from transaction-level records is outside this pilot's scope. |

**Pilot sample (collected September 27, 2026).** The committed CSV is a 144-row template (24 agencies x FY2020-FY2025); 18 rows are populated for three agencies and the rest are not yet collected. Values investigated and found unavailable will be left blank with an explanation in notes. The populated observations are at `data/sample/sba_scorecard_sdvosb.csv`, each with source URL, scorecard edition, retrieval date, and notes. Achievement (%), with goal in parentheses:

| Agency | FY2020 | FY2021 | FY2022 | FY2023 | FY2024 | FY2025 |
|---|---|---|---|---|---|---|
| DOE | 1.21 | 1.69 (3.00) | 1.99 (3.00) | 2.42 (3.00) | 2.30 (5.0) | 2.36 (5.00) |
| VA | 20.24 | 23.76 (3.00) | 16.45 (3.00) | 27.16 (3.00) | 23.63 (5.0) | 21.68 (5.00) |
| NASA | 1.65 | 1.59 (3.00) | 1.46 (3.00) | 2.34 (3.00) | 2.57 (5.0) | 2.26 (5.00) |

FY2020 values come from the FY2021 scorecard's prior-year column, which shows no FY2020 goal.

- **Sample construction:** Population: the 24 agencies SBA scores. Unit: agency x fiscal year, FY2020-FY2025 (at most 144 rows). Inclusion rule, fixed before collection: an agency enters the analysis if it has achievement values for all of FY2021-FY2023 and at least one post-policy year, regardless of those values. Available observations are retained, missing years are documented, and missing achievement is never imputed as zero. Each estimate reports the agencies and observations used.
- **Data quality & sufficiency:** In the pilot, the goal moved from 3% to 5% for all three agencies, and no differences were found in the 12 overlapping prior-year/current-year achievement comparisons checked. Values appear at varying precision (2.3% on one page, 2.30% on the next) and are recorded as displayed. Open comparability questions for A4: DOE's footnote mentions M&O first-tier subcontracts through FY2023 but not in FY2024-FY2025, which may reflect a measurement change or only shorter wording; and the certification requirement may affect what counts toward the outcome in FY2025. The sample demonstrates access and measurement feasibility. It does not establish full-panel coverage or the amount of exposure variation across all 24 agencies.

## 6. Methods & Identification Strategy

- **Estimator / model:** One primary unweighted OLS regression with two-way fixed effects on the agency-year panel:

  Y_at = alpha_a + gamma_t + beta_2024 (S_a x I[t = 2024]) + beta_2025 (S_a x I[t = 2025]) + e_at

  Y_at is SDVOSB achievement; alpha_a are agency fixed effects; gamma_t are fiscal-year fixed effects (with the usual omitted year). FY2020-FY2023 form the omitted exposure-interaction period. beta_t is the difference in that year's achievement, in percentage points, per percentage point of pre-policy distance below 5%, relative to FY2020-FY2023. Each agency-year observation receives equal weight; the regression is not weighted by procurement dollars. I will report 95% agency-clustered confidence intervals using the finite-sample correction and a t reference distribution with G-1 degrees of freedom, where G is the number of agencies in the fitted model. With at most 24 agencies, inference remains provisional.
- **Identification:** The coefficients are associations. A causal reading would require that, absent the goal increase, agencies further below 5% would have followed the same achievement trends as agencies above it. The pilot cannot establish that: exposure is constructed from FY2021-FY2023 outcomes and only FY2020 lies outside that window, so the short pre-period and outcome-based exposure limit any pre-trend check. Regression to the mean is a direct competing explanation, and the certification requirement is a concurrent change the design cannot separate from the goal.
- **Validation & robustness:** (1) Plot achievement by agency and by whether exposure is positive or zero, FY2020-FY2025. In a separate diagnostic specification, add delta_2020 x S_a x I[t = 2020] to the primary model, with FY2021-FY2023 as the omitted exposure-interaction years. This checks a limited pre-period difference; it does not establish parallel trends or remove regression to the mean. (2) Re-estimate with exposure measured from FY2023 alone. (3) Leave-one-agency-out re-estimation, including fits excluding VA and DOE.

## 7. Analysis Plan & Expected Outcomes

- **Pre-specified analyses:** (a) descriptive trends and distributions by agency and exposure group; (b) the primary regression; (c) diagnostic and robustness checks (1)-(3).
- **Interpretation:** Applied year by year as in Section 4. A result that holds in FY2024 but not FY2025, or the reverse, is reported as mixed. Any FY2025 result carries the certification caveat. A robustness check that reverses a sign is reported alongside the primary estimate.
- **Reporting commitment:** Null, inconclusive, and mixed results will be reported as findings, with confidence intervals describing which associations the data can and cannot rule out.

## 8. Contribution & Significance

- **Contribution to the literature:** A preliminary, agency-level look at whether changes in reported SDVOSB achievement after a non-binding goal increase varied with baseline shortfall, complementing work on mandatory veteran set-asides (Carril & Guo, 2026).
- **Contribution to practice:** For SDVOSB firms, evidence on which agencies' reported achievement moved after the increase. For SBA and Congress, preliminary evidence on whether changes in reported achievement varied with agencies' baseline shortfalls, informing a more extensive evaluation.
- **Success metrics (independent of the results):** (1) An agency-year panel for all agencies meeting the inclusion rule, with available observations retained, missing years documented, and a source URL and retrieval date for every value; (2) a reproducible pipeline from source CSV to validated SQLite tables with tests; (3) primary estimates and robustness checks reported with confidence intervals; (4) a deployed dashboard; (5) documented resolution or disclosure of the comparability questions in Section 5.

## 9. Threats to Validity, Limitations & Fallback

- **Internal validity:** Regression to the mean; the certification requirement as a concurrent change; agency-specific shocks unrelated to the goal; possible measurement differences in agency footnote rules (DOE). Exposure is not randomly assigned.
- **Statistical:** At most 24 agencies means few clusters, and two post-policy years limit precision.
- **Construct / external validity:** Distance below the government-wide benchmark is a proxy for compliance pressure, not a direct measure. SBA-reported achievement measures goaling credit, not only dollars to SDVOSBs. Results describe one goal change for one category.
- **Fallback:** If coverage or comparability does not support the regression, the pilot becomes a transparent descriptive study on the same panel, with trajectories by exposure group and a documented account of why the design cannot estimate the association at this scale. The data pipeline and dashboard are delivered either way, and the panel carries into the dissertation.

## 10. Technical Implementation & Reproducibility

- **Database:** SQLite with `agencies` (stable ID, display names over time), `scorecard_observations` (agency, observation year, scorecard edition, achievement, goal, dollars, source URL, retrieval date, notes), and a derived `panel_agency_year` table.
- **Analysis:** Python 3.11 managed with UV (`pyproject.toml`, `uv.lock`); pandas for cleaning; statsmodels for the fixed-effects regression; pytest for data validation (duplicate agency-years, value ranges, goal checks), building on `scripts/feasibility_check.py`, which currently checks ranges and duplicates, not source accuracy or full-panel availability.
- **Dashboard:** Streamlit: agency selector, achievement trajectories, exposure values, and estimates with intervals.
- **Deployment:** Deploy the app from GitHub to Streamlit Community Cloud; separately provide a tested Dockerfile and local container run instructions.

| Dates | Milestone / activities | Course anchor |
|---|---|---|
| Sep 28 - Oct 11 | Collect remaining agencies; evaluate scripted retrieval; SQLite schema; import, cleaning, validation tests; investigate DOE footnote | A4 (Oct 11); Residency 2 (Oct 2-3) |
| Oct 12 - Oct 25 | Trends, distributions, missingness, agency comparisons; exposure distribution for all agencies | A5 (Oct 25) |
| Oct 26 - Nov 8 | Primary regression, diagnostic, robustness checks | A6 (Nov 8) |
| Nov 9 - Nov 20 | Dashboard, Community Cloud deployment, Dockerfile, documentation | A7 (Nov 20) |
| Nov 21 - 22 | Final review and presentation | Final (Nov 22) |

## 11. References

- Carril, R., & Guo, A. (2026, July). *The impact of preference programs in public procurement: Evidence from veteran set-asides* [Working paper]. https://rcarril.github.io/website/VA_setasides.pdf
- Congressional Research Service. (2024, June 6). *Service-disabled veteran-owned small business contracting program changes* (CRS Insight IN12313). https://www.everycrsreport.com/reports/IN12313.html
- Congressional Research Service. (2025, July 22). *Federal small business contracting goals* (CRS Insight IN12018). https://www.everycrsreport.com/files/2025-07-22_IN12018_b8a950650c9af56ea4dab1fd19a9a80a8015ca41.pdf
- Congressional Research Service. (2026, September 8). *Service-disabled veteran-owned small business contracting program* (CRS In Focus IF13309). https://www.everycrsreport.com/reports/IF13309.html
- Denes, T. A. (1997). Do small business set-asides increase the cost of government contracting? *Public Administration Review, 57*(5), 441-444. https://doi.org/10.2307/3109990
- *Kingdomware Technologies, Inc. v. United States*, 579 U.S. 162 (2016).
- Nakabayashi, J. (2013). Small business set-asides in procurement auctions: An empirical analysis. *Journal of Public Economics, 100*, 28-44. https://doi.org/10.1016/j.jpubeco.2013.01.003
- National Defense Authorization Act for Fiscal Year 2024, Pub. L. No. 118-31, secs. 863-864 (2023). https://www.govinfo.gov/content/pkg/PLAW-118publ31/pdf/PLAW-118publ31.pdf
- U.S. Department of the Treasury. (n.d.). *USAspending API documentation*. Retrieved September 27, 2026, from https://api.usaspending.gov/docs/
- U.S. Small Business Administration. (2024a, June 6). Eliminating self-certification for service-disabled veteran-owned small businesses. *Federal Register, 89*, 48266-48269.
- U.S. Small Business Administration. (2024b, August 1). Clarification to direct final rule on eliminating self-certification for service-disabled veteran-owned small businesses. *Federal Register, 89*, 62653. https://www.govinfo.gov/content/pkg/FR-2024-08-01/pdf/2024-16961.pdf
- U.S. Small Business Administration. (n.d.-a). *Scorecard details* [Interactive agency scorecards]. Retrieved September 27, 2026, from https://www.sba.gov/certifications/scorecard-details/
- U.S. Small Business Administration. (n.d.-b). *Small business procurement scorecard overview*. Retrieved September 27, 2026, from https://legacy.sba.gov/document/support-small-business-procurement-scorecard-overview
