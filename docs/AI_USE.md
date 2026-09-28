# AI Use Disclosure

Updated: Assignment 2 feedback revisions (September 16, 2026)

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
- This disclosure file's substance, which I wrote and verified.
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