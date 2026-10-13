# Assignment 4 pipeline architecture

## Scope and sources

The approved proposal identifies SBA scorecards as the pilot's input. FY2021–FY2025 use the public annual JSON files that populate SBA's interactive pages; FY2020 uses the 24 official scorecard PDFs. Saved discovery HTML and JavaScript establish the JSON naming/field mapping and legacy PDF links. USAspending was assessed and explicitly excluded in the approved proposal, so no transaction-data pipeline is claimed.

`data/reference/fy2020_sources.json` contains the verified legacy source pages, PDF URLs, stable IDs, and expected agency titles. The original sample supplies the fixed 24-agency/fiscal-year frame. It is retained unchanged for reconciliation, not used to fill missing source values.

## Extraction

`etl.collect()` discovers the SBA data location, downloads the public data, and records URL, retrieval timestamp, byte size, and SHA-256 for each source. Downloads enforce HTTPS/SBA hostnames, timeout, bounded retry, and a size limit. A refresh requires an empty snapshot directory and never changes the review fixture. JavaScript is read as text, not executed.

`verified_snapshot()` verifies hashes before parsing. `source_records()` validates the annual JSON structures and stable agency IDs. `apply_2020_pdfs()` calls Poppler twice. The raw text supplies the first SDVOSB row; the layout text, which retains the table headings, must locate the same values inside the prime-contracting section, so the layout pass is the authoritative prime/subcontracting boundary check. It verifies the edition, agency title, and agreement with FY2021's prior-year achievement. Ambiguity fails instead of choosing a guessed value.

## Transformation

Pandas reads the CSV sample with explicit string types and missing-token behavior. Custom functions parse displayed percentages and dollar units using Decimal. `2.42` means 2.42%, and `$1.1 B` becomes 1100 million, with the original display string and rounding quantum preserved. No additional source precision is invented.

Aliases map DOW/Defense to DOD, Education to ED, STATE to DOS, and Treasury to TREAS. Government-wide records are excluded by an explicit population rule. Current displayed names remain edition-specific; they are not assumed to represent historical agency names perfectly.

`panel.derive_panel()` implements the proposal's unchanged features. Baseline average uses exactly FY2021–FY2023. Exposure is max(0, 5 − baseline average), in percentage points. Inclusion requires all three baseline values and at least one observed FY2024/FY2025 outcome. All 144 rows remain present; missing outcomes have `observation_included=0`. No regression is fitted.

## Validation and bad-record actions

Custom checks are documented and covered by tests:

- The template must have exactly 24 agencies × six years, with unique keys.
- Required JSON fields, recognized IDs and editions must match their contracts.
- Invalid numeric tokens, invalid goals, hash mismatches and ambiguous PDFs abort.
- Percentage achievements and net dollars may be signed; real HUD negatives are retained with flags.
- Source-declared N/A becomes blank CSV / SQL NULL and is explicitly flagged.
- Missing annual files or agency records reject the batch; they are distinct from official N/A.
- All 48 populated sample cells are compared; conflicts reject the batch.
- Historical/current source overlaps are compared; conflicts reject the batch.
- Pandas calculates duplicate counts and missing cells by field. SQLite enforces PKs, FKs and CHECK constraints.

`validation_summary.json` includes row counts by year/field, duplicates, rejected-record counts, missingness, source errors, reconciliation results, and actions. Success has zero rejected records. For a source/reconciliation failure it reports the identified offending agency-years plus separate source errors and rejects the whole batch. In full mode, a FY2020 row left on its prior-year-only fallback because its own-year PDF is missing is counted as an offending agency-year, not an accepted fallback. If parsing stops before a reliable record count is available, the count is explicitly null with an explanation, not a fabricated zero. `pipeline.log` records stages and failures.

## Load, atomic replacement and repeatability

`database()` creates a fresh temporary SQLite file, creates the reviewed schema, uses parameterized inserts, enables foreign keys, builds the derived panel, commits, and checks SQLite integrity/foreign keys. Only a valid temporary database replaces the target file. This is a full deterministic snapshot replacement rather than append/upsert, appropriate for a 144-row frozen research panel.

Validation occurs before this load. A rejected batch does not replace the previous database or canonical CSV exports; diagnostic reports and logs are still updated. A filesystem failure after the database has been successfully replaced can leave exports incomplete. That case exits 1, writes `validation_summary.json` with `status: failed` and `database_replaced: true`, and logs that the validated database was replaced but exports are incomplete; rerun the same frozen command to regenerate them. The SQLite database itself is replaced atomically. Concurrent writers to the same output directory are not supported.

`verify_rerun.py` runs the pipeline twice against one path and compares all logical table contents/counts and CSV hashes. It also checks zero duplicate observation keys and database integrity. The log is intentionally not hash-compared because timestamps differ. See `docs/validation/rerun_verification.json` for actual execution evidence.

## Commands and return codes

See the root README for setup and the one end-to-end command. Exit 0 means the requested mode passed; exit 2 means a fully inspected batch was rejected for explicit source/conflict reasons; exit 1 means extraction, parsing, filesystem or database failure. `--json-only` is labeled reduced mode and cannot substitute for the full A4 evidence.

Online refreshes can change source content and need source review. Offline builds use no network. All original frozen sources and sample numerical values are preserved. No EDA, model, dashboard, deployment or course submission occurs within the pipeline.
