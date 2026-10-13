"""Offline parser, provenance, reconciliation, and database regression tests."""
import csv
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
from sdvosb_federal_analytics import etl as c
RAW = ROOT/'data/raw/20261011T183300Z'

class ParsingTests(unittest.TestCase):
    def test_percentage_units_and_display_precision(self):
        self.assertEqual(c.parse_pct('2.30%'), '2.30')
        self.assertEqual(c.parse_pct('5.00%', goal=True), '5.00')
    def test_negative_achievement_valid(self):
        self.assertEqual(c.parse_pct('-5.04%'), '-5.04')
    def test_negative_goal_invalid(self):
        with self.assertRaises(c.DataError): c.parse_pct('-1%', goal=True)
    def test_invalid_percentages_fail(self):
        for v in ['NaN','inf','2.3oops','2,30%','25%%']:
            with self.subTest(v=v), self.assertRaises(c.DataError): c.parse_pct(v)
    def test_missing_is_not_zero(self):
        for v in [None,'N/A','',' — ']: self.assertEqual(c.parse_pct(v),'')
        self.assertEqual(c.parse_pct('0.00%'),'0.00')
    def test_billions_conversion(self):
        value, quantum = c.parse_dollars(' $10.4 B ')
        self.assertEqual(Decimal(value), Decimal(10400))
        self.assertEqual(Decimal(quantum), Decimal(100))
    def test_millions_precision(self):
        self.assertEqual(c.parse_dollars('$303.0 M'), ('303.0','0.1'))
    def test_negative_dollar_formats(self):
        self.assertEqual(c.parse_dollars('-$15.4 M')[0], '-15.4')
        self.assertEqual(c.parse_dollars('$-50.6 M')[0], '-50.6')
        self.assertEqual(c.parse_dollars('($50.6 M)')[0], '-50.6')
    def test_dollar_zero_distinct_from_missing(self):
        self.assertEqual(c.parse_dollars('N/A'), ('',''))
        self.assertEqual(c.parse_dollars('$0 M')[0], '0')
    def test_k_and_dollar_units(self):
        self.assertEqual(c.parse_dollars('$250 K')[0], '0.250')
        self.assertEqual(c.parse_dollars('$1,000,000')[0], '1.000000')
    def test_unknown_dollar_unit_fails(self):
        with self.assertRaises(c.DataError): c.parse_dollars('$10 Z')
    def test_source_url_restriction(self):
        c.check_public_url('https://legacy.sba.gov/sites/default/file.pdf')
        for u in ['http://www.sba.gov/','https://example.com/','https://www.sba.gov.evil.example/']:
            with self.assertRaises(c.DataError): c.check_public_url(u)
    def test_pdf_parse_uses_current_not_prior(self):
        text='Department of Test\nFY2020 Small Business Procurement Scorecard\nPrime Contracting\nService Disabled Veteran Owned Small Business 4.02% 3.00%\n-5.04%\n($-50.6 M)\n1) Capped at 200%; 2) footnote'
        r=c.parse_2020_pdf_text(text)
        self.assertEqual(r['achievement'],'-5.04')
        self.assertEqual(r['goal'],'3.00')
        self.assertEqual(r['dollars'],'-50.6')
    def test_relative_legacy_source_links(self):
        parser=c.DiscoveryParser()
        parser.feed('<a href="/sites/default/files/2021-07/USAID-508.pdf">2020</a>')
        urls={c.urljoin('https://legacy.sba.gov/document/test',href) for href in parser.links}
        self.assertIn('https://legacy.sba.gov/sites/default/files/2021-07/USAID-508.pdf',urls)
    def test_pdf_prime_boundaries_required(self):
        raw='Department of Test\nFY2020 Small Business Procurement Scorecard\nPrime Contracting\nService Disabled Veteran Owned Small Business 4.02% 3.00%\n-5.04%\n($-50.6 M)'
        with self.assertRaises(c.DataError): c.parse_2020_pdf_text(raw,'Subcontracting Achievement: only')
    def test_subcontract_only_row_rejected(self):
        raw='Department of Test\nFY2020 Small Business Procurement Scorecard\nPrime Contracting\nService Disabled Veteran Owned Small Business 4.02% 3.00%\n1.04%\n($50.6 M)'
        layout='Prime Contracting Achievement:\nUnrecognized prime table\nSubcontracting Achievement:\n1.04%\nService Disabled Veteran Owned Small Business 4.02% 3.00%\n($50.6 M)'
        with self.assertRaises(c.DataError): c.parse_2020_pdf_text(raw,layout)
    def test_wrong_pdf_edition_fails(self):
        with self.assertRaises(c.DataError): c.parse_2020_pdf_text('FY2021')

class FrozenSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest=c.verified_snapshot(RAW)
        cls.sample=c.read_csv(ROOT/'data/sample/sba_scorecard_sdvosb.csv')
        cls.ids={r['agency_id'] for r in cls.sample}
        cls.editions,cls.docs=c.source_records(RAW,cls.manifest,cls.ids)
        cls.rows,cls.provenance,cls.flags=c.build_panel(cls.sample,cls.editions,cls.docs)
        c.apply_2020_pdfs(RAW,cls.manifest,cls.rows,cls.provenance,cls.flags)
        cls.checks=c.overlap_checks(cls.rows,cls.editions,cls.docs)
        cls.comparisons=c.reconcile(cls.sample,cls.rows)
    def test_144_unique_rows_24_agencies(self):
        self.assertEqual(len(self.rows),144)
        self.assertEqual(len({(r['agency_id'],r['observation_fy']) for r in self.rows}),144)
        self.assertEqual(len({r['agency_id'] for r in self.rows}),24)
    def test_143_complete_rows_one_explicit_na(self):
        for f in c.NUMERIC: self.assertEqual(sum(r[f]!='' for r in self.rows),143)
        missing=[r for r in self.rows if not r[c.NUMERIC[0]]]
        self.assertEqual([(r['agency_id'],r['observation_fy']) for r in missing],[('USAID',2025)])
        self.assertIn('N/A',missing[0]['notes'])
    def test_2020_own_year_pdf_coverage(self):
        rows=[r for r in self.rows if r['observation_fy']==2020]
        self.assertEqual(len(rows),24)
        self.assertTrue(all(r['scorecard_fy']==2020 and r['source_url'].endswith('.pdf') for r in rows))
    def test_sample_exact_numerical_reconciliation(self):
        self.assertEqual(len(self.comparisons),48)
        self.assertTrue(all(r['status']=='match' for r in self.comparisons))
    def test_historical_overlap_checks(self):
        self.assertEqual(len(self.checks),336)
        self.assertEqual(sum(r['adjacent_edition'] for r in self.checks),120)
        self.assertTrue(all(r['status']=='match' for r in self.checks))
    def test_hud_negatives_retained(self):
        hud={r['observation_fy']:r for r in self.rows if r['agency_id']=='HUD'}
        self.assertEqual(hud[2020][c.NUMERIC[0]],'-5.04')
        self.assertEqual(hud[2021][c.NUMERIC[0]],'-1.57')
        self.assertEqual(hud[2020][c.NUMERIC[2]],'-50.6')
    def test_goal_transition_is_observed_not_imputed(self):
        for r in self.rows:
            if r[c.NUMERIC[1]]: self.assertEqual(Decimal(r[c.NUMERIC[1]]),Decimal(3 if r['observation_fy']<2024 else 5))
    def test_stable_aliases(self):
        self.assertTrue({'DOD','ED','DOS','TREAS'}<=self.ids)
        self.assertTrue(all(r['agency_id'] not in {'DOW','Education','STATE','Treasury','GW'} for r in self.rows))
    def test_bad_template_fails(self):
        with self.assertRaises(c.DataError): c.build_panel(self.sample[:-1],self.editions,self.docs)
    def test_missing_agency_is_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); (tmp/'test.json').write_text(json.dumps([r for r in self.editions[2021].values() if r['department_acronym']!='USDA']))
            manifest={'documents':[{'kind':'scorecard_json','scorecard_fy':2021,'filename':'test.json'}], 'errors':[]}
            c.source_records(tmp,manifest,self.ids)
            self.assertTrue(any('USDA' in r['error'] for r in manifest['errors']))
    def test_hash_tampering_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); (tmp/'data.json').write_text('tampered')
            (tmp/'manifest.json').write_text(json.dumps({'documents':[{'filename':'data.json','sha256':'invalid'}]}))
            with self.assertRaises(c.DataError): c.verified_snapshot(tmp)
    def test_sqlite_integrity_and_nulls(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/'test.sqlite'
            c.database(db,self.rows,self.provenance,self.flags,self.manifest,self.checks,self.comparisons)
            with sqlite3.connect(db) as con:
                self.assertEqual(con.execute('PRAGMA integrity_check').fetchone()[0],'ok')
                self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(),[])
                self.assertEqual(con.execute('SELECT COUNT(*) FROM scorecard_observations').fetchone()[0],144)
                self.assertEqual(con.execute('SELECT COUNT(sdvosb_prime_achievement_pct) FROM scorecard_observations').fetchone()[0],143)
                self.assertIsNone(con.execute("SELECT sdvosb_prime_achievement_pct FROM scorecard_observations WHERE agency_id='USAID' AND observation_fy=2025").fetchone()[0])

if __name__=='__main__': unittest.main()
