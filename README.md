# SDVOSB Federal Market Analytics

BUS 751 – Python for Business Analytics (Fall 2026, University of South Alabama)
Author: Judson L. Yates

## Project description

This repository is the semester-long portfolio project for BUS 751. It builds an
end-to-end analytics pipeline over U.S. federal contract award data
(USAspending / FPDS-NG) to describe the federal market for Service-Disabled
Veteran-Owned Small Businesses (SDVOSBs): obligations, distinct awards, awarding
agencies, industries (NAICS), and trends over a bounded set of fiscal years.

Planned components, one per assignment:

| Assignment | Component |
|---|---|
| A3 | Problem definition and data source plan (frozen, documented CSV extract) |
| A4 | SQLite schema and ETL script (import, validate, clean, store) |
| A5 | Exploratory data analysis module (summaries and visualizations) |
| A6 | One analytics/modeling module appropriate to the data |
| A7 | Streamlit dashboard and Docker deployment |

The scope is deliberately descriptive. It is not an official measure of agency
goal compliance under the SBA scorecard.

## Repository structure

```
src/sdvosb_federal_analytics/   Python package: ETL, analysis, and dashboard code
tests/                  Unit tests
docs/                   Documentation, including AI_USE.md
data/raw/               Source extracts (git-ignored)
data/processed/         Cleaned outputs and SQLite database (git-ignored)
notebooks/              Exploratory Jupyter notebooks
pyproject.toml          Project metadata and dependencies (managed by UV)
```

## Setup instructions

Prerequisites: Git and [UV](https://docs.astral.sh/uv/). UV installs and manages
Python for you; you do not need a separate Python or Anaconda install.

1. Install UV (once):
   - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows (PowerShell): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   Confirm with `uv --version`.
2. Clone the repository:
   ```
   git clone https://github.com/judsonlyates/sdvosb-federal-analytics.git
   cd sdvosb-federal-analytics
   ```
3. Create the environment and install all dependencies from the lockfile:
   ```
   uv sync
   ```
4. Verify:
   ```
   uv run python -c "import pandas, numpy; print(pandas.__version__, numpy.__version__)"
   ```
5. Launch Jupyter:
   ```
   uv run jupyter lab
   ```
   In VS Code, select the interpreter at `.venv` when prompted.

## UV commands used in this project

| Command | Purpose |
|---|---|
| `uv init --python 3.11` | Initialize the project and pin Python 3.11 |
| `uv add <package>` | Add a dependency (updates `pyproject.toml` and `uv.lock`) |
| `uv remove <package>` | Remove a dependency |
| `uv sync` | Create `.venv` and install exactly what the lockfile specifies |
| `uv run <command>` | Run a command inside the project environment |
| `uv python list` | Show installed and available Python versions |

## AI use

See `docs/AI_USE.md`.
