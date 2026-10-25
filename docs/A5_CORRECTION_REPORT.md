# Assignment 5 correction record

## October 24 corrections retained

The corrected review ZIP fixed the baseline/threshold wording, inconclusive
rather than equal-change interpretation, exploratory chronology, two crowded
scatterplots, benchmark step, methods link, AI-use attribution, and A5
read-only/path-collision guards. Its separately attributed logs remain under
`validation/a5_revision_2026-10-24/`. The original uploaded ZIP is preserved.

## Pre-push follow-up

- Replaced the build-order-dependent A5 test fixture with a session-level,
  temporary offline A4 build and temporary A5 tables. Updated the collision/hash
  tests to use that fixture and added two regression tests. The graded A4 test
  modules and pipeline source are unchanged.
- Aligned the formal A5 H0/H1 wording with the existing two-sided Welch test.
  The scientific directional expectation, A3 primary model, estimators, and
  all numerical results are unchanged.
- Clarified the working independence assumption, small population, rank-test
  interpretation, and exploratory/multiple-diagnostic inference boundaries.
- Added the missing-USAID explanation to the FY2025 scatter footer; its markers
  and estimates are unchanged.
- Removed repetitive draft-status labels from the README, summary, methods,
  and notebook conclusion. Current author-review status is centralized in
  `REVIEW_CHECKLIST.md`, not marked complete by an assistant.
- Updated the A5 disclosure with material assistant roles, actual execution
  ownership, and no invented local run or personal adoption.
- Added a rubric evidence map without an AI-generated grade estimate.
- Kept review-request scaffolding, the stale review-package inventory, and the
  earlier AI score estimate out of the submission tree. The original copies
  remain preserved outside that tree and in the original ZIP.
- Preserved the A2–A4 AI-disclosure history verbatim.

## Verification ownership

The OpenAI assistant performed the checks in `LOCAL_EXECUTION_EVIDENCE.md`,
Section D. These checks are not a claim that Judson ran commands on his own
computer. A final author review and a separate push authorization remain
distinct from technical readiness. No commit or push was performed.

## Source-to-shortfall trace examples

These verified examples support the walkthrough; reading them is not recorded
as proof that the author independently completed it.

- NASA FY2023: `agency-scorecards-2023.json`, agency `NASA`,
  `prime_sdvosb_cfy_achievement` = 2.34%. FY2021–FY2023 values:
  1.59%, 1.46%, 2.34%; mean 1.7966667%; shortfall 3.2033333 points.
- DOE FY2023: agency `DOE`, current-year achievement 2.42%. Baseline:
  1.69%, 1.99%, 2.42%; mean 2.0333333%; shortfall 2.9666667 points.
  The M&O footnote means this must not be described as an unadjusted
  prime-contract award share.
- HUD and USDA: FY2023 values 5.36% and 5.43%, but baseline means
  2.70% and 4.7233333%. Both have positive three-year-baseline shortfall.
  This explains why 12/12 baseline groups differ from the 14 agencies
  achieving at least 5% in FY2023 alone.
