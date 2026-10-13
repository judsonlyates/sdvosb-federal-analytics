"""Derived-feature, database-constraint, and failure-preservation checks."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from sdvosb_federal_analytics import etl as c
from sdvosb_federal_analytics.panel import derive_panel
from sdvosb_federal_analytics.verify_rerun import main as verify_twice

RAW = Path(__file__).resolve().parents[1] / "data/raw/20261011T183300Z"


class PanelTests(unittest.TestCase):
    def rows(self):
        return [{"agency_id": "A", "observation_fy": y, "sdvosb_prime_achievement_pct": value}
                for y, value in zip(range(2020, 2026), ["-1", "1", "2", "3", "4", ""])]

    def test_approved_exposure_and_missing_outcome(self):
        panel = derive_panel(self.rows())
        self.assertTrue(all(r["baseline_average_pct"] == 2 and r["shortfall_pp"] == 3 for r in panel))
        self.assertEqual(panel[4]["shortfall_x_fy2024"], 3)
        self.assertEqual(panel[4]["shortfall_x_fy2025"], 0)
        self.assertIsNone(panel[5]["achievement_pct"])
        self.assertEqual(panel[5]["agency_included"], 1)
        self.assertEqual(panel[5]["observation_included"], 0)
        self.assertEqual(panel[0]["achievement_pct"], -1)

    def test_incomplete_baseline_is_not_imputed(self):
        rows = self.rows(); rows[2]["sdvosb_prime_achievement_pct"] = ""
        panel = derive_panel(rows)
        self.assertTrue(all(r["baseline_average_pct"] is None and r["shortfall_pp"] is None for r in panel))
        self.assertTrue(all(r["agency_included"] == 0 for r in panel))

    def test_no_post_year_excludes_agency(self):
        rows = self.rows(); rows[4]["sdvosb_prime_achievement_pct"] = ""
        self.assertTrue(all(r["agency_included"] == 0 for r in derive_panel(rows)))

    def test_high_baseline_clips_shortfall_to_zero(self):
        rows = self.rows()
        for row in rows: row["sdvosb_prime_achievement_pct"] = "20"
        self.assertTrue(all(r["shortfall_pp"] == 0 for r in derive_panel(rows)))


class PipelineTests(unittest.TestCase):
    def run_pipeline(self, raw, out):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return c.main(["--offline", "--raw-dir", str(raw), "--output-dir", str(out)])

    def test_twice_is_stable_and_constraints_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(verify_twice(["--output-dir", str(out)]), 0)
            report = json.loads((out / "rerun_verification.json").read_text())
            self.assertTrue(report["identical_logical_records_and_counts"])
            with sqlite3.connect(out / "scorecards.sqlite") as con:
                con.execute("PRAGMA foreign_keys=ON")
                self.assertEqual(con.execute("SELECT COUNT(*) FROM panel_agency_year").fetchone()[0], 144)
                self.assertEqual(con.execute("SELECT SUM(observation_included) FROM panel_agency_year").fetchone()[0], 143)
                self.assertEqual(con.execute("SELECT COUNT(*) FROM (SELECT DISTINCT agency_id FROM panel_agency_year WHERE shortfall_pp>0)").fetchone()[0], 12)
                with self.assertRaises(sqlite3.IntegrityError):
                    con.execute("INSERT INTO agencies VALUES ('VA')")
                with self.assertRaises(sqlite3.IntegrityError):
                    con.execute("UPDATE scorecard_observations SET sdvosb_prime_goal_pct=-1 WHERE agency_id='VA'")
                with self.assertRaises(sqlite3.IntegrityError):
                    con.execute("UPDATE scorecard_observations SET source_id='not-a-source' WHERE agency_id='VA'")
                with self.assertRaises(sqlite3.IntegrityError):
                    con.execute("UPDATE panel_agency_year SET shortfall_pp=-1 WHERE agency_id='VA'")

    def test_bad_hash_preserves_previous_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp); out = tmp / "out"; raw = tmp / "raw"
            self.assertEqual(self.run_pipeline(RAW, out), 0)
            before = (out / "scorecards.sqlite").read_bytes()
            shutil.copytree(RAW, raw)
            (raw / "agency-scorecards-2025.json").write_text("[]")
            self.assertEqual(self.run_pipeline(raw, out), 1)
            self.assertEqual(before, (out / "scorecards.sqlite").read_bytes())
            report = json.loads((out / "validation_summary.json").read_text())
            self.assertEqual(report["status"], "failed")
            self.assertIsNone(report["rejected_record_count"])

    def test_missing_record_rejects_batch_and_preserves_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp); out = tmp / "out"; raw = tmp / "raw"
            self.assertEqual(self.run_pipeline(RAW, out), 0)
            before = (out / "scorecards.sqlite").read_bytes()
            shutil.copytree(RAW, raw)
            manifest = json.loads((raw / "manifest.json").read_text())
            doc = next(d for d in manifest["documents"] if d["kind"] == "scorecard_json" and d["scorecard_fy"] == 2025)
            path = raw / doc["filename"]
            records = json.loads(path.read_text())
            path.write_text(json.dumps([r for r in records if r["department_acronym"] != "USDA"]))
            doc["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            doc["bytes"] = path.stat().st_size
            (raw / "manifest.json").write_text(json.dumps(manifest))
            self.assertEqual(self.run_pipeline(raw, out), 2)
            self.assertEqual(before, (out / "scorecards.sqlite").read_bytes())
            report = json.loads((out / "validation_summary.json").read_text())
            self.assertEqual(report["rejected_record_count"], 1)
            self.assertFalse(report["database_replaced"])

    def test_missing_pdf_counts_fallback_row_as_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp); out = tmp / "out"; raw = tmp / "raw"
            self.assertEqual(self.run_pipeline(RAW, out), 0)
            before = (out / "scorecards.sqlite").read_bytes()
            shutil.copytree(RAW, raw)
            (raw / "fy2020-NSF.pdf").unlink()
            manifest = json.loads((raw / "manifest.json").read_text())
            manifest["documents"] = [d for d in manifest["documents"] if d["filename"] != "fy2020-NSF.pdf"]
            (raw / "manifest.json").write_text(json.dumps(manifest))
            self.assertEqual(self.run_pipeline(raw, out), 2)
            self.assertEqual(before, (out / "scorecards.sqlite").read_bytes())
            report = json.loads((out / "validation_summary.json").read_text())
            self.assertEqual(report["status"], "rejected_batch")
            self.assertEqual(report["rejected_record_count"], 1)
            self.assertTrue(any("23 of 24" in e["error"] for e in report["source_errors"]))

    def test_export_failure_after_load_is_reported_accurately(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"; out.mkdir()
            (out / "sba_scorecard_sdvosb.csv").mkdir()  # export path unwritable; database load still succeeds
            self.assertEqual(self.run_pipeline(RAW, out), 1)
            self.assertTrue((out / "scorecards.sqlite").exists())
            report = json.loads((out / "validation_summary.json").read_text())
            self.assertEqual(report["status"], "failed")
            self.assertTrue(report["database_replaced"])
            log = (out / "pipeline.log").read_text()
            self.assertIn("FAILED after the validated database was replaced", log)
            self.assertNotIn("previous valid database is not replaced", log)

    def test_snapshot_overwrite_rejected(self):
        with self.assertRaises(c.DataError):
            c.collect(RAW)
