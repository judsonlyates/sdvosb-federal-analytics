"""Reproduce A4 inputs and A5 from frozen, audited sources.

Usage from project root:
    python scripts/run_portfolio.py --through a5

Use the existing locked Python environment; do not refresh the lockfile for a rerun.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def command(*args:str)->None:
    """Run one fixed pipeline stage with the current Python interpreter."""
    line=[sys.executable,*args]
    print('>', ' '.join(line),flush=True)
    subprocess.run(line,cwd=ROOT,check=True)


def main():
    """Build the supported A5 package from the frozen A4 source snapshot."""
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--through',choices=('a5',),default='a5')
    a=p.parse_args()
    command('-m','sdvosb_federal_analytics.etl','--offline','--raw-dir','data/raw/20261011T183300Z')
    command('-m','sdvosb_federal_analytics.verify_rerun')
    command('-m','sdvosb_federal_analytics.supplement')
    command('-m','sdvosb_federal_analytics.eda')
    print('Successfully built through',a.through.upper())


if __name__=='__main__':
    main()
