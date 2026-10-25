"""Self-contained A5 fixtures; no prebuilt project database is required."""
import pytest
from sdvosb_federal_analytics.etl import ROOT, main as build_a4
from sdvosb_federal_analytics.supplement import extract,write_database
from sdvosb_federal_analytics.eda import load_tables

RAW=ROOT/'data/raw/20261011T183300Z'


@pytest.fixture(scope='session')
def a4_test_database(tmp_path_factory):
    """Build the frozen A4 inputs in pytest storage, never in project outputs."""
    output=tmp_path_factory.mktemp('a4_test_inputs')
    status=build_a4(['--offline','--raw-dir',str(RAW),'--output-dir',str(output)])
    if status != 0:
        pytest.fail(f'Offline A4 test-input build failed with exit status {status}')
    return output/'scorecards.sqlite'

@pytest.fixture(scope='module')
def derived(tmp_path_factory,a4_test_database):
    """Build A5 tables using the isolated A4 fixture and temporary outputs."""
    d=tmp_path_factory.mktemp('a5_derive')
    hist, vendors, report=extract(RAW,a4_test_database)
    db=d/'analysis.sqlite'
    write_database(db,hist,vendors)
    panel,h,v=load_tables(a4_test_database,db)
    return d,db,panel,h,v,report
