# Review walkthrough before submission

This guide explains the implementation and separates preparation checks from the student's own review.

1. Open `docs/proposal.md`. Explain the agency-year unit, the 5% benchmark, and why the study estimates association rather than causality.
2. Open `src/sdvosb_federal_analytics/schema.sql` and `docs/ERD.md`. Explain why an agency ID is separate from an edition-specific name, why one agency-year key prevents duplicate facts, and why each fact links to a hashed source document.
3. Follow `etl.run_pipeline()`: extract/verify sources, parse/transform, reconcile/validate, then load. Read `parse_pct()`, `parse_dollars()` and the PDF boundary checks. Explain how a failed source differs from official N/A.
4. Run the README pipeline command. Inspect `data/processed/validation_summary.json` and `pipeline.log`. Expect 144 rows, 143 complete observations, zero duplicates/rejections, 48 sample matches, and 336 historical overlaps.
5. Inspect the source and output for HUD FY2020/FY2021, USAID FY2025, DOE's footnotes, and VA FY2023. Explain why negatives and NULL are retained and why 27.16% is not replaced with another measure.
6. Read `panel.py`. Explain max(0, 5 − mean FY2021–FY2023), the three-year completeness requirement, and why USAID stays in the agency population but its missing FY2025 outcome is not analysis-ready.
7. Run the tests (40 plus 5 subtests) and the two-run command. Open `rerun_verification.json` and verify every table's row count and logical hash agree. Test success does not by itself prove the research design.
8. Read `docs/AI_USE.md`. Its A4 section records who did what and what was not done; update it whenever the status below changes (for example after the local run or the ChatGPT review). Do not claim agreement or verification that did not happen.
9. Compare the final repository with the actual A4 rubric. The A4 commits are real and descriptive and carry a `Co-Authored-By` line for the assistant that made them; nothing was backdated. Pushing the existing repository is the course submission step; nothing is submitted to a course platform.

## Student checks: status at the A4 push (October 12, 2026)

- [x] I reviewed the independent audit's verdict and findings and authorized the fixes and the push.
- [ ] I reviewed the schema, pipeline, validation rules and source caveats line by line. — To complete before A5.
- [ ] I ran the documented commands in my own environment. — Not run locally at push time; both AI-run records are in `docs/VALIDATION.md`. Route for Windows: WSL, or Poppler's `pdftotext` on PATH, then the four README commands.
- [ ] I can explain the code and identify the parts drafted with AI. — The AI-drafted parts are identified in `docs/AI_USE.md`; the explanation walk-through (steps 1–7 above) is to complete before A5.
- [x] I reviewed independent model feedback and resolved evidence-backed differences. — Claude audit: reviewed; five findings fixed. ChatGPT Pro review: not completed at push time.
- [x] I authorized the intended GitHub update. — The complete diff was summarized to me by the audit; the full line-level diff review is part of the line-by-line item above.

These are statements of what had actually been done when the A4 update was pushed, not assertions that every step is finished.
