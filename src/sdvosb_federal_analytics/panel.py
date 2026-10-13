"""Deterministic proposal-defined agency-year features; no model fitting."""
from decimal import Decimal

PANEL_FIELDS = (
    "agency_id", "observation_fy", "achievement_pct", "baseline_average_pct",
    "shortfall_pp", "baseline_year_count", "available_post_year_count",
    "agency_included", "observation_included", "is_fy2024", "is_fy2025",
    "shortfall_x_fy2024", "shortfall_x_fy2025",
)


def derive_panel(rows):
    """Keep every row; mark inclusion and preserve NULL for an incomplete baseline.

    Exposure is max(0, 5 - FY2021–2023 mean) in percentage points. An agency
    qualifies with all three baseline outcomes and at least one FY2024/25
    outcome. A missing outcome never becomes zero or an included observation.
    """
    field = "sdvosb_prime_achievement_pct"
    by_agency = {}
    for row in rows:
        by_agency.setdefault(row["agency_id"], {})[int(row["observation_fy"])] = row
    features = {}
    for agency, years in by_agency.items():
        baseline = [Decimal(years[y][field]) for y in (2021, 2022, 2023)
                    if y in years and years[y][field] != ""]
        n_post = sum(y in years and years[y][field] != "" for y in (2024, 2025))
        mean = sum(baseline) / 3 if len(baseline) == 3 else None
        shortfall = max(Decimal(0), Decimal(5) - mean) if mean is not None else None
        features[agency] = mean, shortfall, len(baseline), n_post
    panel = []
    for row in rows:
        agency, year = row["agency_id"], int(row["observation_fy"])
        mean, shortfall, n_base, n_post = features[agency]
        included = int(n_base == 3 and n_post > 0)
        panel.append(dict(zip(PANEL_FIELDS, (
            agency, year, float(row[field]) if row[field] != "" else None,
            float(mean) if mean is not None else None,
            float(shortfall) if shortfall is not None else None,
            n_base, n_post, included, int(included and row[field] != ""),
            int(year == 2024), int(year == 2025),
            float(shortfall * int(year == 2024)) if shortfall is not None else None,
            float(shortfall * int(year == 2025)) if shortfall is not None else None,
        ))))
    return panel
