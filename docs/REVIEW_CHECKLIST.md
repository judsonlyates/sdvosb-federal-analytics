# Assignment 5 review and submission record

## Author review and personal execution (completed)

I completed the documented local workflow and review below. My confirmation
is recorded in
[Section B of the execution record](LOCAL_EXECUTION_EVIDENCE.md#section-b-student-verification-completed);
the assistants' earlier checks are recorded separately.

- [x] Synced dependencies and successfully ran the full A4-to-A5 build, the test suite, and the A4 two-run verifier on my own computer.
- [x] Opened the A5 notebook and executed its cells.
- [x] Read the executive summary and notebook conclusion and adopted the interpretation.
- [x] Traced the NASA and DOE source values through the database to the baseline and shortfall calculations; can explain the 12/12 baseline split, the 14 agencies at or above 5% in FY2023, and the inconclusive intervals.
- [x] Reviewed the code, all ten figures, and the A5 AI disclosure.
- [x] Inspected the final changed-file list.
- [x] Authorized the corrected A5 submission and the documentation follow-ups.

## Technical verification (assistant-run checks)

The following results are from the assistants' runs, not a transcript of my
local run. Section D of `LOCAL_EXECUTION_EVIDENCE.md` records the pre-push
checks; Sections A and C retain the earlier preparation history.

- [x] Locked Python 3.11 environment installed without a lockfile change.
- [x] All 60 tests and 5 subtests pass before any project database exists.
- [x] Tests leave the project-output A4 database absent; test inputs are temporary.
- [x] Full offline A4-to-A5 pipeline passes; tests also pass after building.
- [x] All 55 frozen sources and nine A4 logical tables pass preservation checks.
- [x] All six A5 numerical result files retain their original hashes.
- [x] Ten figures reviewed; the FY2025 scatter footer explains missing USAID.
- [x] Hypotheses align with the executed two-sided Welch test.
- [x] Rubric evidence is mapped in `A5_RUBRIC_EVIDENCE.md`.
- [x] Five actual notebook code cells execute in-process with zero errors.

### Execution-environment note

The OpenAI runner could not launch a fresh Jupyter kernel because of runtime
permissions. Its in-process execution is recorded as such, not as a
fresh-kernel test. Claude separately reported successful fresh-kernel runs.
My own notebook execution is recorded above. This note describes a limitation
of one verification environment, not unfinished author review.

## Submission

The included A5 specification requires a push to the existing GitHub
repository, with no separate LMS upload. Its deadline is Sunday, October 25,
11:59 PM; the specification does not state a timezone.

The A5 package was pushed on October 24, 2026 (commit `94cb1c2`) at my express
authorization. The later documentation updates record my completed review
and clarify the disclosure. They do not change code, data, figures, results,
or the notebook. Git history is the publication record.
