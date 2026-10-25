"""A5 EDA and frozen supplemental data checks."""
import shutil
import numpy as np
import pytest
from sdvosb_federal_analytics.etl import ROOT
from sdvosb_federal_analytics.supplement import extract,number,write_database,logical_hashes
from sdvosb_federal_analytics.eda import (agency_changes,describe_variables,welch_analysis,run_regressions,correlation_matrix)
RAW=ROOT/'data/raw/20261011T183300Z'

def test_integer_and_missing_values():
    assert number('N/A') is None
    assert number('0',integer=True)==0
    assert number('1,024',integer=True)==1024
    assert number('-5.04%')==-5.04
    with pytest.raises(ValueError): number('-1',integer=True)
    with pytest.raises(ValueError): number('3.1',integer=True)
    with pytest.raises(ValueError): number('error',integer=True)

def test_complete_supplement_and_provenance(derived):
    d,db,panel,h,v,report=derived
    assert len(h)==216 and h.achievement_pct.notna().sum()==215
    assert len(v)==144 and v.sdvosb_prime_contractor_count.notna().sum()==143
    assert report['excluded_gw_rows']==5
    assert report['historical_overlap_checks']==384
    assert report['vendor_overlap_checks']==192
    assert len(h[h.observation_fy==2017])==24
    assert h[h.observation_fy==2017].edition_count.eq(1).all()
    assert h.query('agency_id == "USAID" and observation_fy == 2025').achievement_pct.isna().all()
    assert v.query('agency_id == "USAID" and observation_fy == 2025').sdvosb_prime_contractor_count.isna().all()
    assert 'GW' not in set(h.agency_id)
    assert set(v.agency_id)==set(h.agency_id)

def test_supplement_two_builds_identical(derived):
    _,db,_,h,v,_=derived
    a=logical_hashes(db)
    write_database(db,h.to_dict('records'),v.to_dict('records'))
    assert logical_hashes(db)==a

def test_frozen_hash_rejected_without_database_replacement(derived,tmp_path,a4_test_database):
    _,db,_,_,_,_=derived
    before=db.read_bytes()
    fixture=tmp_path/'raw'; fixture.mkdir()
    # Hardlinks/symlinks deliberately avoided; must not mutate real fixture.
    shutil.copy2(RAW/'manifest.json',fixture/'manifest.json')
    for fy in range(2021,2026):shutil.copy2(RAW/f'agency-scorecards-{fy}.json',fixture/f'agency-scorecards-{fy}.json')
    with (fixture/'agency-scorecards-2021.json').open('ab') as fd: fd.write(b' ')
    with pytest.raises(ValueError,match='hash mismatch'):extract(fixture,a4_test_database)
    assert db.read_bytes()==before

def test_a4_parity_and_ratios(derived):
    _,db,panel,h,v,_=derived
    assert len(panel)==144 and panel.achievement_pct.notna().sum()==143
    assert panel.groupby(['agency_id','observation_fy']).size().eq(1).all()
    assert panel.query('agency_id == "NASA" and observation_fy == 2021').sdvosb_prime_contractor_count.iloc[0]==104
    assert h.query('agency_id == "NASA" and observation_fy == 2020').achievement_pct.iloc[0]==1.65
    assert v.sdvosb_to_small_business_ratio.dropna().between(0,1).all()

def test_a5_welch_reproduces_independent_result(derived):
    _,_,panel,_,_,_=derived
    frame=agency_changes(panel)
    r=welch_analysis(frame,2024)
    assert r['n_positive']==12 and r['n_zero']==12
    assert r['n_total']==24
    assert r['difference']==pytest.approx(.3708333333333331,abs=1e-10)
    assert r['welch_p_two_sided']==pytest.approx(.6443156291395863,abs=1e-10)
    assert r['ci_low']<0<r['ci_high']
    assert r['shapiro_positive_p']<.05
    assert r['rank_biserial']>=-1 and r['rank_biserial']<=1

def test_a5_fy2025_missingness(derived):
    _,_,panel,_,_,_=derived
    r=welch_analysis(agency_changes(panel),2025)
    assert (r['n_total'],r['n_positive'],r['n_zero'])==(23,11,12)
    assert r['difference']==pytest.approx(1.155)

def test_a5_univariate_multivariate(derived):
    _,_,panel,h,_,_=derived
    changes=agency_changes(panel)
    descr=describe_variables(panel,h,changes)
    assert len(descr)==8 and descr.missing.sum()>=2
    regressions,influence,extras=run_regressions(changes)
    assert set(regressions.model)=={'simple_OLS_HC3','multivariable_OLS_HC3'}
    assert regressions.nobs.eq(24).all()
    assert len(influence)==24
    assert extras['highest_cooks_agency']=='VA'
    m=correlation_matrix(changes)
    assert m.shape==(6,6)
    assert m.loc['shortfall_pp','baseline_average_pct']<-.9

def test_no_manufactured_missing_zero(derived):
    _,db,panel,h,v,report=derived
    missing_h=h.loc[(h.agency_id=='USAID')&(h.observation_fy==2025)]
    assert len(missing_h)==1 and np.isnan(missing_h.achievement_pct.iloc[0])
    assert panel.query('agency_id == "USAID" and observation_fy == 2025').observation_included.eq(0).all()

def test_exposure_constant_within_agency(derived):
    _,_,panel,_,_,_=derived
    assert panel.groupby('agency_id').shortfall_pp.nunique().eq(1).all()


def test_baseline_groups_are_not_fy2023_threshold_groups(derived):
    """Protect the distinction behind the corrected executive-summary wording."""
    _,_,panel,_,_,_=derived
    changes=agency_changes(panel)
    assert (changes.shortfall_pp>0).sum()==12
    fy2023=panel.query('observation_fy == 2023')
    assert (fy2023.achievement_pct>=5).sum()==14
    for agency in ('HUD','USDA'):
        r=fy2023.set_index('agency_id').loc[agency]
        assert r.shortfall_pp>0 and r.achievement_pct>5
    fy2025=panel.query('observation_fy == 2025 and shortfall_pp > 0 and achievement_pct >= 5')
    assert set(fy2025.agency_id)=={'DOS','HUD','TREAS','USDA'}


def test_label_spreading_is_bounded_and_deterministic():
    """Identical and tightly clustered labels separate without moving markers."""
    from sdvosb_federal_analytics.eda import _spread_label_y
    values=np.array([.2,.2,.21,.5,.8])
    a=_spread_label_y(values,0,1,.12)
    assert np.all(np.diff(a)>=.12-1e-12)
    assert a[0]>=0 and a[-1]<=1
    np.testing.assert_array_equal(a,_spread_label_y(values,0,1,.12))
    with pytest.raises(ValueError):_spread_label_y(values,0,1,.3)


@pytest.mark.parametrize('year,n_agencies',[(2024,24),(2025,23)])
def test_change_scatter_all_labels_legible_and_markers_unchanged(derived,year,n_agencies):
    """Inspect actual rendered text extents, not just successful PNG writing."""
    import matplotlib.pyplot as plt
    from sdvosb_federal_analytics.eda import change_scatter
    _,_,panel,_,_,_=derived
    changes=agency_changes(panel)
    fig,ax=change_scatter(changes,year)
    try:
        fig.canvas.draw();renderer=fig.canvas.get_renderer()
        expected=changes.dropna(subset=[f'delta_{year}'])
        assert len(ax.texts)==n_agencies
        assert {t.get_text() for t in ax.texts}==set(expected.agency_id)
        boxes=[t.get_bbox_patch().get_window_extent(renderer) for t in ax.texts]
        assert all(not a.overlaps(b) for i,a in enumerate(boxes) for b in boxes[i+1:])
        bounds=ax.get_window_extent(renderer)
        assert all(b.x0>=bounds.x0 and b.x1<=bounds.x1 and b.y0>=bounds.y0 and b.y1<=bounds.y1 for b in boxes)
        plotted=ax.collections[0].get_offsets()
        actual=sorted(tuple(map(float,p)) for p in plotted)
        wanted=sorted(zip(expected.shortfall_pp,expected[f'delta_{year}']))
        np.testing.assert_allclose(actual,wanted,rtol=0,atol=1e-12)
        assert 'FY2021–FY2023' in ax.get_legend().get_title().get_text()
    finally:
        plt.close(fig)


def test_supplement_missing_a4_does_not_create_database(tmp_path):
    """Read-only A4 access fails without creating a misleading empty file."""
    import sqlite3
    missing=tmp_path/'missing.sqlite'
    with pytest.raises(sqlite3.OperationalError):extract(RAW,missing)
    assert not missing.exists()


def test_supplement_cannot_overwrite_a4(derived,a4_test_database):
    """An explicit CLI output/input collision is rejected before any write."""
    from sdvosb_federal_analytics.supplement import main
    before=a4_test_database.read_bytes()
    with pytest.raises(ValueError,match='must differ'):
        main(['--a4-db',str(a4_test_database),'--output',str(a4_test_database)])
    assert a4_test_database.read_bytes()==before


def test_a5_fixture_does_not_depend_on_project_database(derived,a4_test_database):
    """A clean checkout can run all tests without a project-output database."""
    d,db,panel,_,_,_=derived
    project_outputs=(ROOT/'data/processed').resolve()
    assert not a4_test_database.resolve().is_relative_to(project_outputs)
    assert not db.resolve().is_relative_to(project_outputs)
    assert db.parent==d
    assert len(panel)==144


def test_a5_fixture_preserves_its_a4_input(derived,a4_test_database):
    """Reading and rebuilding A5 tables must leave the isolated A4 bytes intact."""
    _,db,_,history,vendors,_=derived
    from sdvosb_federal_analytics.eda import load_tables
    before=a4_test_database.read_bytes()
    write_database(db,history.to_dict('records'),vendors.to_dict('records'))
    load_tables(a4_test_database,db)
    assert a4_test_database.read_bytes()==before


def test_supplement_report_cannot_alias_a4(tmp_path):
    """A symlinked report must not bypass source/output protection."""
    from sdvosb_federal_analytics.supplement import main
    source=tmp_path/'source.sqlite';source.write_bytes(b'unchanged source')
    (tmp_path/'a5_supplement_validation.json').symlink_to(source)
    with pytest.raises(ValueError,match='must differ'):
        main(['--a4-db',str(source),'--output',str(tmp_path/'analysis.sqlite')])
    assert source.read_bytes()==b'unchanged source'
    assert not (tmp_path/'analysis.sqlite').exists()


def test_supplement_output_cannot_equal_report(tmp_path):
    """Reject a database filename that would be replaced by the JSON report."""
    from sdvosb_federal_analytics.supplement import main
    source=tmp_path/'source.sqlite';source.write_bytes(b'unchanged source')
    output=tmp_path/'a5_supplement_validation.json'
    with pytest.raises(ValueError,match='must differ'):
        main(['--a4-db',str(source),'--output',str(output)])
    assert not output.exists()
