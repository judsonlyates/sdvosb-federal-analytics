# AI Use Disclosure

The A2 and A3 disclosures are preserved as written at the time. The A4 disclosure (October 11–12, 2026) follows them.

## Tools used

- Claude (Anthropic, web) — used to plan the project scope and to draft a shell
  script that created the folder structure, `.gitignore`, `LICENSE`, `README.md`,
  and this file's skeleton, and that ran the `uv init` / `uv add` commands.

## Where I used them

- Repository skeleton and documentation drafts (README, .gitignore, LICENSE).
- The first three commits in this repository ("Add initial project structure",
  "Configure UV environment", "Add project README and AI use disclosure") were
  made by the AI-drafted bootstrap script. I read the script before running it,
  ran it myself, reviewed the resulting files and commit history, and made the
  final commit and push by hand.
- Deciding the project topic and its boundaries.
- Assignment 2 feedback revisions (removing the duplicate package, correcting the README structure map, adding tests/test_smoke.py) were drafted with Claude; I ran the commands and the test myself and confirmed 1 passed.

## Where I deliberately did not

- Creating the GitHub repository and configuring my Git credentials.
- This disclosure file's substance for A2 and A3, which I wrote and verified. (The A4 section below was drafted with AI assistance at my direction and is explicit about who did what.)
- Assignment 3's research question and hypothesis will be my own work.

## What the tool got wrong and I caught
The AI-drafted setup script and README were written for a UNIX/MAC environment; running it on Windows through Git Bash, Git warned on every file that LF line endings would be replaced by CRLF, and neither the script nor the README anticipated or documented Windows line-ending behavior.

## Verification

I ran every command in the README on my own machine and confirmed
`uv --version`, `uv sync`, and the pandas/numpy import check succeed.

## Assignment 3

### Where I used AI
- Claude (claude.ai) helped me plan the scope, drafted `docs/proposal.md` from my research question, hypothesis, and scope decisions, and wrote `scripts/feasibility_check.py`.
- Claude transcribed the SBA scorecard values in `data/sample/sba_scorecard_sdvosb.csv` from photos I took of each scorecard page.

### What I decided and did myself
- The research question, the hypothesis and its reasoning, and the decision to narrow the project to an agency-year scorecard pilot.
- Choosing the three sample agencies, opening all 15 scorecard pages (DOE, VA, NASA, FY2021-FY2025), and photographing them.
- Running the feasibility script, editing the repository, and making every commit and push.

### How I verified
- Spot-checked DOE FY2022 (1.99%) and NASA FY2024 (2.57%) in the CSV against my photos.
- Ran `uv run python scripts/feasibility_check.py data/sample/sba_scorecard_sdvosb.csv` and confirmed 3 agencies with complete FY2021-FY2023 data, 2 below 5%, and goals of 3.0 in FY2021-FY2023 and 5.0 in FY2024-FY2025.
- Read the full proposal before submitting; I can explain every section.

### Errors caught during review
- The first draft said government-wide achievement had hovered near 3%. SBA and CRS show 5.07% in FY2023, already above the new goal.
- Carril and Guo was cited with the wrong co-author initial.
- The draft claimed goal credit changed on August 5, 2024. SBA's August 1, 2024 clarification says certification was not required by that date; the goaling requirement begins October 1, 2024, with self-certification allowed through December 22, 2024.
- The draft decision rule counted a positive result in either year as support for H1. Corrected to evaluate each year separately and report mixed results as mixed.
- A CSV note attributed Puerto Rico/territory language to DOE's FY2023 footnote. Corrected to match the actual footnote.

## Assignment 4 (October 11–12, 2026)

### Tools used, and for what

- **OpenAI Codex (October 11–12).** Collected the remaining public SBA
  scorecards (FY2021–FY2025 annual JSON, the 24 FY2020 PDFs, and the discovery
  HTML/JavaScript), wrote and tested the collector, integrated the importable ETL
  into this repository, drafted `schema.sql`, `panel.py`, `verify_rerun.py`, the
  tests, the ERD, the data dictionary, `PIPELINE.md`, `DATA_QUALITY.md`,
  `VALIDATION.md` (Section A), `WALKTHROUGH.md`, the README changes, and the
  review package I then sent out for a second opinion. It also identified and
  documented the source issues listed under "Errors caught."
- **Claude (Anthropic, October 12).** Ran an independent audit of that package
  against the A4 rubric, starting from the package alone: extracted the archive, ran the
  documented commands, recomputed the derived panel from the raw files with its
  own code, ran fault injections and database probes, and reported findings
  (recorded in `VALIDATION.md`, Section B). I then put Claude in charge of
  execution: it applied the five fixes it had found, added two tests, wrote
  this A4 section and the final `WALKTHROUGH.md` and `VALIDATION.md` text at my
  direction, regenerated the evidence in `docs/validation/`, and made the A4
  commits. Those commits carry a `Co-Authored-By` line naming it.
- **ChatGPT Pro.** A second independent review was planned with the same
  package and prompt. It had not been completed when this update was pushed, so
  no ChatGPT finding is incorporated or claimed here.

### What I decided and did myself

- The research design is unchanged from my approved A3 proposal: agency-year
  unit, FY2021–FY2023 baseline, exposure `max(0, 5 − mean)`, the inclusion rule,
  and the associational (not causal) scope. The proposal and the A3 sample are
  byte-identical to the base commit.
- I decided to commission two independent reviews before submitting rather than
  push the preparation output directly, read the Claude audit's verdict and
  findings, and authorized the fixes, this disclosure's wording, and the push.
- Creating the repository, Git credentials, and the earlier commits remain my
  own work as disclosed above.

### Verification performed, and by whom

- Codex ran the test suite and the two-run check in its own Linux environment
  (`VALIDATION.md`, Section A).
- Claude ran them again independently in a second Linux environment, plus the
  recomputation, probes, and fault injections (`VALIDATION.md`, Section B).
- I had not run the A4 commands on my own Windows machine when this was pushed.
  The README documents the route (WSL, or Poppler's `pdftotext` on PATH). I am
  stating that plainly rather than claiming a local run that did not happen.
- The optional base-R check was not run by anyone; R was unavailable in both
  environments.

### Errors caught

Caught by Codex during preparation:

- The A3 feasibility script rejected all negative achievement values. The full
  official panel includes real HUD negatives, so the revised check preserves
  signed achievement and keeps the 0–100 rule for goals.
- The standalone collector lacked the proposed materialized `panel_agency_year`
  table and repository-specific A4 evidence; integration added the derived
  table, normalized relations, ERD, field dictionary, logging, rejection
  metrics, and two-run evidence.
- Failure behavior was strengthened so a missing or corrupt source or a conflict
  does not replace a previously valid database.

Caught by the Claude audit (all low severity, none affecting the data; fixed
before this push and covered by the two added tests):

- The failure log always said the previous database was not replaced, even when
  the failure happened after a validated database had already been written.
- A batch rejected for a missing FY2020 PDF reported zero rejected records.
- The `own_year_pdf` flag text asserted a FY2021 cross-check that is skipped
  when the prior-year value is blank.
- A raw-text prime-table guard in the PDF parser could never fire; the layout
  pass is the real boundary check.
- The console script still printed the A2 "Hello" placeholder.

Caught by me: the A4 errors above were found by the assistants' checks, not by
me, and I am recording that rather than claiming otherwise. What I caught at the
process level was that the preparation output was being presented to me as
verified by one assistant alone; I required a second, independent, executed
review before anything was pushed, and that review found the items listed.

### Review status at push

The design and data rules in this repository are mine and I can explain them.
I read the audit verdict and findings before authorizing this push. The
line-by-line read of the A4 code and the local run are items on the
`WALKTHROUGH.md` checklist, which records what was and was not complete at push
time; I will complete it before the A5 work begins.


## Assignment 5 (October 2026)

This section records material AI assistance with A5. The computational checks
attributed to assistants below were run by them, not by me; my own execution
and review are recorded separately under "Personal execution and review" and
in `LOCAL_EXECUTION_EVIDENCE.md`, Section B. Current status is in
`REVIEW_CHECKLIST.md`.

### Tools used and where

- **ChatGPT / OpenAI (October 14):** Prepared exploratory calculations from the
  frozen data, then drafted the A5 supplementary extraction, analysis module,
  tests, notebook, figures, and methods documentation. It independently audited
  the integrated package, including its statistics, source preservation, and
  rubric coverage.
- **Claude / Anthropic (October 14):** Drafted the analysis-plan addendum from
  the A4 feedback, integrated the A5 files with the graded A4 project, refreshed
  the dependency lockfile, completed documentation, ran the clean-build checks
  recorded in `LOCAL_EXECUTION_EVIDENCE.md`, Section A, and drafted the
  executive summary.
- **OpenAI assistant (October 24):** Corrected the baseline-group and 5%
  threshold wording, narrowed causal and analysis-timing claims, repaired plot
  labels and the methods link, incorporated this disclosure, and performed the
  additional checks recorded in Section C of `LOCAL_EXECUTION_EVIDENCE.md`.
  The assistant prepared a separate corrected review copy without committing
  or pushing it.
- **Claude / Anthropic (October 24):** Independently rebuilt the corrected
  package and reported a successful fresh-kernel notebook run. It found the
  tests-first database dependency and identified remaining submission-copy
  status language.
- **OpenAI assistant (pre-push revision):** Independently reproduced the
  tests-first failure, the successful build and post-build tests, the central
  statistics, and the saved result hashes. At my request it then isolated the
  A5 test fixtures, added regression tests, aligned the formal hypothesis wording
  with the already executed two-sided test, clarified one missing-data footer,
  cleaned up submission documents, and mapped the work to the rubric. The test,
  build, preservation, and notebook execution evidence is separately attributed
  in `LOCAL_EXECUTION_EVIDENCE.md`. No new estimator or statistical result was
  introduced, and this revision did not commit or push the project.

Preliminary numerical outputs were generated and shown before approval of the
October 14 addendum. That does not mean I personally studied those results.
The A3 hypothesis, exposure definition, and primary fixed-effects model remain
unchanged. The extended diagnostics and fallback rules were refined after an
initial feasibility run, not blindly preregistered.

### Where AI was deliberately not used

The student decisions recorded in the A3 disclosure remain mine: the research
question and hypothesis, agency-year scope, and approved exposure definition.
AI execution is not represented as my personal execution or as my
source-to-database walkthrough; those are recorded as my own work below. The
assistants did not perform my understanding or my adoption of the business
interpretation. Section B of the execution record states the steps I
reported completing; Claude formatted that record and this update at my
direction and added nothing I did not report.

### An error I caught

An AI draft incorrectly stated that I had personally reviewed the preliminary
model results. I corrected that claim on October 14: I had not read those
results. The corrected documentation distinguishes outputs generated by AI
from results personally reviewed by me. The baseline-group wording errors,
plot-label problems, and broken methods link were found by the independent
AI audit, not by me.

### Verification ownership

Automated build, test, notebook, and preservation checks performed by the
assistants are attributed to them in `LOCAL_EXECUTION_EVIDENCE.md`, Sections
A, C, and D; they are not claims of execution on my computer. My own execution
is recorded in Section B of that file and summarized below.

### Personal execution and review (completed October 24, 2026)

After the A5 push, I personally completed the documented local workflow on my
own computer: I synced the project dependencies, ran the full A4-to-A5 build,
ran the test suite, ran the A4 two-run reproducibility verification, and
opened the A5 notebook and executed its cells. I traced the NASA and DOE
source values from the frozen SBA files through the database to the baseline
and shortfall calculations. I reviewed the code, the executive summary, the
notebook, and all ten figures, and I reviewed and adopted the final
interpretation and this disclosure. I did not keep terminal logs of that run,
so Section B records outcomes rather than logs, and none of the environment
details or counts reported in the assistants' sections are restated as mine.

### Submission authorization

After receiving the disclosure summary, technical verification, and rubric
review, I expressly authorized the corrected A5 repository update to be
committed and pushed; the OpenAI assistant performed that repository operation
at my direction on October 24, 2026 (commit `94cb1c2`). I then completed the
personal execution and review above and authorized this documentation-only
follow-up commit, which Claude prepared and pushed at my direction. It changes
`AI_USE.md`, `LOCAL_EXECUTION_EVIDENCE.md`, and `REVIEW_CHECKLIST.md` only.
Git history records the actual publication of both updates.
