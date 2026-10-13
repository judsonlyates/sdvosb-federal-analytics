# Data dictionary

## Scope, sources, and conventions

This dictionary matches all nine tables in
[`schema.sql`](../src/sdvosb_federal_analytics/schema.sql), the transformations in
[`etl.py`](../src/sdvosb_federal_analytics/etl.py), and the derived fields in
[`panel.py`](../src/sdvosb_federal_analytics/panel.py). See [ERD.md](ERD.md) for
relationships, normalization decisions, and indexes.

The observational unit is an agency/fiscal-year pair. The required population
is the 24 agency identifiers in the preserved sample crossed with FY2020–FY2025.
The extraction retains all 144 pairs, including rows with missing source values.
The source is SBA scorecard prime-contracting information, not transaction-level
procurement data or subcontracting achievement.

### Source identifiers used below

- **Sample:** `data/sample/sba_scorecard_sdvosb.csv`, the preserved original
  agency-year template and previously populated verification values.
- **Annual JSON:** frozen FY2021–FY2025 SBA annual scorecard data discovered
  through the [SBA scorecard page](https://www.sba.gov/certifications/scorecard-details/).
  The saved page and loader JavaScript establish its field/display mapping.
- **FY2020 PDF:** the first-page prime-contracting SDVOSB row in each official
  legacy SBA PDF. `data/reference/fy2020_sources.json` maps agencies to their
  source pages/PDFs. Both raw and layout-preserving PDF text are checked.
- **Manifest:** `manifest.json` in the selected raw snapshot directory,
  containing downloaded-file identity and retrieval metadata. Files are
  hash-verified before use.
- **ETL-derived:** a deterministic selection, transformation, validation, or
  feature calculation using those inputs.

### Storage and missing-value conventions

`TEXT`, `INTEGER`, and `REAL` are the SQLite declared types/affinities. The
tables are not declared `STRICT`; ETL parsing provides additional type and
source-shape validation. `REAL` is floating-point storage, not an exact-decimal
or display-format type. Source strings remain available for precision review.

In the tables below, **Required** means the SQL column is `NOT NULL`.
**Nullable** means SQL permits `NULL`; a stronger ETL rule is stated separately
where applicable. `NOT NULL` does not itself prohibit an empty text string.
There are no column defaults. `PK` and `FK` identify components of keys; exact
composite keys are listed before each table.

- Percentages use displayed percentage units, so `2.30%` becomes numerical
  `2.30`, not `0.023`. Percentage-point differences use those same numerical
  units. Achievement is signed; it is not restricted to 0–100. The goal is
  restricted to 0–100 when present.
- Dollar amounts are signed millions of USD. `$10.4 B` becomes `10400` million
  USD, with a source display step of `100` million USD. `$303.0 M` becomes
  `303.0`, with a `0.1` million USD step. These steps describe source rounding,
  not additional measured precision or a statistical error bound.
- Recognized missing tokens are empty text, `N/A`, `NA`, `not available`,
  `null`, `none`, `--`, and an em dash, case-insensitive after trimming. A
  missing numerical CSV cell loads as SQL `NULL`. Numeric zero remains zero.
- Boolean fields are integer `0`/`1`, with explicit SQL checks. The sample
  reconciliation CSV uses `false`/`true` for its display-equality field; the
  database converts those strings to `0`/`1`.
- `observation_fy` is the fiscal year measured. `scorecard_fy` is the source
  edition, which can differ when a prior-year achievement field is selected.
  Retrieval dates/times describe the captured file, not the award date or
  guaranteed original publication date.

## 1. `agencies`

**Grain:** one stable agency identity. **PK:** `agency_id`.

| Column | Type / nullability | Definition, source, and rule |
|---|---|---|
| `agency_id` | TEXT, required; PK | Stable project code from the sample. Incoming source aliases are mapped to it: `DOW` and `Defense` → `DOD`, `Education` → `ED`, `STATE` → `DOS`, and `Treasury` → `TREAS`. Other recognized codes are retained. Government-wide `GW` is excluded. Unknown or duplicate source agencies fail validation. |

The sample's 24 stable identifiers are USAID, USDA, DOC, DOD, ED, DOE, HHS,
DHS, HUD, DOI, DOJ, DOL, DOS, DOT, TREAS, VA, EPA, GSA, NASA, NSF, NRC, OPM,
SBA, and SSA. Identity does not depend on a current displayed agency name.

## 2. `source_documents`

**Grain:** one downloaded file in the selected snapshot. **PK:** `source_id`.
**Additional unique key:** `filename`.

| Column | Type / nullability | Definition, source, and rule |
|---|---|---|
| `source_id` | TEXT, required; PK | SHA-256 content digest from the manifest, used as the document identity. It is not a URL. SQL requires equality to `sha256`; ETL verifies the digest against saved bytes. |
| `kind` | TEXT, required | Manifest file role. Collector values are `discovery_html`, `discovery_javascript`, `scorecard_json`, `legacy_discovery_html`, and `scorecard_pdf`. SQL does not impose an enumeration. |
| `scorecard_fy` | INTEGER, nullable | Manifest source edition. SQL checks 2020–2025 when non-NULL. General discovery HTML/JavaScript have no edition and use `NULL`; the legacy source pages/PDFs use 2020 and annual JSON uses its edition. |
| `url` | TEXT, required | Requested official source URL from the manifest, rather than the constructed agency-specific display URL. Collector requests must use HTTPS and an allowed SBA hostname. SQL does not validate the URL syntax or require URL uniqueness. |
| `retrieved_at` | TEXT, required | Retrieval time at its recorded precision. The seven interactive-source files have UTC ISO 8601 timestamps; the 48 legacy page/PDF records have date-only `2026-10-11` with `retrieval_time_precision="day"` in the frozen manifest. No exact time is invented. SQL does not parse/validate the format. |
| `filename` | TEXT, required; UNIQUE | Basename of the saved raw file, unique within this database/snapshot. ETL verifies the corresponding local snapshot file and its checksum before extraction. |
| `sha256` | TEXT, required | Named manifest checksum, deliberately repeating the content identity for audit readability. SQL checks length 64 and equality to `source_id`; hexadecimal content correctness is established by ETL hashing, not the length check alone. |
| `bytes` | INTEGER, required | Downloaded file length in bytes from the manifest. SQL requires a nonnegative value. Zero is structurally permitted; source parsing still requires usable content. |

`final_url`, HTTP status, content type, ETag, last-modified header, and legacy
source-page/agency metadata, when present, remain in the raw manifest. They are
not additional columns in this table. Record-specific interpretive notes belong
in `quality_flags` and `provenance`, not in shared document metadata.

## 3. `agency_names`

**Grain:** one agency/source-edition label in this collection.
**PK:** `(agency_id, scorecard_fy)`.
**FK:** `agency_id` → `agencies(agency_id)`.

| Column | Type / nullability | Definition, source, and rule |
|---|---|---|
| `agency_id` | TEXT, required; PK/FK | Stable project identity for the name, with the same alias rules as `agencies`. |
| `scorecard_fy` | INTEGER, required; PK | Selected scorecard edition associated with this displayed label. SQL checks 2020–2025. This is not a legal-name effective year. |
| `display_name` | TEXT, required | Annual JSON `department_friendly_name`, or the verified FY2020 PDF title. Saved as displayed at retrieval, including retrospective renaming in historical editions. Not replaced with an assumed historically contemporaneous name. |

Labels are deduplicated from sourced observations. The observation's composite
name FK ensures its label belongs to both the correct agency and the selected
edition. The schema does not add a separate source-document FK to this table;
the corresponding observation and provenance identify the selected snapshot.

## 4. `scorecard_observations`

**Grain:** one agency/observation fiscal year.
**PK:** `(agency_id, observation_fy)`.
**FKs:** `agency_id` → `agencies(agency_id)`;
`(agency_id, scorecard_fy)` → `agency_names(agency_id, scorecard_fy)`;
`source_id` → `source_documents(source_id)`.

| Column | Type / nullability | Definition, source, and rule |
|---|---|---|
| `agency_id` | TEXT, required; PK/FK | Agency whose performance is measured; stable sample identity. Also participates in the composite edition-name FK. |
| `observation_fy` | INTEGER, required; PK | Fiscal year measured. SQL checks 2020–2025. ETL requires each of the six years for each of the 24 agencies, even if measurements are missing. |
| `scorecard_fy` | INTEGER, nullable; composite FK | Edition selected for the observation. Own-year JSON uses 2021–2025; an own-year FY2020 PDF uses 2020; a FY2021 prior-year fallback uses 2021 for an observation year of 2020. No independent SQL range check exists here, but a non-NULL value must match the checked `agency_names` key. NULL is retained only for failed-source diagnostics, not for a sourced N/A outcome. |
| `sdvosb_prime_achievement_pct` | REAL, nullable | SBA-reported prime SDVOSB achievement in percent units. Annual JSON `prime_sdvosb_cfy_achievement`; FY2020 PDF current achievement; or FY2021 `prime_sdvosb_pfy_achievement` as a flagged FY2020 fallback. Signed source values are retained; negatives and values above 100 are flagged rather than clipped. Missing remains NULL. |
| `sdvosb_prime_goal_pct` | REAL, nullable | Displayed prime SDVOSB goal in percent units, from JSON `prime_sdvosb_cfy_goal` or the FY2020 PDF goal column. SQL/ETL require 0–100 when present. A historical achievement column does not supply its year's goal. No goal is imputed from the policy benchmark. |
| `sdvosb_prime_dollars_millions` | REAL, nullable | Displayed prime SDVOSB dollars converted to millions of USD, from JSON `prime_sdvosb_dollars` or the FY2020 PDF amount. B × 1,000; M × 1; K × 0.001; unmarked dollars × 0.000001. Signed values and parentheses indicating negatives are supported. Source rounding is preserved in evidence. |
| `source_id` | TEXT, nullable; FK | Digest identifying the selected primary raw JSON or PDF document. Copied from the observation's extraction provenance, never from the display URL. NULL is permitted for a failed-source diagnostic; a sourced N/A record still references its document. |
| `notes` | TEXT, required | Human-readable record-specific quality messages joined with ` | ` by ETL. An empty string is allowed when there is no message. Structured versions live in `quality_flags`; this column supports the flat-file export. |

The successful USAID FY2025 record keeps its valid name/edition and source
reference, while all three numerical fields are NULL because the source
displays N/A. No reason for that missingness is inferred. A missing source
record is a distinct condition, marked `source_record_missing`, and is not
treated as a successful collection.

## 5. `provenance`

**Grain:** one extraction evidence payload per sourced observation.
**PK and FK:** `(agency_id, observation_fy)` →
`scorecard_observations(agency_id, observation_fy)`.

| Column | Type / nullability | Definition, source, and rule |
|---|---|---|
| `agency_id` | TEXT, required; PK/FK | Agency identifying the evidence's parent observation. |
| `observation_fy` | INTEGER, required; PK/FK | Observation fiscal year identifying the evidence's parent observation. |
| `details_json` | TEXT, required | JSON serialization of the row-level extraction record described below. SQL requires `json_valid(details_json)`. This validates JSON syntax, not the payload's field schema or agreement with its relational key; ETL generates those contents. |

### JSON payload fields and `row_provenance.csv`

These are payload keys, not separate SQL columns. They also define the columns
of the row-provenance CSV. Display strings and metadata are intentionally
retained together as an audit snapshot, including data also available by join.

| Payload key | Representation and meaning |
|---|---|
| `agency_id` | Stable agency code, repeating the parent key for a standalone evidence record. |
| `observation_fy` | Integer year measured, repeating the parent key. |
| `scorecard_fy` | Integer selected source edition. |
| `source_acronym` | Original JSON `department_acronym` before alias normalization; for FY2020 PDF extraction, the configured stable agency code. |
| `json_source_url` | Raw annual JSON URL from the manifest. Empty string for PDF-derived observations; the PDF URL is obtained through `source_id` and `source_documents.url`. |
| `snapshot_file` | Saved raw document basename. |
| `snapshot_sha256` | Document's SHA-256 digest; supplies `scorecard_observations.source_id`. |
| `retrieved_at` | Source document retrieval timestamp or date-only value, preserving the recorded precision. See `source_documents.retrieved_at`. |
| `achievement_field` | JSON field name used, or the PDF locator `page 1 / prime table / SDVOSB / 2020 achievement`. Distinguishes a current-year field from a prior-year fallback. |
| `achievement_as_displayed` | Original JSON value or extracted PDF percentage token, retaining source display precision and missing markers. Numerical NULL in the database can therefore be traced to its display. |
| `goal_as_displayed` | Original JSON goal or extracted PDF goal token. Empty for a FY2020 prior-year-only fallback because that source provides no FY2020 goal. |
| `dollars_as_displayed` | Original JSON dollar value or extracted PDF amount, retaining currency/unit/sign formatting. Empty for a FY2020 prior-year-only fallback. |
| `dollar_rounding_quantum_millions` | Decimal string giving one last-displayed-digit step after conversion to millions of USD; empty if there is no dollar value. No extra precision is inferred. |
| `source_prime_footnotes` | JSON prime footnotes with HTML removed and whitespace normalized, or the parsed FY2020 prime-table footnote text. The original bytes remain in the frozen source. |
| `footnotes_apply_to_edition` | Integer edition to which the retained footnotes apply; do not silently treat later-edition footnotes as the original rules for a prior-year observation. |
| `agency_comments` | Plain-text JSON agency comments after HTML/whitespace cleanup. PDF extraction records `See the frozen PDF for agency comments.` rather than claiming to have extracted the full comments. |
| `flags` | Semicolon-separated quality flag codes present when this extraction record was produced. Structured codes/details are in `quality_flags`. |

An absent source record has no extracted provenance row. A source record with
N/A values does have provenance. JSON contents are not hand-edited separately
from canonical observations or used as a competing numerical data source.

## 6. `quality_flags`

**Grain:** one flag code applied to one observation.
**PK:** `(agency_id, observation_fy, flag)`.
**FK:** `(agency_id, observation_fy)` → `scorecard_observations`.

| Column | Type / nullability | Definition, source, and rule |
|---|---|---|
| `agency_id` | TEXT, required; PK/FK | Agency carrying the flag. |
| `observation_fy` | INTEGER, required; PK/FK | Observation year carrying the flag. |
| `flag` | TEXT, required; PK | Machine-readable ETL quality/source-selection code. SQL does not constrain an enumeration; the current codes are listed below. The key prohibits duplicate codes on the same observation. |
| `detail` | TEXT, required | Record-specific explanation, including displayed values, rounding steps, source-selection limitations, or comparability notes as applicable. |

| Current flag | Meaning and handling |
|---|---|
| `source_record_missing` | Required agency/source record was not retrieved or usable; no values are inferred. This is a collection failure diagnostic. |
| `prior_year_only` | FY2020 achievement is obtained from FY2021 history; FY2020 goal and dollars stay missing until supported by an own-year PDF. |
| `own_year_pdf` | FY2020 fields were independently extracted from its own-year PDF prime table; the detail text states whether the achievement was reconciled to the FY2021 prior-year column (always, in the frozen build) or that column was unavailable. |
| `source_not_available` | Source explicitly supplies a missing achievement marker. Preserve the row and NULL outcome. |
| `negative_achievement` | Signed source achievement is retained; it is not converted to missing or zero. |
| `negative_dollars` | Signed source dollars are retained. |
| `achievement_above_100` | Source-reported achievement above 100 is retained for review rather than capped. |
| `rounded_display_dollars` | Dollar conversion and the source display step are recorded; accounting precision is not implied. |
| `retrospective_display_name` | The current historical JSON label differs from the stable agency identity. Preserve both identity and source label. |
| `doe_mosrc_explicit` | The FY2020 DOE PDF expressly references MOSRC; preserve the source-definition caveat. |
| `doe_mo_explicit` | The relevant DOE edition expressly references M&O first-tier subcontracting in prime achievement. |
| `doe_comparability_unresolved` | Annual DOE comparability needs review; omitted wording does not establish exclusion. |
| `deobligation_method_break` | FY2022 onward carries the documented SBA methodology-change caution. |
| `certification_transition` | FY2025 carries the proposal's certification-transition caution. |
| `va_alternative_measure_unreconciled` | A separately reported VA measure has not been reconciled; it does not replace the SBA scorecard value. |

Flags document handling and source qualifications. They are not model findings
or automatic deletion rules. Detailed source-specific discussion is retained
with the record evidence and in [DATA_QUALITY.md](DATA_QUALITY.md).

## 7. `overlap_checks`

**Grain:** one primary observation compared with one later scorecard edition
and historical field.
**PK:** `(agency_id, observation_fy, comparison_scorecard_fy, comparison_field)`.
**FKs:** `(agency_id, observation_fy)` → `scorecard_observations`;
`source_id` → `source_documents(source_id)`.

| Column | Type / nullability | Definition, source, and rule |
|---|---|---|
| `agency_id` | TEXT, required; PK/FK | Agency whose achievement is compared. |
| `observation_fy` | INTEGER, required; PK/FK | Year measured by both sides of the comparison. |
| `primary_scorecard_fy` | INTEGER, nullable | Edition selected for the canonical observation, copied into the audit record. NULL if no primary source was available. No independent SQL range check. |
| `primary_achievement_pct` | REAL, nullable | Canonical achievement used in this comparison, in percentage units. NULL when missing. Intentionally repeated to retain both comparison inputs. |
| `comparison_scorecard_fy` | INTEGER, required; PK | Later annual JSON edition supplying the historical value. ETL selects available FY2021–FY2025 editions; SQL does not separately constrain its range. |
| `comparison_field` | TEXT, required; PK | Historical JSON field: `prime_sdvosb_pfy_achievement`, `prime_sdvosb_pfy2_achievement`, `prime_sdvosb_pfy3_achievement`, or `prime_sdvosb_pfy4_achievement`, for lags one through four where present. |
| `comparison_achievement_pct` | REAL, nullable | Later edition's achievement for the same observation year, parsed in displayed percentage units. NULL when that comparison field is missing-valued. |
| `status` | TEXT, required | SQL enum: `match`, `missing`, or `conflict`. ETL uses `missing` if either side is missing; otherwise it compares Decimal numerical values before REAL storage. |
| `adjacent_edition` | INTEGER, required | SQL 0/1 flag. One when the comparison edition is exactly one year after the observation year; otherwise zero. |
| `source_id` | TEXT, required; FK | Digest of the later annual JSON used for the comparison. It may differ from the observation's primary source digest. |

Only historical fields whose observation year exists in the panel are checked.
If FY2020 itself uses the FY2021 prior-year field as its primary source, that
same field is not counted as independent overlap evidence. When a FY2020 PDF
is the primary source, its comparison with FY2021 history is independent and
is retained. Audit conflicts are surfaced; the later value never silently
overwrites the selected canonical observation.

## 8. `sample_reconciliation`

**Grain:** one originally nonblank sample measurement compared with the new
collection. **PK:** `(agency_id, observation_fy, field)`.
**FK:** `(agency_id, observation_fy)` → `scorecard_observations`.

| Column | Type / nullability | Definition, source, and rule |
|---|---|---|
| `agency_id` | TEXT, required; PK/FK | Agency from the original sample row. |
| `observation_fy` | INTEGER, required; PK/FK | Observation year from the original sample row. |
| `field` | TEXT, required; PK | One of `sdvosb_prime_achievement_pct`, `sdvosb_prime_goal_pct`, or `sdvosb_prime_dollars_millions`, selected by ETL. SQL does not impose this enumeration. |
| `original_sample_value` | TEXT, required | Original nonblank sample string, retained without converting its display precision to REAL. Its unit is determined by `field`. Blank original cells generate no comparison row. |
| `collected_value` | TEXT, nullable | Newly collected normalized numeric string, in the same field units. NULL if the new extraction lacks a value. Text is retained so formatting can be compared as well as magnitude. |
| `status` | TEXT, required | SQL enum: `match`, `conflict`, or `missing_new_value`. ETL compares Decimal numeric values; different formatting alone does not imply a conflict. |
| `display_text_identical` | INTEGER, required | SQL 0/1 flag for exact string equality between original and collected values before loading. For example, equal numerical values with different trailing zeros can be a `match` with this flag equal to zero. |

These comparisons provide evidence against the preserved sample. They do not
modify the sample or replace current source facts with old values.

## 9. `panel_agency_year`

**Grain:** one deterministic preparation row for every canonical observation.
**PK and FK:** `(agency_id, observation_fy)` →
`scorecard_observations(agency_id, observation_fy)`.
**Source:** `derive_panel` in `panel.py`; rebuilt in full on every ETL run.

| Column | Type / nullability | Definition and calculation |
|---|---|---|
| `agency_id` | TEXT, required; PK/FK | Stable identity copied from the canonical observation. |
| `observation_fy` | INTEGER, required; PK/FK | Observation year copied from the canonical observation. All FY2020–FY2025 keys remain present. |
| `achievement_pct` | REAL, nullable | Copy of `sdvosb_prime_achievement_pct`, in percent units; NULL remains NULL. |
| `baseline_average_pct` | REAL, nullable | Agency's arithmetic mean of FY2021, FY2022, and FY2023 achievements, calculated with Decimal before floating-point output. Defined only if all three are present; otherwise NULL. Repeated across that agency's rows. |
| `shortfall_pp` | REAL, nullable | `max(0, 5 - baseline_average_pct)` in percentage points. NULL if the three-year baseline is incomplete. SQL checks nonnegative when present. The fixed 5% comparison benchmark is not an imputed observed goal. |
| `baseline_year_count` | INTEGER, required | Number of nonmissing achievement values in FY2021–FY2023. SQL checks 0–3. Neither missing values nor source goals enter the count. |
| `available_post_year_count` | INTEGER, required | Number of nonmissing achievement values in FY2024–FY2025. SQL checks 0–2. Availability does not require both years. |
| `agency_included` | INTEGER, required | SQL 0/1. One exactly when `baseline_year_count = 3` and `available_post_year_count >= 1`; otherwise zero. Applies to the agency across all its rows. |
| `observation_included` | INTEGER, required | SQL 0/1. One exactly when the agency qualifies and this observation's achievement is nonmissing. No additional year restriction is applied in this field. |
| `is_fy2024` | INTEGER, required | SQL 0/1. One for observation FY2024, otherwise zero, independently of missingness or inclusion. |
| `is_fy2025` | INTEGER, required | SQL 0/1. One for observation FY2025, otherwise zero, independently of missingness or inclusion. |
| `shortfall_x_fy2024` | REAL, nullable | `shortfall_pp * is_fy2024`, in percentage points. NULL if shortfall is undefined; otherwise zero outside FY2024. |
| `shortfall_x_fy2025` | REAL, nullable | `shortfall_pp * is_fy2025`, in percentage points. NULL if shortfall is undefined; otherwise zero outside FY2025. |

An incomplete baseline never becomes a partial-year average or a zero
shortfall. An agency needs at least one available post-period achievement, not
both, so a missing post year does not discard its other observations. USAID
FY2025 remains in the table with `achievement_pct = NULL` and
`observation_included = 0`; its valid FY2024 outcome can still satisfy the
agency-level post-period requirement. Inclusion is recorded rather than
implemented by deleting rows. These are preparation features, not estimates or
interpretations of policy effects.

The panel deliberately repeats canonical outcomes and agency-level features.
It is a materialized projection rather than an independent normalized source of
truth. It must not be manually edited; correct inputs or transformations and
rebuild it.

## Flat-file outputs and relational mapping

| Output | Fields and mapping |
|---|---|
| `sba_scorecard_sdvosb.csv` | Ordered columns: `agency_id`, `agency_name_as_displayed`, `observation_fy`, `scorecard_fy`, `sdvosb_prime_achievement_pct`, `sdvosb_prime_goal_pct`, `sdvosb_prime_dollars_millions`, `source_url`, `retrieved_date`, `notes`. The observation fields map directly to `scorecard_observations`; the display name maps to `agency_names.display_name`. |
| `panel_agency_year.csv` | The 13 `panel_agency_year` columns in dictionary order. Nullable values are empty CSV cells. |
| `row_provenance.csv` | The 17 payload fields listed under `provenance`, in that order. The database stores each record as `details_json` alongside its relational key. |
| `quality_flags.csv` | The four `quality_flags` columns in dictionary order. |
| `cross_year_checks.csv` | The ten `overlap_checks` fields in dictionary order, except the last column is `source_url` for the comparison document. Database loading resolves that document URL to its manifest SHA-256 `source_id`. |
| `sample_reconciliation.csv` | The seven `sample_reconciliation` fields in dictionary order. `display_text_identical` is `true`/`false` here and becomes integer 1/0 in SQLite. |
| `validation_summary.json` | Build-level diagnostic summary, not an additional relational table. Includes coverage/missingness, source errors, validation comparison counts, and feature-preparation checks. |
| `scorecards.sqlite` | The nine-table relational database documented above. |

The three extra display/export fields in the main CSV are defined as follows:

| Export field | Definition and source |
|---|---|
| `agency_name_as_displayed` | Selected source-edition name, mapped to `agency_names.display_name`. On a failed-source diagnostic row only, the template label is retained in the CSV and no sourced name/edition is asserted. |
| `source_url` | Agency-specific SBA scorecard page URL for annual JSON observations, constructed using the source acronym and edition, or the direct PDF URL for FY2020 PDF observations. This navigational display URL is not necessarily `source_documents.url` and is never the source primary key. |
| `retrieved_date` | Retrieval date in `YYYY-MM-DD` form, obtained from the first ten characters of the source's timestamp or date-only value. Metadata retains whatever time precision the source manifest records. Empty for a failed-source diagnostic. |

The CSVs are reviewable exports of the same build. Source snapshots, manifest
digests, keys, and validation evidence establish traceability; a manually edited
export is not accepted as a replacement for a reproducible ETL run.
