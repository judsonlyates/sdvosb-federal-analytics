"""A3 feasibility check on hand-collected SBA scorecard data.

Enter percentages as plain numbers: 4.25 means 4.25%. A trailing % sign is accepted.
Blank cells are treated as not yet collected.

Usage: uv run python scripts/feasibility_check.py data/sample/sba_scorecard_sdvosb.csv
"""
import sys
import pandas as pd

PRE_BASE = [2021, 2022, 2023]
POST = [2024, 2025]
NEW_GOAL = 5.0
PCT_COLS = ["sdvosb_prime_achievement_pct", "sdvosb_prime_goal_pct"]


def parse_pct(series: pd.Series, name: str) -> pd.Series:
    raw = series.astype("string").str.strip().str.rstrip("%").str.strip()
    raw = raw.mask(raw == "")
    out = pd.to_numeric(raw, errors="coerce")
    bad = raw.notna() & out.isna()
    if bad.any():
        sys.exit(f"ERROR: non-numeric values in {name}: {sorted(series[bad].unique())}")
    if ((out < 0) | (out > 100)).any():
        sys.exit(f"ERROR: {name} has values outside 0-100")
    return out


df = pd.read_csv(sys.argv[1], dtype=str, keep_default_na=False, na_values=[""])
for c in PCT_COLS:
    df[c] = parse_pct(df[c], c)
df["observation_fy"] = pd.to_numeric(df["observation_fy"], errors="raise").astype(int)

filled = df[df[PCT_COLS].notna().any(axis=1)]
dupes = filled.duplicated(["agency_id", "observation_fy"], keep=False)
if dupes.any():
    sys.exit(f"ERROR: duplicate agency-year rows:\n{filled.loc[dupes, ['agency_id', 'observation_fy', 'scorecard_fy']]}")

frac = filled["sdvosb_prime_goal_pct"].dropna()
if len(frac) and (frac < 1).all():
    print("WARNING: every goal value is below 1 - were percentages entered as fractions (0.05 instead of 5)?")

print("== Observations collected, by fiscal year ==")
print(df.groupby("observation_fy")["sdvosb_prime_achievement_pct"].count().to_string())

print("\n== Goal values by fiscal year (post years should show 5.0 if goals moved to the statutory level) ==")
print(df.dropna(subset=["sdvosb_prime_goal_pct"]).groupby("observation_fy")["sdvosb_prime_goal_pct"]
      .value_counts().to_string())

base = df[df["observation_fy"].isin(PRE_BASE)].dropna(subset=["sdvosb_prime_achievement_pct"])
n_years = base.groupby("agency_id")["observation_fy"].nunique()
complete = n_years[n_years == len(PRE_BASE)].index
avg = base[base["agency_id"].isin(complete)].groupby("agency_id")["sdvosb_prime_achievement_pct"].mean()
shortfall = (NEW_GOAL - avg).clip(lower=0).rename("shortfall_pp")

print(f"\n== Agencies with all FY2021-FY2023 achievement values: {len(complete)} of {df['agency_id'].nunique()} ==")
if len(complete):
    print(f"Below 5% (shortfall > 0): {(shortfall > 0).sum()}   At or above 5%: {(shortfall == 0).sum()}")
    if (shortfall > 0).any():
        print("\nShortfall among agencies below 5% (percentage points):")
        print(shortfall[shortfall > 0].describe().round(2).to_string())
    print("\nPer agency:")
    print(pd.concat([avg.rename("avg_fy21_23"), shortfall], axis=1)
          .sort_values("shortfall_pp", ascending=False).round(2).to_string())
    if len(complete) < df["agency_id"].nunique():
        print("\nNOTE: partial collection. These counts describe the collected agencies only, not the full panel.")
