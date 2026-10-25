# Executive Summary: Agency-Level SDVOSB Goaling Achievement Around the FY2024 Goal Increase

**Assignment 5, BUS 751 · Judson L. Yates · October 2026**

## The question

In FY2024 the government-wide goal for contracting with service-disabled veteran-owned small businesses rose from 3% to 5%. Using each agency’s FY2021–FY2023 average, twelve of the 24 scored agencies had a positive shortfall from 5% and twelve had zero shortfall. These are fixed three-year-baseline groups, not FY2023 achievement categories: fourteen agencies were at or above 5% in FY2023 alone. Did the positive-shortfall group show larger subsequent increases?

## What the data show

**The mean-change comparisons are inconclusive in both years.** The baseline-positive-shortfall group raised its SBA-reported SDVOSB achievement by 0.4 percentage points on average from FY2023 to FY2024; the zero-shortfall group moved by less than 0.1. The estimated difference is +0.371 points, but its 95% interval runs from −1.302 to +2.044 points. FY2025 has a larger estimated difference (+1.155 points) and a wider interval, from −2.624 to +4.934. The comparisons do not establish larger increases in the positive-shortfall group, and they do not establish that the groups changed equally.

**The movement is agency by agency, not group by group.** Eight of the twelve baseline-positive-shortfall agencies rose in FY2024 and four fell. The largest single gain in both years belongs to a zero-shortfall agency, the Small Business Administration, whose reported achievement rose from about 44% in FY2023 to about 60% in FY2025. Large declines also occur in the zero-shortfall group (GSA, VA, OPM). Four agencies in the baseline-positive-shortfall group reported at least 5% in FY2025: Treasury, HUD, State, and USDA. HUD and USDA had already exceeded 5% in FY2023. The other seven reporting agencies in that group remained below 5% in FY2025; USAID was missing.

**The baseline groups were on different paths before the goal changed.** The zero-shortfall group averaged about 7.6% in FY2020 and 13% by FY2023; the positive-shortfall group rose from about 1.8% to 3.2% over the same years. The gap between the groups was widening before FY2024, which is one reason a simple before-and-after comparison cannot be read as an effect of the goal.

## What this means

*For an SDVOSB deciding where to compete:* the scorecards tell you which agencies award a large share to SDVOSBs and which do not, and that is useful. They do not show that any agency changed its buying because of the new goal. Agency selection should rest on where the work is (NAICS demand, forecasted solicitations, contract vehicles) and on relationships, not on the expectation that a lagging agency will now catch up.

*For SBA and agency small-business offices:* these exploratory comparisons do not establish a larger increase among baseline-positive-shortfall agencies. They cannot determine whether the policy caused changes. Agency-specific targets and procurement practices are useful context to investigate, but this analysis does not measure their effects.

*For the research:* the A5 group comparison and the originally approved A3 continuous-exposure fixed-effects model estimate different contrasts. Assignment 6 will evaluate that original model separately. The extended diagnostics and fallback rules in `docs/ANALYSIS_PLAN.md` were refined after an initial feasibility run, not blindly preregistered.

## Why the numbers are bounded

The outcome is SBA's goaling-credit measure, not a count of firms or contracts. The baseline years straddle a FY2022 change in how SBA treats deobligations, DOE's achievement includes M&O subcontracts in at least some years, VA's figure uses a denominator that differs from other published measures, and the FY2025 figures reflect new certification rules. FY2023 appears in both the shortfall measure and the change, so an unusually low FY2023 inflates both. The supplementary contractor counts describe how many SDVOSB prime contractors each agency reported, not how many firms entered federal contracting.

---

### Technical detail

Primary test: Welch's two-sample t-test on the FY2023→FY2024 change in achievement, positive-shortfall (n = 12) versus zero-shortfall (n = 12) agencies. This exploratory test was documented after an initial feasibility run; it is not a blinded pre-analysis commitment. Difference +0.371 points, 95% CI [−1.302, +2.044], t = 0.47, df = 15.7, p = 0.644, Hedges' g = 0.19. Shapiro-Wilk rejected normality in the positive-shortfall group (p < 0.001); Mann-Whitney sensitivity U = 73, p = 0.977, rank-biserial 0.01. Spearman correlation between continuous shortfall and FY2024 change: ρ = −0.01 (p = 0.96). FY2025 (n = 23; USAID missing): difference +1.155, 95% CI [−2.624, +4.934], p = 0.520; Mann-Whitney p = 0.053; Spearman ρ = 0.36 (p = 0.09). Simple OLS of FY2024 change on shortfall: slope +0.014 per point (HC3 p = 0.95); adding log FY2023 SDVOSB dollars does not change the conclusion. Full tables in `results/`, figures in `figures/`, methods in `docs/A5_METHODS.md`.
