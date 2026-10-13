#!/usr/bin/env python3
"""Collect the public SBA scorecard data with immutable source snapshots.

Python 3.11+, pandas, SQLite, and Poppler pdftotext.
Run from the repository root; see README.md for online and offline commands.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
from html import unescape
from html.parser import HTMLParser
import json
import logging
import pandas as pd
from .panel import derive_panel, PANEL_FIELDS
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse, urljoin
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
PAGE_URL = "https://www.sba.gov/certifications/scorecard-details/"
YEARS = tuple(range(2020, 2026))
EDITIONS = tuple(range(2021, 2026))
ALIASES = {"DOW": "DOD", "Defense": "DOD", "Education": "ED", "STATE": "DOS", "Treasury": "TREAS"}
NUMERIC = ("sdvosb_prime_achievement_pct", "sdvosb_prime_goal_pct", "sdvosb_prime_dollars_millions")
FIELDS = ("agency_id", "agency_name_as_displayed", "observation_fy", "scorecard_fy", *NUMERIC,
          "source_url", "retrieved_date", "notes")
MISSING = {"", "n/a", "na", "not available", "null", "none", "--", "—"}


class DataError(ValueError):
    """Source shape or value is inconsistent with the documented contract."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(path: Path) -> list[dict]:
    """Read tabular input using pandas without converting blanks to NaN or zero."""
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig").to_dict("records")


def write_csv(path: Path, rows: list[dict], fields=None):
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="raise")
        w.writeheader()
        w.writerows(rows)


def write_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def raw_text(value) -> str:
    return "" if value is None else str(value).strip()


def parse_pct(value, *, goal=False) -> str:
    """Keep display precision and units: 2.30 means 2.30%, never 0.023.

    Signed achievement is valid because net deobligations can be negative.
    This deliberately differs from the original feasibility script's 0–100 rule.
    """
    s = raw_text(value)
    if s.lower() in MISSING:
        return ""
    s = s.removesuffix("%").strip()
    if not re.fullmatch(r"[+-]?\d+(?:\.\d+)?", s):
        raise DataError(f"Unrecognized percentage: {value!r}")
    n = Decimal(s)
    if goal and not Decimal(0) <= n <= Decimal(100):
        raise DataError(f"Goal outside 0–100: {value!r}")
    return s


def parse_dollars(value) -> tuple[str, str]:
    """Convert a displayed USD amount to millions and retain display rounding step."""
    s = raw_text(value)
    if s.lower() in MISSING:
        return "", ""
    s = re.sub(r"\s+", "", s).replace(",", "")
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    s = s.replace("$-", "-$")
    match = re.fullmatch(r"([+-]?)\$?(\d+(?:\.\d+)?)([KMB]?)", s, re.I)
    if not match:
        raise DataError(f"Unrecognized dollar amount: {value!r}")
    sign, digits, unit = match.groups()
    scale = {"": Decimal("0.000001"), "K": Decimal("0.001"), "M": Decimal(1), "B": Decimal(1000)}[unit.upper()]
    n = Decimal((sign or "") + digits) * scale
    quantum = Decimal(1).scaleb(Decimal(digits).as_tuple().exponent) * scale
    return format(n, "f"), format(quantum, "f")


class DiscoveryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.data_paths = []
        self.scripts = []
        self.mapping_fields = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if "sba-agency-scorecards-details" in attrs.get("class", "") and "data-data-path" in attrs:
            self.data_paths.append(attrs["data-data-path"].rstrip("/"))
        if tag == "script" and "scorecards-details.js" in attrs.get("src", ""):
            self.scripts.append(attrs["src"])
        self.mapping_fields.update(k[5:] for k in attrs if k.startswith("data-prime_"))


def check_public_url(url: str):
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"www.sba.gov", "sba.gov", "legacy.sba.gov"} or parsed.username or parsed.password:
        raise DataError(f"Unexpected source URL, review required: {url}")


def fetch(url: str, path: Path, kind: str, edition=None) -> dict:
    check_public_url(url)
    error = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": "SBA-scorecard-research-collector/1.0", "Accept": "application/json,text/html,*/*"}), timeout=45) as resp:
                final = resp.url
                check_public_url(final)
                data = resp.read(15_000_001)
                if len(data) > 15_000_000:
                    raise DataError(f"Source too large: {url}")
                timestamp = datetime.now(timezone.utc).isoformat()
                info = {"kind": kind, "scorecard_fy": edition, "url": url, "final_url": final,
                        "retrieved_at": timestamp, "filename": path.name, "sha256": sha256(data),
                        "bytes": len(data), "http_status": resp.status, "content_type": resp.headers.get("Content-Type"),
                        "etag": resp.headers.get("ETag"), "last_modified": resp.headers.get("Last-Modified")}
            path.write_bytes(data)
            return info
        except (HTTPError, URLError, TimeoutError) as e:
            error = e
            if isinstance(e, HTTPError) and 400 <= e.code < 500 and e.code != 429:
                break
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise DataError(f"Unable to retrieve {url}: {error}")


def collect(raw_dir: Path, include_pdfs=True) -> dict:
    if raw_dir.exists() and any(raw_dir.iterdir()):
        raise DataError("Snapshot directory is not empty. Use --offline or choose a new --raw-dir.")
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"format_version": 1, "created_at": datetime.now(timezone.utc).isoformat(), "documents": [], "errors": []}
    try:
        doc = fetch(PAGE_URL, raw_dir / "scorecard-details.html", "discovery_html")
        manifest["documents"].append(doc)
        parser = DiscoveryParser()
        parser.feed((raw_dir / doc["filename"]).read_text(encoding="utf-8"))
        if len(set(parser.data_paths)) != 1 or len(set(parser.scripts)) != 1:
            raise DataError("Unable to discover a unique public scorecard data path and loader script.")
        required = {"prime_sdvosb_cfy_achievement", "prime_sdvosb_cfy_goal", "prime_sdvosb_dollars", "prime_sdvosb_pfy_achievement"}
        if not required <= parser.mapping_fields:
            raise DataError("Scorecard HTML no longer maps expected SDVOSB fields.")
        jsdoc = fetch(parser.scripts[0], raw_dir / "scorecards-details.js", "discovery_javascript")
        manifest["documents"].append(jsdoc)
        script = (raw_dir / jsdoc["filename"]).read_text(encoding="utf-8")
        if "agency-scorecards-${encodeURIComponent(year)}.json" not in script or "element.textContent = value" not in script:
            raise DataError("Public JavaScript data naming or field hydration changed; review before collecting.")
        manifest["discovered_data_path"] = parser.data_paths[0]
        for year in EDITIONS:
            url = f"{parser.data_paths[0]}/agency-scorecards-{year}.json"
            try:
                doc = fetch(url, raw_dir / f"agency-scorecards-{year}.json", "scorecard_json", year)
                manifest["documents"].append(doc)
            except DataError as e:
                manifest["errors"].append({"scorecard_fy": year, "error": str(e)})
        if include_pdfs:
            for source in json.loads((ROOT / "data" / "reference" / "fy2020_sources.json").read_text()):
                try:
                    agency = source["agency_id"]
                    doc = fetch(source["source_page_url"], raw_dir / f"fy2020-{agency}-source.html", "legacy_discovery_html", 2020)
                    doc["agency_id"] = agency
                    manifest["documents"].append(doc)
                    html = (raw_dir / doc["filename"]).read_text(encoding="utf-8")
                    link_parser = DiscoveryParser()
                    link_parser.feed(html)
                    links = {urljoin(source["source_page_url"], href) for href in link_parser.links}
                    if source["source_url"] not in links:
                        raise DataError(f"FY2020 {agency}: configured PDF is no longer linked by the agency source page.")
                    doc = fetch(source["source_url"], raw_dir / f"fy2020-{agency}.pdf", "scorecard_pdf", 2020)
                    doc.update(agency_id=agency, source_page_url=source["source_page_url"])
                    manifest["documents"].append(doc)
                except DataError as e:
                    manifest["errors"].append({"scorecard_fy": 2020, "agency_id": source["agency_id"], "error": str(e)})
    finally:
        write_json(raw_dir / "manifest.json", manifest)
    return manifest


def verified_snapshot(raw_dir: Path) -> dict:
    manifest = json.loads((raw_dir / "manifest.json").read_text())
    for doc in manifest["documents"]:
        path = raw_dir / doc["filename"]
        if path.parent != raw_dir or path.is_symlink() or sha256(path.read_bytes()) != doc["sha256"]:
            raise DataError(f"Snapshot hash mismatch or unsafe filename: {doc['filename']}")
    return manifest


def source_records(raw_dir: Path, manifest: dict, agency_ids: set[str]):
    editions, documents = {}, {}
    for doc in manifest["documents"]:
        if doc["kind"] != "scorecard_json":
            continue
        year = int(doc["scorecard_fy"])
        data = json.loads((raw_dir / doc["filename"]).read_text(encoding="utf-8-sig"))
        if not isinstance(data, list):
            raise DataError(f"FY{year}: expected an array")
        records = {}
        for item in data:
            if not isinstance(item, dict):
                raise DataError(f"FY{year}: non-object agency record")
            code = item.get("department_acronym")
            if code == "GW":
                continue
            stable = ALIASES.get(code, code)
            if stable not in agency_ids:
                raise DataError(f"FY{year}: unexpected agency acronym {code!r}")
            if stable in records:
                raise DataError(f"FY{year}: duplicate stable agency {stable}")
            if item.get("fiscal_year") != year:
                raise DataError(f"FY{year}: fiscal_year mismatch for {stable}")
            for field in ("department_friendly_name", "prime_sdvosb_cfy_achievement", "prime_sdvosb_cfy_goal", "prime_sdvosb_dollars", "prime_sdvosb_pfy_achievement"):
                if field not in item:
                    raise DataError(f"FY{year} {stable}: source field missing: {field}")
            records[stable] = item
        editions[year] = records
        documents[year] = doc
        missing_agencies = sorted(agency_ids - set(records))
        if missing_agencies:
            manifest.setdefault("errors", []).append({"scorecard_fy": year, "error": f"Missing required agency records: {missing_agencies}"})
    for year in EDITIONS:
        if year not in editions:
            manifest.setdefault("errors", []).append({"scorecard_fy": year, "error": "Required annual JSON snapshot is absent."})
    return editions, documents


def plain_html(value) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]*>", " ", raw_text(value)))).strip()


def parse_2020_pdf_text(text: str, layout: str | None = None) -> dict:
    """Select the first SDVOSB row from the raw text and confirm it against the layout text.

    The raw pass takes the first SDVOSB row because the prime table precedes the
    subcontracting table on page 1. Raw text does not retain the table headings,
    so the layout pass is the authoritative prime/subcontracting boundary check:
    it must find the same values inside the "Prime Contracting Achievement:"
    section. Pass ``layout`` whenever it is available; omitting it is a reduced
    check used only by unit tests.
    """
    if "FY2020 Small Business Procurement Scorecard" not in text:
        raise DataError("PDF does not identify the FY2020 scorecard edition.")
    matches = list(re.finditer(r"Service Disabled Veteran Owned Small Business\s+([+-]?[\d.]+%)\s+([+-]?[\d.]+%)\s+([+-]?[\d.]+%)\s+\(([^)]+)\)", text))
    if not matches:
        raise DataError("No recognized FY2020 prime SDVOSB row in PDF text.")
    m = matches[0]
    footnote = re.search(r"(1\) Capped at 200%; 2\)[^\n]+)", text[m.end():])
    dollars, quantum = parse_dollars(m.group(4))
    if layout is not None:
        section = re.search(r"Prime Contracting Achievement:(.*?)Subcontracting Achievement:", layout, re.S)
        if section is None:
            raise DataError("PDF layout lacks explicit prime/subcontracting table boundaries.")
        lm = re.search(r"([+-]?[\d.]+%)\s*\nService Disabled Veteran Owned Small Business\s+([+-]?[\d.]+%)\s+([+-]?[\d.]+%)\s*\n\s*\(([^)]+)\)", section.group(1))
        if lm is None:
            raise DataError("No recognized SDVOSB row within the PDF prime table boundaries.")
        if (parse_pct(lm.group(1)), parse_pct(lm.group(3), goal=True), parse_dollars(lm.group(4))[0]) != (parse_pct(m.group(3)), parse_pct(m.group(2), goal=True), dollars):
            raise DataError("Raw and layout PDF extraction disagree; review required.")
    return {"agency_name_as_displayed": text.splitlines()[0].strip(),
            "achievement": parse_pct(m.group(3)), "goal": parse_pct(m.group(2), goal=True),
            "dollars": dollars, "quantum": quantum, "achievement_raw": m.group(3),
            "goal_raw": m.group(2), "dollars_raw": m.group(4), "raw_row": m.group(0),
            "prime_footnotes": footnote.group(1) if footnote else ""}


def apply_2020_pdfs(raw_dir, manifest, rows, provenance, flags):
    """Re-extract frozen PDFs on each run; no numerical values are hardcoded."""
    indices = {(r["agency_id"], r["observation_fy"]): i for i, r in enumerate(rows)}
    pindices = {(r["agency_id"], r["observation_fy"]): i for i, r in enumerate(provenance)}
    names = {r["agency_id"]: r["agency_name_as_displayed"] for r in json.loads((ROOT / "data" / "reference" / "fy2020_sources.json").read_text())}
    seen = set()
    for doc in manifest["documents"]:
        if doc["kind"] != "scorecard_pdf" or doc["scorecard_fy"] != 2020:
            continue
        agency = doc["agency_id"]
        if agency in seen or (agency, 2020) not in indices:
            raise DataError(f"Duplicate or unexpected FY2020 PDF agency: {agency}")
        seen.add(agency)
        try:
            text = subprocess.check_output(["pdftotext", "-f", "1", "-l", "1", "-raw", str(raw_dir / doc["filename"]), "-"], text=True, timeout=30)
            layout = subprocess.check_output(["pdftotext", "-f", "1", "-l", "1", "-layout", str(raw_dir / doc["filename"]), "-"], text=True, timeout=30)
        except (FileNotFoundError, subprocess.SubprocessError) as e:
            raise DataError(f"pdftotext (Poppler) is required to re-extract FY2020 PDF sources: {e}") from e
        parsed = parse_2020_pdf_text(text, layout)
        if parsed["agency_name_as_displayed"] != names[agency]:
            raise DataError(f"FY2020 PDF agency title changed for {agency}; review required.")
        row = rows[indices[agency, 2020]]
        prior = row[NUMERIC[0]]
        if prior and Decimal(prior) != Decimal(parsed["achievement"]):
            raise DataError(f"FY2020 PDF/FY2021 prior-column conflict for {agency}: {parsed['achievement']} vs {prior}")
        row.update(agency_name_as_displayed=parsed["agency_name_as_displayed"], scorecard_fy=2020,
                   sdvosb_prime_achievement_pct=parsed["achievement"], sdvosb_prime_goal_pct=parsed["goal"],
                   sdvosb_prime_dollars_millions=parsed["dollars"], source_url=doc["url"], retrieved_date=doc["retrieved_at"][:10])
        prior_note = ("achievement also matches FY2021 prior-year column." if prior
                      else "FY2021 prior-year column unavailable, so no cross-edition comparison was made.")
        rowflags = [("own_year_pdf", f"All three fields from the FY2020 PDF prime table, page 1; {prior_note}"),
                    ("rounded_display_dollars", f"Dollars converted from {parsed['dollars_raw']}; display quantum {parsed['quantum']} million USD.")]
        if Decimal(parsed["achievement"]) < 0:
            rowflags.append(("negative_achievement", "Negative source-reported achievement retained; see HUD deobligation caveat."))
        if Decimal(parsed["dollars"]) < 0:
            rowflags.append(("negative_dollars", "Negative net SDVOSB dollars retained from source."))
        if agency == "DOE":
            rowflags.append(("doe_mosrc_explicit", "FY2020 footnote explicitly includes DOE MOSRC dollars; exact comparability to later M&O wording requires review."))
        row["notes"] = " | ".join(detail for _, detail in rowflags)
        flags[:] = [f for f in flags if not (f["agency_id"] == agency and f["observation_fy"] == 2020)]
        flags.extend({"agency_id": agency, "observation_fy": 2020, "flag": code, "detail": detail} for code, detail in rowflags)
        p = {"agency_id": agency, "observation_fy": 2020, "scorecard_fy": 2020, "source_acronym": agency,
             "json_source_url": "", "snapshot_file": doc["filename"], "snapshot_sha256": doc["sha256"],
             "retrieved_at": doc["retrieved_at"], "achievement_field": "page 1 / prime table / SDVOSB / 2020 achievement",
             "achievement_as_displayed": parsed["achievement_raw"], "goal_as_displayed": parsed["goal_raw"],
             "dollars_as_displayed": parsed["dollars_raw"], "dollar_rounding_quantum_millions": parsed["quantum"],
             "source_prime_footnotes": parsed["prime_footnotes"], "footnotes_apply_to_edition": 2020,
             "agency_comments": "See the frozen PDF for agency comments.", "flags": ";".join(code for code, _ in rowflags)}
        if (agency, 2020) in pindices:
            provenance[pindices[agency, 2020]] = p
        else:
            provenance.append(p)
    return len(seen)


def build_panel(sample: list[dict], editions: dict, documents: dict):
    expected_keys = {(r["agency_id"], int(r["observation_fy"])) for r in sample}
    agency_ids = {a for a, _ in expected_keys}
    if len(sample) != 144 or len(expected_keys) != 144 or len(agency_ids) != 24 or expected_keys != {(a, y) for a in agency_ids for y in YEARS}:
        raise DataError("Original sample must provide a unique 24-agency × FY2020–2025 template.")
    rows, provenance, flags = [], [], []
    for template in sample:
        agency, year = template["agency_id"], int(template["observation_fy"])
        edition = 2021 if year == 2020 else year
        item = editions.get(edition, {}).get(agency)
        row = dict.fromkeys(FIELDS, "")
        row.update(agency_id=agency, agency_name_as_displayed=template["agency_name_as_displayed"], observation_fy=year)
        row_flags = []
        if item is None:
            row["notes"] = f"NOT_RETRIEVED: No usable FY{edition} source record. No values inferred."
            row_flags.append(("source_record_missing", row["notes"]))
        else:
            doc = documents[edition]
            achievement_field = "prime_sdvosb_pfy_achievement" if year == 2020 else "prime_sdvosb_cfy_achievement"
            achievement = parse_pct(item[achievement_field])
            goal = "" if year == 2020 else parse_pct(item["prime_sdvosb_cfy_goal"], goal=True)
            dollars, quantum = ("", "") if year == 2020 else parse_dollars(item["prime_sdvosb_dollars"])
            url = PAGE_URL + "?" + urlencode({"agency": item["department_acronym"], "scorecard_year": edition})
            row.update(agency_name_as_displayed=item["department_friendly_name"], scorecard_fy=edition,
                       sdvosb_prime_achievement_pct=achievement, sdvosb_prime_goal_pct=goal,
                       sdvosb_prime_dollars_millions=dollars, source_url=url, retrieved_date=doc["retrieved_at"][:10])
            if year == 2020:
                row_flags.append(("prior_year_only", "FY2020 achievement from FY2021 prior-year column; FY2020 goal/dollars not present in this source."))
            if not achievement:
                row_flags.append(("source_not_available", f"SBA displays {raw_text(item[achievement_field])!r}; missing is not zero."))
            if achievement and Decimal(achievement) < 0:
                row_flags.append(("negative_achievement", "Negative SBA achievement retained; HUD FY2021 comments explain net deobligations."))
            if dollars and Decimal(dollars) < 0:
                row_flags.append(("negative_dollars", "Negative net SDVOSB dollars retained from source."))
            if achievement and Decimal(achievement) > 100:
                row_flags.append(("achievement_above_100", "Reported achievement exceeds 100%; source retained for review."))
            if dollars:
                row_flags.append(("rounded_display_dollars", f"Dollars converted from {raw_text(item['prime_sdvosb_dollars'])}; display quantum {quantum} million USD; no additional precision inferred."))
            if agency == "DOD":
                row_flags.append(("retrospective_display_name", "Current website displays Department of War for historical editions; stable agency_id is DOD."))
            if agency == "DOE":
                if year in (2021, 2022, 2023):
                    row_flags.append(("doe_mo_explicit", "This edition expressly includes M&O first-tier subcontracting in prime contracting."))
                else:
                    row_flags.append(("doe_comparability_unresolved", "Exact annual M&O treatment needs review; omitted footnote wording does not establish exclusion."))
            if year >= 2022:
                row_flags.append(("deobligation_method_break", "SBA methodology changed beginning FY2022; assess comparability, especially HUD. See comparability report."))
            if year == 2025:
                row_flags.append(("certification_transition", "FY2025 certification transition is a concurrent measurement/policy caveat in the submitted proposal."))
            if agency == "VA" and year == 2023:
                row_flags.append(("va_alternative_measure_unreconciled", "27.16% is the SBA scorecard value; alternative 16.7% measure is not substituted."))
            row["notes"] = " | ".join(message for _, message in row_flags)
            provenance.append({"agency_id": agency, "observation_fy": year, "scorecard_fy": edition,
                               "source_acronym": item["department_acronym"], "json_source_url": doc["url"],
                               "snapshot_file": doc["filename"], "snapshot_sha256": doc["sha256"],
                               "retrieved_at": doc["retrieved_at"], "achievement_field": achievement_field,
                               "achievement_as_displayed": item[achievement_field],
                               "goal_as_displayed": "" if year == 2020 else item["prime_sdvosb_cfy_goal"],
                               "dollars_as_displayed": "" if year == 2020 else item["prime_sdvosb_dollars"],
                               "dollar_rounding_quantum_millions": quantum, "source_prime_footnotes": plain_html(item.get("prime_footnotes")),
                               "footnotes_apply_to_edition": edition, "agency_comments": plain_html(item.get("comments")),
                               "flags": ";".join(code for code, _ in row_flags)})
        rows.append(row)
        flags.extend({"agency_id": agency, "observation_fy": year, "flag": code, "detail": detail} for code, detail in row_flags)
    return rows, provenance, flags


def overlap_checks(rows, editions, documents):
    primary = {(r["agency_id"], int(r["observation_fy"])): r for r in rows}
    checks = []
    for edition, agencies in sorted(editions.items()):
        for agency, item in agencies.items():
            for lag in range(1, 5):
                year = edition - lag
                if (agency, year) not in primary:
                    continue
                field = "prime_sdvosb_pfy_achievement" if lag == 1 else f"prime_sdvosb_pfy{lag}_achievement"
                if field not in item:
                    continue
                row = primary[agency, year]
                if year == 2020 and edition == 2021 and row["scorecard_fy"] == 2021:
                    continue  # This is the selected primary source, not an independent overlap.
                other = parse_pct(item[field])
                current = row[NUMERIC[0]]
                status = "missing" if not other or not current else ("match" if Decimal(other) == Decimal(current) else "conflict")
                checks.append({"agency_id": agency, "observation_fy": year, "primary_scorecard_fy": row["scorecard_fy"],
                               "primary_achievement_pct": current, "comparison_scorecard_fy": edition,
                               "comparison_field": field, "comparison_achievement_pct": other, "status": status,
                               "adjacent_edition": int(lag == 1), "source_url": documents[edition]["url"]})
    return checks


def reconcile(sample, rows):
    current = {(r["agency_id"], int(r["observation_fy"])): r for r in rows}
    records = []
    for old in sample:
        for field in NUMERIC:
            if not old[field]:
                continue
            new = current[old["agency_id"], int(old["observation_fy"])][field]
            status = "missing_new_value" if not new else "match" if Decimal(old[field]) == Decimal(new) else "conflict"
            records.append({"agency_id": old["agency_id"], "observation_fy": old["observation_fy"], "field": field,
                            "original_sample_value": old[field], "collected_value": new, "status": status,
                            "display_text_identical": str(old[field] == new).lower()})
    return records


def database(path: Path, rows, provenance, flags, manifest, checks, comparisons):
    tmp = path.with_suffix(".tmp.sqlite")
    if tmp.exists():
        tmp.unlink()
    con = sqlite3.connect(tmp)
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))
    con.executemany("INSERT INTO agencies VALUES (?)", [(a,) for a in sorted({r["agency_id"] for r in rows})])
    for d in manifest["documents"]:
        con.execute("INSERT INTO source_documents VALUES (?,?,?,?,?,?,?,?)",
                    (d["sha256"], d["kind"], d["scorecard_fy"], d["url"], d["retrieved_at"], d["filename"], d["sha256"], d["bytes"]))
    names = {(r["agency_id"], r["scorecard_fy"]): r["agency_name_as_displayed"]
             for r in rows if r["scorecard_fy"] != ""}
    con.executemany("INSERT INTO agency_names VALUES (?,?,?)", [(a, y, name) for (a,y), name in names.items()])
    source_by_key = {(r["agency_id"], r["observation_fy"]): r["snapshot_sha256"] for r in provenance}
    for row in rows:
        values = (row["agency_id"], row["observation_fy"], row["scorecard_fy"] or None,
                  *(float(row[f]) if row[f] != "" else None for f in NUMERIC),
                  source_by_key.get((row["agency_id"], row["observation_fy"])), row["notes"])
        con.execute("INSERT INTO scorecard_observations VALUES (?,?,?,?,?,?,?,?)", values)
    con.executemany("INSERT INTO provenance VALUES (?,?,?)",
                    [(r["agency_id"], r["observation_fy"], json.dumps(r)) for r in provenance])
    con.executemany("INSERT INTO quality_flags VALUES (?,?,?,?)",
                    [(r["agency_id"], r["observation_fy"], r["flag"], r["detail"]) for r in flags])
    sources_by_url = {d["url"]: d["sha256"] for d in manifest["documents"]}
    for r in checks:
        con.execute("INSERT INTO overlap_checks VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (r["agency_id"], r["observation_fy"], r["primary_scorecard_fy"] or None,
                     float(r["primary_achievement_pct"]) if r["primary_achievement_pct"] != "" else None,
                     r["comparison_scorecard_fy"], r["comparison_field"],
                     float(r["comparison_achievement_pct"]) if r["comparison_achievement_pct"] != "" else None,
                     r["status"], r["adjacent_edition"], sources_by_url[r["source_url"]]))
    con.executemany("INSERT INTO sample_reconciliation VALUES (?,?,?,?,?,?,?)",
                    [(r["agency_id"], int(r["observation_fy"]), r["field"], r["original_sample_value"],
                      r["collected_value"] or None, r["status"], int(r["display_text_identical"] == "true")) for r in comparisons])
    panel = derive_panel(rows)
    con.executemany(
        "INSERT INTO panel_agency_year VALUES (" + ",".join("?" for _ in PANEL_FIELDS) + ")",
        [tuple(r[field] for field in PANEL_FIELDS) for r in panel],
    )
    con.commit()
    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or con.execute("PRAGMA foreign_key_check").fetchall():
        raise DataError("SQLite integrity verification failed")
    con.close()
    tmp.replace(path)


def summary(rows, checks, comparisons, manifest):
    frame = pd.DataFrame(rows)
    duplicates = int(frame.duplicated(["agency_id", "observation_fy"]).sum())
    missing = [{"agency_id": r["agency_id"], "observation_fy": r["observation_fy"], "fields": [f for f in NUMERIC if r[f] == ""]} for r in rows if any(r[f] == "" for f in NUMERIC)]
    complete_base = []
    for agency in dict.fromkeys(r["agency_id"] for r in rows):
        base = [r for r in rows if r["agency_id"] == agency and r["observation_fy"] in (2021,2022,2023)]
        if len(base) == 3 and all(r[NUMERIC[0]] != "" for r in base):
            avg = sum(Decimal(r[NUMERIC[0]]) for r in base)/3
            posts = [r["observation_fy"] for r in rows if r["agency_id"] == agency and r["observation_fy"] in (2024,2025) and r[NUMERIC[0]] != ""]
            complete_base.append({"agency_id": agency, "baseline_average_pct": float(avg), "shortfall_pp": float(max(Decimal(0),Decimal(5)-avg)), "available_post_years": posts})
    return {"status": "validated", "input_template_rows": len(rows), "rows": len(rows),
            "duplicate_record_count": duplicates, "rejected_record_count": 0,
            "missing_cells_by_field": {f: int((frame[f] == "").sum()) for f in NUMERIC},
            "bad_record_action": "Fail the batch on malformed, duplicate, missing-source or conflicting records; keep previous database. Source-declared N/A is retained as NULL and flagged; negatives are retained and flagged.", "agencies": len(set(r["agency_id"] for r in rows)),
            "achievement_count": sum(r[NUMERIC[0]] != "" for r in rows), "goal_count": sum(r[NUMERIC[1]] != "" for r in rows),
            "dollars_count": sum(r[NUMERIC[2]] != "" for r in rows), "complete_three_field_rows": sum(all(r[f] != "" for f in NUMERIC) for r in rows),
            "counts_by_year": {y: {f: sum(r["observation_fy"]==y and r[f]!="" for r in rows) for f in NUMERIC} for y in YEARS},
            "missing": missing, "source_errors": manifest.get("errors", []),
            "overlap_checks": len(checks), "overlap_conflicts": sum(r["status"]=="conflict" for r in checks),
            "adjacent_edition_checks": sum(r["adjacent_edition"] for r in checks),
            "sample_values_compared": len(comparisons), "sample_conflicts": sum(r["status"]!="match" for r in comparisons),
            "agencies_with_complete_baseline": len(complete_base), "baseline_shortfall_positive": sum(r["shortfall_pp"]>0 for r in complete_base),
            "baseline_exposure": complete_base, "negative_achievement_rows": [{"agency_id": r["agency_id"], "observation_fy": r["observation_fy"], "achievement_pct":r[NUMERIC[0]]} for r in rows if r[NUMERIC[0]] and Decimal(r[NUMERIC[0]])<0]}


def run_pipeline(args):
    """Extract, validate, transform, then atomically replace a complete database.

    Any data conflict or missing required source writes diagnostic reports but
    does not replace the last valid database or canonical CSV exports.
    """
    logger = logging.getLogger(__name__)
    raw = args.raw_dir.resolve()
    if not args.offline:
        logger.info("EXTRACT: retrieving official SBA source documents")
        collect(raw, include_pdfs=not args.json_only)
    manifest = verified_snapshot(raw)
    logger.info("EXTRACT: verified %d frozen source documents", len(manifest["documents"]))
    sample = read_csv(args.sample)
    editions, docs = source_records(raw, manifest, {r["agency_id"] for r in sample})
    rows, provenance, flags = build_panel(sample, editions, docs)
    pdf_fallback_rejects = False
    if not args.json_only:
        pdf_count = apply_2020_pdfs(raw, manifest, rows, provenance, flags)
        if pdf_count != 24:
            pdf_fallback_rejects = True
            manifest.setdefault("errors", []).append({"scorecard_fy": 2020, "error": f"Only {pdf_count} of 24 own-year PDFs available; prior-year-only fallback rows remain explicit."})
    logger.info("TRANSFORM: %d agency-year rows; %d provenance records", len(rows), len(provenance))
    checks = overlap_checks(rows, editions, docs)
    comparisons = reconcile(sample, rows)
    report = summary(rows, checks, comparisons, manifest)
    report["source_document_count"] = len(manifest["documents"])
    report["quality_flag_count"] = len(flags)
    report["analysis_ready_observations"] = sum(r["observation_included"] for r in derive_panel(rows))
    report["pipeline_mode"] = "json_only_reduced" if args.json_only else "full"
    failed = bool(report["overlap_conflicts"] or report["sample_conflicts"] or report["source_errors"] or report["duplicate_record_count"])
    if failed:
        rejected = {(r["agency_id"], int(r["observation_fy"])) for r in checks if r["status"] == "conflict"}
        rejected.update((r["agency_id"], int(r["observation_fy"])) for r in comparisons if r["status"] != "match")
        rejected.update((r["agency_id"], int(r["observation_fy"])) for r in flags if r["flag"] == "source_record_missing")
        if pdf_fallback_rejects:  # In full mode a prior-year-only FY2020 row is an incomplete record, not an accepted fallback.
            rejected.update((r["agency_id"], int(r["observation_fy"])) for r in flags if r["flag"] == "prior_year_only")
        report.update(status="rejected_batch", rejected_record_count=len(rejected),
                      rejected_record_count_note="Count of identified offending agency-years; source-document errors are separately listed and also reject the entire batch.",
                      batch_rows_not_published=len(rows), database_replaced=False)
        write_json(args.output_dir / "validation_summary.json", report)
        logger.error("VALIDATE: batch rejected; %d identified offending records; prior database retained", len(rejected))
        return 2
    logger.info("VALIDATE: 0 duplicates, 0 rejected records; %d source-declared missing rows retained", len(report["missing"]))
    out = args.output_dir
    # Build/check the database first; a failing database transaction cannot replace it.
    database(out / "scorecards.sqlite", rows, provenance, flags, manifest, checks, comparisons)
    args.database_replaced = True  # Read by main() so a later export failure is reported accurately.
    write_csv(out / "sba_scorecard_sdvosb.csv", rows, FIELDS)
    write_csv(out / "panel_agency_year.csv", derive_panel(rows), PANEL_FIELDS)
    write_csv(out / "row_provenance.csv", provenance)
    write_csv(out / "quality_flags.csv", flags)
    write_csv(out / "cross_year_checks.csv", checks)
    write_csv(out / "sample_reconciliation.csv", comparisons)
    report.update(status="success", database_replaced=True)
    write_json(out / "validation_summary.json", report)
    logger.info("LOAD: database replaced after integrity/foreign-key checks; %d facts, %d analysis-ready observations", len(rows), report["analysis_ready_observations"])
    print(json.dumps({k:v for k,v in report.items() if k not in ("baseline_exposure", "missing")}, indent=2))
    print(f"Outputs written to {out}")
    return 0


def main(argv=None):
    """Command-line entry point with a persisted log and nonzero failure status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="Rebuild from a hash-verified frozen snapshot without network.")
    parser.add_argument("--raw-dir", type=Path, default=ROOT / "data" / "raw" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "processed")
    parser.add_argument("--sample", type=Path, default=ROOT / "data" / "sample" / "sba_scorecard_sdvosb.csv")
    parser.add_argument("--json-only", action="store_true", help="Reduced mode: FY2020 goals/dollars remain missing; this is not the complete A4 build.")
    args = parser.parse_args(argv)
    args.database_replaced = False
    args.output_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(args.output_dir / "pipeline.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    try:
        logger.info("START: offline=%s raw_dir=%s", args.offline, args.raw_dir)
        return run_pipeline(args)
    except (DataError, OSError, ValueError, KeyError, TypeError, sqlite3.Error, pd.errors.ParserError) as exc:
        if args.database_replaced:
            logger.exception("FAILED after the validated database was replaced: exports are incomplete; rerun the same command to regenerate them")
            action = "Database already replaced with a validated build; exports incomplete. Rerun the same command to regenerate exports."
        else:
            logger.exception("FAILED: previous valid database is not replaced on validation failure")
            action = "Abort with nonzero status; inspect pipeline.log; no invalid facts are published."
        write_json(args.output_dir / "validation_summary.json", {
            "status": "failed", "error": str(exc), "rejected_record_count": None,
            "database_replaced": args.database_replaced,
            "rejected_record_count_note": ("The batch validated with zero rejected records; the failure was in writing exports."
                                           if args.database_replaced else
                                           "Failure occurred before a reliable record-level count could be established; the entire batch was aborted."),
            "bad_record_action": action,
        })
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        logger.removeHandler(handler)
        handler.close()


if __name__ == "__main__":
    raise SystemExit(main())
