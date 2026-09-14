# AI Use Disclosure

Updated: Assignment 2 (September 13, 2026)

## Tools used

- Claude (Anthropic, web) — used to plan the project scope and to draft a shell
  script that created the folder structure, `.gitignore`, `LICENSE`, `README.md`,
  and this file's skeleton, and that ran the `uv init` / `uv add` commands.
- ChatGPT (OpenAI) — used as a second opinion on project scoping (which topic to
  pursue and what to exclude from the class project).

## Where I used them

- Repository skeleton and documentation drafts (README, .gitignore, LICENSE).
- The first three commits in this repository ("Add initial project structure",
  "Configure UV environment", "Add project README and AI use disclosure") were
  made by the AI-drafted bootstrap script. I read the script before running it,
  ran it myself, reviewed the resulting files and commit history, and made the
  final commit and push by hand.
- Deciding the project topic and its boundaries.

## Where I deliberately did not

- Creating the GitHub repository and configuring my Git credentials.
- This disclosure file's substance, which I wrote and verified.
- Assignment 3's research question and hypothesis will be my own work.

## What the tool got wrong and I caught

<!-- REQUIRED. Replace this with one real thing. Examples of the kind of thing to
     look for while running the script tonight: a command flag that did not exist
     on your UV version, a file uv init created that the script did not expect,
     a .gitignore rule that hid something you needed, a README step that did not
     work on your OS. Be specific: what it said, what actually happened. -->

## Verification

I ran every command in the README on my own machine and confirmed
`uv --version`, `uv sync`, and the pandas/numpy import check succeed.
