# Collection results and interpretation notes

## Coverage and validation

As retrieved October 11, 2026, the official SBA sources provide 143 complete observations out of the planned 144 rows. FY2020–FY2024 each have 24 complete agency rows. FY2025 has 23, with USAID reporting N/A for achievement, goal, dollars, and footnotes and no explanatory comment. The row remains in the panel, with missing values rather than zeros. No reason for the missing source values is assumed.

The 18 previously populated sample observations contain 48 nonblank numerical cells. Every one matches the new extraction exactly in numerical terms. The sample file and proposal were preserved unchanged. All 336 comparisons of target-year achievements with later scorecards' historical columns agree, including all 120 adjacent-year checks and all 24 FY2020 PDF-to-FY2021 checks.

The new collector retrieves the data actually used by SBA's interactive scorecard page. The saved HTML identifies its public data directory, and the saved JavaScript shows annual JSON loading and direct field-to-display hydration. These sources are not a substitution from SAM or USAspending. FY2020 is extracted independently from official legacy SBA PDFs with raw-text and page-layout checks constrained to the prime-contracting table.

- Scorecard interface: https://www.sba.gov/certifications/scorecard-details/
- Example annual data: https://www.sba.gov/app/mu-plugins/sba-agency-scorecards/data/agency-scorecards-2023.json
- FY2020 legacy overview: https://legacy.sba.gov/document/support-small-business-procurement-scorecard-overview

## HUD negatives and the FY2022 measurement break

HUD reports FY2020 achievement of -5.04% and dollars of -$50.6 million, and FY2021 achievement of -1.57% and dollars of -$15.4 million. The FY2021 SBA scorecard's agency comments explain the negative figures as the effect of deobligating prior-year funds. These are recorded source values, not parser errors.

The original `feasibility_check.py` applies a 0–100 rule to achievement and consequently fails on these rows. The failure was reproduced and logged. The revised check in this portfolio allows signed achievement, flags it, and keeps the 0–100 rule for goals.

Beginning FY2022, SBA changed its treatment of deobligations: it excludes deobligations on awards with no positive obligation in the current or prior fiscal year. This is not an exclusion of every negative transaction. The change applies to both small and other-than-small business awards. The approved FY2021–FY2023 baseline straddles this break. It is especially important for HUD and can confound apparent changes around the later goal increase.

Possible sensitivity analyses for discussion with the instructor include excluding HUD and using FY2022–FY2023 for an alternative baseline. The A4 pipeline does not silently change the submitted design or delete observations.

- HUD FY2020 PDF: https://legacy.sba.gov/sites/default/files/2021-07/HUD-508.pdf
- FY2021 JSON, HUD agency comments: https://www.sba.gov/app/mu-plugins/sba-agency-scorecards/data/agency-scorecards-2021.json
- SBA Federal Register notice, June 22, 2022: https://www.govinfo.gov/content/pkg/FR-2022-06-22/pdf/2022-13287.pdf

## DOE definition caveat

The FY2020 DOE PDF explicitly mentions DOE MOSRC dollars. FY2021–FY2023 scorecard footnotes explicitly include M&O first-tier subcontracting in prime-contracting achievement. FY2024–FY2025 omit that phrase.

DOE's current explanatory page says SBA allows first-tier M&O/FMC subcontract awards to count in its prime small-business totals, with these data tracked through MOSRC. This supports keeping the definitional caution. The omission of wording in later scorecards does not prove those dollars stopped being included. Exact annual SDVOSB treatment remains unresolved; the official scorecard values are retained without substitution from an unadjusted prime-only series.

- DOE explanation: https://www.energy.gov/osbp/doing-business-doe
- DOE scorecards: https://www.energy.gov/osbp/sba-scorecards
- DOE FY2020 PDF: https://legacy.sba.gov/sites/default/files/2021-07/DOE-508_0.pdf

## VA FY2023 discrepancy

SBA's FY2023 scorecard reports 27.16% and $10.4 billion; its FY2024 prior-year column repeats 27.16%. The committed sample agrees. CRS Table 5 in R47226 reports a 16.7% figure from SAM and a $62.6 billion small-business-eligible base. CRS notes that dynamic source updates can produce differences from SBA scorecards.

The SBA displayed figures imply a denominator of roughly $38.3 billion, far from $62.6 billion, so this is not a rounding explanation. The exact denominator, exclusion, or source-vintage mechanism has not been established. The requested outcome is SBA scorecard achievement, so 27.16% is retained and the alternative measure is flagged rather than mixed into the panel.

- SBA FY2023 JSON: https://www.sba.gov/app/mu-plugins/sba-agency-scorecards/data/agency-scorecards-2023.json
- CRS report: https://www.congress.gov/crs-product/R47226

## Other limitations

SBA achievement includes goaling credits rather than only unadjusted transaction dollars. Public source footnotes mention double credit for local-area set-asides and, in some editions, Puerto Rico and covered territories. The full annual footnotes and comments are retained in the provenance output.

FY2025 certification changes remain a concurrent policy/measurement caveat from the submitted proposal. Agency name labels are recorded as displayed today, so historical labels in current JSON may reflect retrospective renaming. Dollars are rounded at source and cannot support exact procurement accounting.

All 24 agencies meet the submitted inclusion criterion, and the baseline exposure has 12 agencies below 5% and 12 at or above it. No hypothesis test or causal estimate was run. The unresolved comparability issues should be addressed before drawing substantive conclusions.
