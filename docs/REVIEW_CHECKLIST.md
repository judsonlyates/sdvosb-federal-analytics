# Assignment 5 review and submission checklist

## Technical status (assistant-run checks)

The pre-push corrections and assistant-run checks are complete. These are the
assistants' runs, recorded separately from my own execution below. See
`LOCAL_EXECUTION_EVIDENCE.md`, Section D, for those checks; Sections A and C
retain the separately attributed preparation history.

- [x] Locked Python 3.11 environment installed without a lockfile change.
- [x] All 60 tests and 5 subtests pass before any project database exists.
- [x] Tests leave the project-output A4 database absent; test inputs are temporary.
- [x] Full offline A4-to-A5 pipeline passes; tests also pass after building.
- [x] All 55 frozen sources and nine A4 logical tables pass preservation checks.
- [x] All six A5 numerical result files retain their original hashes.
- [x] Ten figures reviewed; the FY2025 scatter footer now explains missing USAID.
- [x] Hypotheses align with the already executed two-sided Welch test.
- [x] Rubric evidence is mapped in `A5_RUBRIC_EVIDENCE.md`.
- [x] Five actual notebook code cells execute in-process with zero errors.
- [ ] Fresh-kernel execution independently certified by the current OpenAI runner.
      Its kernel launch is blocked by runtime permissions. Claude separately
      reported a successful fresh-kernel check on the preceding corrected copy
      and again on the pushed commit; those reports are not relabeled as an
      OpenAI or student-computer execution.

## Author review and personal execution (completed October 24, 2026)

Completed by me on my own computer after the push, as recorded in
`LOCAL_EXECUTION_EVIDENCE.md`, Section B. These are my own actions, not the
assistants' runs relabeled.

- [x] Synced dependencies and ran the documented A4-to-A5 build, the test suite, and the A4 two-run verifier successfully.
- [x] Opened the A5 notebook and executed its cells.
- [x] Read the executive summary and notebook conclusion and adopted the interpretation.
- [x] Traced the NASA and DOE source values through the database to the baseline and shortfall; can explain the 12/12 baseline split, the 14 agencies at or above 5% in FY2023, and the inconclusive intervals.
- [x] Reviewed the code, all ten figures, and the A5 AI disclosure, and adopted the disclosure.
- [x] Inspected the final changed-file list.
- [x] Separately authorized the commit/push of the corrected A5 package, and this documentation-only follow-up.

## Submission

The required submission is a push to the existing GitHub repository; there is
no separate LMS upload in the included A5 specification. The deadline is Sunday,
October 25, 11:59 PM; the specification does not state a timezone. The A5
package was pushed on October 24, 2026 (commit `94cb1c2`) at my express
authorization. This follow-up commit changes documentation only, to record the
author review and personal execution above; no code, data, figure, result, or
notebook file is changed by it. Git history is the authoritative publication
record.
