-- Canonical normalized facts plus explicitly documented audit/derived relations.
PRAGMA foreign_keys = ON;
CREATE TABLE agencies (
    agency_id TEXT PRIMARY KEY NOT NULL
);
CREATE TABLE source_documents (
    source_id TEXT PRIMARY KEY NOT NULL,
    kind TEXT NOT NULL,
    scorecard_fy INTEGER CHECK(scorecard_fy BETWEEN 2020 AND 2025),
    url TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    filename TEXT NOT NULL UNIQUE,
    sha256 TEXT NOT NULL CHECK(length(sha256) = 64),
    bytes INTEGER NOT NULL CHECK(bytes >= 0),
    CHECK(source_id = sha256)
);
CREATE TABLE agency_names (
    agency_id TEXT NOT NULL REFERENCES agencies(agency_id),
    scorecard_fy INTEGER NOT NULL CHECK(scorecard_fy BETWEEN 2020 AND 2025),
    display_name TEXT NOT NULL,
    PRIMARY KEY(agency_id, scorecard_fy)
);
CREATE TABLE scorecard_observations (
    agency_id TEXT NOT NULL,
    observation_fy INTEGER NOT NULL CHECK(observation_fy BETWEEN 2020 AND 2025),
    scorecard_fy INTEGER,
    sdvosb_prime_achievement_pct REAL,
    sdvosb_prime_goal_pct REAL CHECK(sdvosb_prime_goal_pct BETWEEN 0 AND 100),
    sdvosb_prime_dollars_millions REAL,
    source_id TEXT REFERENCES source_documents(source_id),
    notes TEXT NOT NULL,
    PRIMARY KEY(agency_id, observation_fy),
    FOREIGN KEY(agency_id) REFERENCES agencies(agency_id),
    FOREIGN KEY(agency_id, scorecard_fy) REFERENCES agency_names(agency_id, scorecard_fy)
);
CREATE TABLE provenance (
    agency_id TEXT NOT NULL,
    observation_fy INTEGER NOT NULL,
    details_json TEXT NOT NULL CHECK(json_valid(details_json)),
    PRIMARY KEY(agency_id, observation_fy),
    FOREIGN KEY(agency_id, observation_fy) REFERENCES scorecard_observations(agency_id, observation_fy)
);
CREATE TABLE quality_flags (
    agency_id TEXT NOT NULL,
    observation_fy INTEGER NOT NULL,
    flag TEXT NOT NULL,
    detail TEXT NOT NULL,
    PRIMARY KEY(agency_id, observation_fy, flag),
    FOREIGN KEY(agency_id, observation_fy) REFERENCES scorecard_observations(agency_id, observation_fy)
);
CREATE TABLE overlap_checks (
    agency_id TEXT NOT NULL,
    observation_fy INTEGER NOT NULL,
    primary_scorecard_fy INTEGER,
    primary_achievement_pct REAL,
    comparison_scorecard_fy INTEGER NOT NULL,
    comparison_field TEXT NOT NULL,
    comparison_achievement_pct REAL,
    status TEXT NOT NULL CHECK(status IN ('match', 'missing', 'conflict')),
    adjacent_edition INTEGER NOT NULL CHECK(adjacent_edition IN (0,1)),
    source_id TEXT NOT NULL REFERENCES source_documents(source_id),
    PRIMARY KEY(agency_id, observation_fy, comparison_scorecard_fy, comparison_field),
    FOREIGN KEY(agency_id, observation_fy) REFERENCES scorecard_observations(agency_id, observation_fy)
);
CREATE TABLE sample_reconciliation (
    agency_id TEXT NOT NULL,
    observation_fy INTEGER NOT NULL,
    field TEXT NOT NULL,
    original_sample_value TEXT NOT NULL,
    collected_value TEXT,
    status TEXT NOT NULL CHECK(status IN ('match', 'conflict', 'missing_new_value')),
    display_text_identical INTEGER NOT NULL CHECK(display_text_identical IN (0,1)),
    PRIMARY KEY(agency_id, observation_fy, field),
    FOREIGN KEY(agency_id, observation_fy) REFERENCES scorecard_observations(agency_id, observation_fy)
);
-- Materialized analysis-ready projection; always rebuilt from canonical facts.
CREATE TABLE panel_agency_year (
    agency_id TEXT NOT NULL,
    observation_fy INTEGER NOT NULL,
    achievement_pct REAL,
    baseline_average_pct REAL,
    shortfall_pp REAL CHECK(shortfall_pp >= 0),
    baseline_year_count INTEGER NOT NULL CHECK(baseline_year_count BETWEEN 0 AND 3),
    available_post_year_count INTEGER NOT NULL CHECK(available_post_year_count BETWEEN 0 AND 2),
    agency_included INTEGER NOT NULL CHECK(agency_included IN (0,1)),
    observation_included INTEGER NOT NULL CHECK(observation_included IN (0,1)),
    is_fy2024 INTEGER NOT NULL CHECK(is_fy2024 IN (0,1)),
    is_fy2025 INTEGER NOT NULL CHECK(is_fy2025 IN (0,1)),
    shortfall_x_fy2024 REAL,
    shortfall_x_fy2025 REAL,
    PRIMARY KEY(agency_id, observation_fy),
    FOREIGN KEY(agency_id, observation_fy) REFERENCES scorecard_observations(agency_id, observation_fy)
);
-- Composite primary keys already index agency-first access and prevent duplicates.
CREATE INDEX idx_observations_fy ON scorecard_observations(observation_fy);
CREATE INDEX idx_observations_source ON scorecard_observations(source_id);
CREATE INDEX idx_flags_flag ON quality_flags(flag);
CREATE INDEX idx_overlaps_source ON overlap_checks(source_id);
CREATE INDEX idx_panel_fy_included ON panel_agency_year(observation_fy, observation_included);
