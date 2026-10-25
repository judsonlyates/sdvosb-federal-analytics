"""Reusable exploratory analysis of SBA SDVOSB agency-year scorecard data.

Assignment 5: import this module in the notebook rather than rewriting tests,
figures, or preprocessing in notebook cells. No causal estimands are identified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
import statsmodels.formula.api as smf

from .etl import ROOT


def load_tables(a4_database: Path, supplemental_database: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Read A4 canonical records and A5 additions without writing either database."""
    for path in (a4_database, supplemental_database):
        if not path.is_file():
            raise FileNotFoundError(f'Build database before running analysis: {path}')
    with sqlite3.connect(f'file:{a4_database.resolve()}?mode=ro',uri=True) as db:
        panel = pd.read_sql_query('''
            SELECT p.*,o.sdvosb_prime_goal_pct AS goal_pct,
                   o.sdvosb_prime_dollars_millions AS sdvosb_dollars_millions
            FROM panel_agency_year p JOIN scorecard_observations o
            ON p.agency_id=o.agency_id AND p.observation_fy=o.observation_fy
            ORDER BY p.agency_id,p.observation_fy
        ''',db)
    with sqlite3.connect(f'file:{supplemental_database.resolve()}?mode=ro',uri=True) as db:
        history=pd.read_sql_query('SELECT * FROM historical_achievement ORDER BY agency_id,observation_fy',db)
        vendors=pd.read_sql_query('SELECT * FROM vendor_counts ORDER BY agency_id,observation_fy',db)
    for tag,frame,expected in [('A4 panel',panel,144),('history',history,216),('vendors',vendors,144)]:
        if len(frame)!=expected or frame.duplicated(['agency_id','observation_fy']).any():
            raise ValueError(f'{tag} has unexpected rows or duplicate agency-year keys')
    both=panel.merge(vendors.drop(columns=['source_fy','source_field','source_sha256']),
                     on=['agency_id','observation_fy'],how='left',validate='one_to_one')
    if both.sdvosb_prime_contractor_count.notna().sum()!=143:
        raise ValueError('Vendor-count join lost source-reported observations')
    return both,history,vendors


def agency_changes(panel: pd.DataFrame) -> pd.DataFrame:
    """Create the 24-agency cross-section; preserve missing USAID FY2025."""
    wide=panel.pivot(index='agency_id',columns='observation_fy',values='achievement_pct')
    base=panel.query('observation_fy == 2023').set_index('agency_id')
    vendors_2023=base['sdvosb_prime_contractor_count']
    changes=base[['baseline_average_pct','shortfall_pp','sdvosb_dollars_millions']].copy()
    changes['delta_2024']=wide[2024]-wide[2023]
    changes['delta_2025']=wide[2025]-wide[2023]
    changes['sdvosb_contractors_2023']=vendors_2023
    if (changes.sdvosb_dollars_millions<=0).any() or changes.sdvosb_dollars_millions.isna().any():
        raise ValueError('Nonpositive/missing FY2023 dollars; cannot use log procurement scale')
    changes['log_fy2023_dollars']=np.log(changes.sdvosb_dollars_millions)
    changes['shortfall_group']=np.where(changes.shortfall_pp>0,'Below 5%','At/above 5%')
    changes=changes.reset_index()
    if len(changes)!=24 or changes.shortfall_pp.gt(0).sum()!=12:
        raise ValueError('Unexpected exposure distribution; inspect the A4 data')
    return changes


def describe_variables(panel: pd.DataFrame, history: pd.DataFrame, changes: pd.DataFrame) -> pd.DataFrame:
    """Univariate descriptive data with explicit missingness and displayed units."""
    fields=[('achievement_pct','SBA goaling achievement','percentage points',panel),
            ('goal_pct','Agency scorecard goal','percent',panel),
            ('sdvosb_dollars_millions','SBA-reported SDVOSB dollars','USD millions',panel),
            ('baseline_average_pct','FY2021–2023 baseline','percentage points',changes),
            ('shortfall_pp','Distance below 5%','percentage points',changes),
            ('sdvosb_prime_contractor_count','SDVOSB prime contractor count','contractors',panel),
            ('sdvosb_to_small_business_ratio','SDVOSB/all small-business contractor ratio','proportion',panel),
            ('achievement_pct','Historical achievement FY2017–2025','percentage points',history)]
    records=[]
    for field,label,units,frame in fields:
        v=frame[field]
        records.append(dict(variable=label,source_field=field,units=units,dtype=str(v.dtype),
                            total_rows=len(v),nonmissing=int(v.count()),missing=int(v.isna().sum()),
                            min=float(v.min()) if v.count() else None,
                            q25=float(v.quantile(.25)) if v.count() else None,
                            median=float(v.median()) if v.count() else None,
                            mean=float(v.mean()) if v.count() else None,
                            q75=float(v.quantile(.75)) if v.count() else None,
                            max=float(v.max()) if v.count() else None))
    return pd.DataFrame(records)


def welch_analysis(changes: pd.DataFrame, year: int) -> dict:
    """Fixed two-sided Welch group comparison and nonparametric sensitivity.

    Inferential H0: equal group means; H1: unequal group means. The scientific
    prediction is a larger positive-shortfall-group change, but the reported
    two-sided test also detects unexpected opposite-direction differences.
    """
    if year not in (2024,2025): raise ValueError('Only post-policy years 2024/2025 are defined')
    source=changes[['agency_id','shortfall_pp',f'delta_{year}']].dropna()
    positives=source.loc[source.shortfall_pp.gt(0),f'delta_{year}'].to_numpy()
    zero=source.loc[source.shortfall_pp.eq(0),f'delta_{year}'].to_numpy()
    n1,n0=len(positives),len(zero)
    if min(n1,n0)<5: raise ValueError('Too few agencies to run group test')
    difference=float(positives.mean()-zero.mean())
    s1=float(positives.var(ddof=1)); s0=float(zero.var(ddof=1))
    se=np.sqrt(s1/n1+s0/n0)
    df=(s1/n1+s0/n0)**2/((s1/n1)**2/(n1-1)+(s0/n0)**2/(n0-1))
    ttest=stats.ttest_ind(positives,zero,equal_var=False,alternative='two-sided')
    critical=stats.t.ppf(.975,df)
    pooled=np.sqrt(((n1-1)*s1+(n0-1)*s0)/(n1+n0-2))
    hedges=(difference/pooled)*(1-3/(4*(n1+n0-2)-1)) if pooled else None
    u=stats.mannwhitneyu(positives,zero,alternative='two-sided',method='asymptotic')
    rho,p_spearman=stats.spearmanr(source.shortfall_pp,source[f'delta_{year}'])
    return dict(year=year,n_total=n1+n0,n_positive=n1,n_zero=n0,
                mean_positive=float(positives.mean()),mean_zero=float(zero.mean()),
                difference=difference,standard_error=float(se),welch_df=float(df),
                welch_t=float(ttest.statistic),welch_p_two_sided=float(ttest.pvalue),
                ci_low=float(difference-critical*se),ci_high=float(difference+critical*se),
                hedges_g=float(hedges) if hedges is not None else None,
                shapiro_positive_p=float(stats.shapiro(positives).pvalue),
                shapiro_zero_p=float(stats.shapiro(zero).pvalue),
                mann_whitney_u=float(u.statistic),mann_whitney_p=float(u.pvalue),
                rank_biserial=float(2*u.statistic/(n1*n0)-1),
                spearman_rho=float(rho),spearman_p=float(p_spearman))


def run_regressions(changes: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame,dict]:
    """Simple and multivariable A5 OLS, with HC3 and influence diagnostics."""
    data=changes.dropna(subset=['delta_2024','shortfall_pp','log_fy2023_dollars']).copy()
    simple=smf.ols('delta_2024 ~ shortfall_pp',data=data).fit(cov_type='HC3',use_t=True)
    multi=smf.ols('delta_2024 ~ shortfall_pp + log_fy2023_dollars',data=data).fit(cov_type='HC3',use_t=True)
    if len(data)!=24 or simple.model.rank!=len(simple.params) or multi.model.rank!=len(multi.params):
        raise ValueError('Unexpected A5 regression rank or sample')
    out=[]
    for model_name,model in [('simple_OLS_HC3',simple),('multivariable_OLS_HC3',multi)]:
        ci=model.conf_int()
        for term in model.params.index:
            out.append(dict(model=model_name,variable=term,coefficient=float(model.params[term]),
                            se_hc3=float(model.bse[term]),p_value=float(model.pvalues[term]),
                            ci_low=float(ci.loc[term,0]),ci_high=float(ci.loc[term,1]),
                            r_squared=float(model.rsquared),nobs=int(model.nobs)))
    influence=multi.get_influence()
    cooks=influence.cooks_distance[0]
    leverage=influence.hat_matrix_diag
    diagnostic=pd.DataFrame({'agency_id':data.agency_id.to_numpy(),
                             'cooks_distance':cooks,'leverage':leverage,
                             'residual':multi.resid.to_numpy(),
                             'threshold_4_over_n':4/len(data)}).sort_values('cooks_distance',ascending=False)
    extras=dict(n_agencies=int(len(data)),
                highest_cooks_agency=str(diagnostic.iloc[0].agency_id),
                highest_cooks=float(diagnostic.iloc[0].cooks_distance),
                n_above_reference=int((diagnostic.cooks_distance>4/len(data)).sum()),
                note='Cook distance 4/n is a screening reference, not a deletion rule')
    return pd.DataFrame(out),diagnostic,extras


def correlation_matrix(changes: pd.DataFrame) -> pd.DataFrame:
    """Spearman correlations with pairwise complete-case deletion."""
    fields=['baseline_average_pct','shortfall_pp','delta_2024','delta_2025',
            'log_fy2023_dollars','sdvosb_contractors_2023']
    return changes[fields].corr(method='spearman',min_periods=10)


def _spread_label_y(values: np.ndarray, lower: float, upper: float, gap: float) -> np.ndarray:
    """Separate sorted label positions with bounded, minimum-gap isotonic placement."""
    values=np.asarray(values,dtype=float)
    if len(values)==0:
        return values.copy()
    if np.any(np.diff(values)<0) or gap<0 or (len(values)-1)*gap>upper-lower:
        raise ValueError('Label values must be sorted and fit the available bounds')
    # Pool adjacent violating blocks after subtracting the required linear gap.
    blocks=[]
    for i,value in enumerate(values-np.arange(len(values))*gap):
        blocks.append([float(value),1])
        while len(blocks)>1 and blocks[-2][0]>blocks[-1][0]:
            right=blocks.pop();left=blocks.pop()
            count=left[1]+right[1]
            blocks.append([(left[0]*left[1]+right[0]*right[1])/count,count])
    fitted=np.concatenate([np.repeat(value,count) for value,count in blocks])
    fitted=np.clip(fitted,lower,upper-(len(values)-1)*gap)
    return fitted+np.arange(len(values))*gap


def change_scatter(changes: pd.DataFrame, year: int):
    """Plot one year's unchanged agency points with deterministic, nonoverlapping labels.

    Zero-shortfall labels occupy a separated left-hand lane. Other labels use
    checked screen-space offsets and short leaders; no data point is jittered.
    Raises an explicit error rather than silently exporting overlapping labels.
    """
    if year not in (2024,2025):
        raise ValueError('A5 change scatter supports FY2024 or FY2025')
    g=changes.dropna(subset=[f'delta_{year}']).sort_values('agency_id').copy()
    g['exposure_group']=np.where(g.shortfall_pp>0,'Positive shortfall','Zero shortfall')
    fig,ax=plt.subplots(figsize=(11.5,7.5))
    sns.scatterplot(data=g,x='shortfall_pp',y=f'delta_{year}',hue='exposure_group',
                    style='exposure_group',hue_order=['Positive shortfall','Zero shortfall'],
                    style_order=['Positive shortfall','Zero shortfall'],s=85,ax=ax)
    y=g[f'delta_{year}'];span=float(y.max()-y.min())
    ax.set_xlim(-.85,float(g.shortfall_pp.max())+.65)
    ax.set_ylim(float(y.min())-.12*span,float(y.max())+.16*span)
    ax.axhline(0,color='.3',linestyle=':',lw=1)
    ax.set(xlabel='Baseline shortfall FY2021–FY2023 (percentage points)',
           ylabel=f'Change FY2023 to FY{year} (percentage points)',
           title=f'Agency shortfall versus FY{year} achievement change')
    ax.legend(fontsize=9,title='FY2021–FY2023 baseline group',loc='upper right')
    fig.subplots_adjust(bottom=.19)
    fig.canvas.draw()
    renderer=fig.canvas.get_renderer()
    bounds=ax.get_window_extent(renderer)
    point_boxes=[]
    from matplotlib.transforms import Bbox
    for row in g.itertuples(index=False):
        px,py=ax.transData.transform((row.shortfall_pp,getattr(row,f'delta_{year}')))
        point_boxes.append(Bbox.from_extents(px-7,py-7,px+7,py+7))
    occupied=[ax.get_legend().get_window_extent(renderer).expanded(1.03,1.08)]
    zero=g[g.shortfall_pp==0].sort_values([f'delta_{year}','agency_id'])
    zero_pixels=ax.transData.transform(np.column_stack([np.zeros(len(zero)),zero[f'delta_{year}']]))[:,1]
    separated=_spread_label_y(zero_pixels,bounds.y0+15,bounds.y1-15,17)
    for row,py in zip(zero.itertuples(index=False),separated):
        label_y=ax.transData.inverted().transform((bounds.x0,py))[1]
        text=ax.annotate(row.agency_id,(0,getattr(row,f'delta_{year}')),
                         xytext=(-.22,label_y),textcoords='data',ha='right',va='center',fontsize=8,
                         bbox=dict(facecolor='white',edgecolor='none',pad=.2),
                         arrowprops=dict(arrowstyle='-',color='.45',lw=.65,shrinkA=2,shrinkB=5))
    # Exclude leaders from occupied text bounds: they may cross open plot space.
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    occupied=[ax.get_legend().get_window_extent(renderer).expanded(1.03,1.08)]
    occupied.extend(t.get_bbox_patch().get_window_extent(renderer).expanded(1.1,1.25) for t in ax.texts)
    candidates=[(dx,dy) for dy in (10,-12,24,-26,38,-40,52,-54,66,-68)
                         for dx in (8,-8,20,-20)]
    for row in g[g.shortfall_pp>0].sort_values([f'delta_{year}','agency_id']).itertuples(index=False):
        for dx,dy in candidates:
            text=ax.annotate(row.agency_id,(row.shortfall_pp,getattr(row,f'delta_{year}')),
                             xytext=(dx,dy),textcoords='offset points',
                             ha='left' if dx>0 else 'right',va='center',fontsize=8,
                             bbox=dict(facecolor='white',edgecolor='none',pad=.2),
                             arrowprops=dict(arrowstyle='-',color='.45',lw=.65,shrinkA=2,shrinkB=5))
            text.update_positions(renderer);text.update_bbox_position_size(renderer)
            box=text.get_bbox_patch().get_window_extent(renderer).expanded(1.1,1.25)
            fits=box.x0>=bounds.x0 and box.x1<=bounds.x1 and box.y0>=bounds.y0 and box.y1<=bounds.y1
            if fits and not any(box.overlaps(other) for other in occupied+point_boxes):
                occupied.append(box)
                break
            text.remove()
        else:
            plt.close(fig)
            raise ValueError(f'Could not place {row.agency_id} label without overlap for FY{year}')
    return fig,ax


def figures(panel:pd.DataFrame,history:pd.DataFrame,changes:pd.DataFrame,
            correlations:pd.DataFrame,influence:pd.DataFrame,dest:Path) -> list[str]:
    """Save static publication-oriented EDA PNG figures with consistent style."""
    dest.mkdir(parents=True,exist_ok=True)
    sns.set_theme(style='whitegrid',context='notebook',palette='colorblind')
    palette=sns.color_palette('colorblind',2)
    saved=[]
    def save(fig,name,note=None):
        """Write one figure to the figures directory at 180 DPI and record its filename.

        If ``note`` is given it is drawn as a small footer beneath the axes so the
        source years and caveats travel with the image. The figure is closed after
        saving so long notebook sessions do not accumulate open Matplotlib figures.
        """
        fig.subplots_adjust(bottom=max(fig.subplotpars.bottom,.19))
        if note: fig.text(.015,.012,note,fontsize=8,ha='left',color='.35')
        fig.savefig(dest/name,dpi=180,bbox_inches='tight',pad_inches=.18)
        saved.append(name);plt.close(fig)

    # Plot 1: full exposure distribution, including zero-mass.
    sorted_ag=changes.sort_values(['shortfall_pp','agency_id'])
    colors=[palette[0] if v>0 else '.6' for v in sorted_ag.shortfall_pp]
    fig,ax=plt.subplots(figsize=(9,7))
    ax.barh(sorted_ag.agency_id,sorted_ag.shortfall_pp,color=colors)
    ax.set(xlabel='Pre-policy distance below 5% (percentage points)',ylabel='Agency',title='Baseline SDVOSB shortfall, all 24 agencies')
    save(fig,'a5_01_shortfall_distribution.png','FY2021–FY2023 baseline. Twelve agencies have zero shortfall; zero does not mean untreated.')

    # Plot 2: 24 small multiple histories for all nine years.
    fig,axes=plt.subplots(6,4,figsize=(16,17),sharex=True)
    for ax,(agency,g) in zip(axes.flat,history.groupby('agency_id')):
        g=g.sort_values('observation_fy')
        ax.plot(g.observation_fy,g.achievement_pct,marker='o',markersize=2.5,lw=1.6,
                color=palette[0] if changes.set_index('agency_id').loc[agency,'shortfall_pp']>0 else '.45')
        ax.axvline(2024,lw=.8,linestyle=':',color='.5')
        ax.set_title(agency,fontsize=9)
        ax.tick_params(labelsize=7)
    fig.suptitle('Agency-level SBA SDVOSB goaling achievement, FY2017–FY2025',y=.999,fontsize=16)
    fig.supxlabel('Fiscal year',y=.065);fig.supylabel('Reported achievement (%)',x=.04)
    fig.subplots_adjust(hspace=.48,wspace=.3)
    save(fig,'a5_02_historical_agency_trajectories.png','24 agencies; source-declared USAID FY2025 missing. SBA percentages may include special goaling credit.')

    # Plot 3: group means and statutory reference, correctly labeled.
    p=panel.groupby('observation_fy',as_index=False).apply(lambda x:pd.Series({'below_mean':x.loc[x.shortfall_pp>0,'achievement_pct'].mean(),
       'at_or_above_mean':x.loc[x.shortfall_pp==0,'achievement_pct'].mean()}),include_groups=False).reset_index(drop=True)
    p['fiscal_year']=list(range(2020,2026))
    fig,ax=plt.subplots(figsize=(9,5))
    for y,label,c,style in [('below_mean','Positive shortfall',palette[0],'-'),('at_or_above_mean','Zero shortfall',palette[1],'--')]:
        ax.plot(p.fiscal_year,p[y],marker='o',color=c,linestyle=style,label=label)
    ax.step([2020,2024,2025],[3,5,5],where='post',linestyle=':',color='k',alpha=.5,label='Government-wide benchmark (reference)')
    ax.axvline(2024,color='.5',linestyle=':',lw=1)
    ax.set(xlabel='Fiscal year',ylabel='Mean achievement (%)',title='Mean SBA-reported achievement by baseline shortfall group')
    ax.legend(loc='best',fontsize=9)
    save(fig,'a5_03_group_trends.png','Group means by FY; FY2024 transition year. Reference line is not an agency-specific negotiated goal.')

    # Plot 4/5: the two years shown separately, each agency labeled.
    for year in (2024,2025):
        g=changes.dropna(subset=[f'delta_{year}'])
        fig,ax=change_scatter(changes,year)
        missing_note=' USAID FY2025 is source-declared missing.' if year==2025 else ''
        save(fig,f'a5_0{4 if year==2024 else 5}_shortfall_vs_change_{year}.png',
             f'FY2023 shares a term with the exposure definition; this chart is exploratory. n={len(g)} agencies.{missing_note}')

    # Plot 6: contractor counts: agency-level median, not falsely distinct government-wide sum.
    v=panel.groupby(['observation_fy',panel.shortfall_pp.gt(0)])['sdvosb_prime_contractor_count'].median().reset_index(name='median_contractors')
    v['group']=np.where(v.shortfall_pp,'Positive shortfall','Zero shortfall')
    fig,ax=plt.subplots(figsize=(9,5))
    sns.lineplot(data=v,x='observation_fy',y='median_contractors',hue='group',style='group',
                 hue_order=['Positive shortfall','Zero shortfall'],
                 style_order=['Positive shortfall','Zero shortfall'],markers=True,dashes=True,ax=ax)
    ax.legend(title='FY2021–FY2023 baseline group',fontsize=9)
    ax.set(xlabel='Fiscal year',ylabel='Median agency count\n(SDVOSB prime contractors)',title='Contractor breadth, descriptive secondary outcome')
    save(fig,'a5_06_vendor_counts.png','Agency medians, not a cross-agency distinct contractor total. FY2020–FY2025; USAID FY2025 is missing.')

    # Plot 7: ratio uses a different denominator from achievement.
    v=panel.groupby(['observation_fy',panel.shortfall_pp.gt(0)])['sdvosb_to_small_business_ratio'].median().reset_index(name='median_ratio')
    v['group']=np.where(v.shortfall_pp,'Positive shortfall','Zero shortfall')
    fig,ax=plt.subplots(figsize=(9,5))
    sns.lineplot(data=v,x='observation_fy',y='median_ratio',hue='group',style='group',
                 hue_order=['Positive shortfall','Zero shortfall'],
                 style_order=['Positive shortfall','Zero shortfall'],markers=True,dashes=True,ax=ax)
    ax.legend(title='FY2021–FY2023 baseline group',fontsize=9)
    ax.set(xlabel='Fiscal year',ylabel='Median contractor-count ratio\n(SDVOSB / all small business)',title='SDVOSB share of small-business prime contractor counts')
    save(fig,'a5_07_vendor_ratio.png','Count ratio, not a contracting dollar share; agency medians FY2020–FY2025.')

    # Plot 8: selected pairwise Spearman correlations.
    fig,ax=plt.subplots(figsize=(9,7))
    sns.heatmap(correlations,cmap='vlag',center=0,vmin=-1,vmax=1,annot=True,fmt='.2f',ax=ax,square=True)
    ax.set_title('Exploratory Spearman correlation matrix')
    fig.subplots_adjust(bottom=.34,left=.2)
    save(fig,'a5_08_spearman_correlations.png','Pairwise-complete agency-level correlations, n ≤24; several variables are mechanically related.')

    # Plot 9: group Q-Q assumption checks.
    groups=[('Positive shortfall',changes.loc[changes.shortfall_pp>0,'delta_2024']),
            ('Zero shortfall',changes.loc[changes.shortfall_pp==0,'delta_2024'])]
    fig,axes=plt.subplots(1,2,figsize=(10,4.5))
    for ax,(label,values) in zip(axes,groups):
        stats.probplot(values,dist='norm',plot=ax)
        ax.set_title(f'Q–Q: {label} (n={len(values)})')
    save(fig,'a5_09_qq_welch_assumptions.png','Diagnostics inform caution, not ex-post selection of the hypothesis test.')

    # Plot 10: influence of agencies on multivariable descriptive regression.
    fig,ax=plt.subplots(figsize=(9,5))
    ax.bar(influence.agency_id,influence.cooks_distance,color=palette[0])
    ax.axhline(4/24,linestyle=':',color='.3',label='4/n screening reference')
    ax.tick_params(axis='x',rotation=75,labelsize=8)
    ax.set(ylabel="Cook's distance",xlabel='Agency',title='Influence in exploratory multivariable OLS (FY2024 change)')
    ax.legend()
    save(fig,'a5_10_multivariable_influence.png','Reference is not an automatic agency exclusion criterion; n=24.')
    return saved


def run_eda(a4_database: Path,supplemental_database: Path,results_dir:Path,figures_dir:Path) -> dict:
    """Compute and persist all A5 deliverables from reproducible source databases."""
    results_dir.mkdir(parents=True,exist_ok=True)
    panel,history,vendors=load_tables(a4_database,supplemental_database)
    changes=agency_changes(panel)
    summary=describe_variables(panel,history,changes)
    tests={str(y):welch_analysis(changes,y) for y in (2024,2025)}
    estimates,influence,diagnostics=run_regressions(changes)
    correlations=correlation_matrix(changes)
    chart_names=figures(panel,history,changes,correlations,influence,figures_dir)
    changes.to_csv(results_dir/'a5_agency_changes.csv',index=False,float_format='%.12g')
    summary.to_csv(results_dir/'a5_descriptive_summary.csv',index=False,float_format='%.12g')
    estimates.to_csv(results_dir/'a5_regression_estimates.csv',index=False,float_format='%.12g')
    influence.to_csv(results_dir/'a5_influence.csv',index=False,float_format='%.12g')
    correlations.to_csv(results_dir/'a5_correlations.csv',float_format='%.12g')
    report={'source':'Frozen SBA scorecards 2026-10-11; A4 canonical database + A5 supplemental database',
            'analytic_population_agencies':24,'agency_years':len(panel),'complete_achievement_rows':int(panel.achievement_pct.count()),
            'missing_agency_year':'USAID FY2025','shortfall_positive_agencies':int((changes.shortfall_pp>0).sum()),
            'shortfall_zero_agencies':int((changes.shortfall_pp==0).sum()),
            'tests':tests,'multivariable_influence':diagnostics,'saved_figures':chart_names,
            'research_boundary':'Exploratory associations only; baseline mechanically shares FY2023 with changes; not causal.'}
    (results_dir/'a5_results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main(argv=None):
    """Command-line entry point: build the A5 descriptive and exploratory outputs.

    Reads the graded A4 database and the A5 supplementary database, writes the
    result tables under ``results/`` and the figures under ``figures/``, and prints
    a short JSON summary. Returns a process exit code (0 on success).
    """
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--a4-db',type=Path,default=ROOT/'data/processed/scorecards.sqlite')
    parser.add_argument('--supp-db',type=Path,default=ROOT/'data/processed/analysis.sqlite')
    parser.add_argument('--results',type=Path,default=ROOT/'results')
    parser.add_argument('--figures',type=Path,default=ROOT/'figures')
    a=parser.parse_args(argv)
    report=run_eda(a.a4_db,a.supp_db,a.results,a.figures)
    print(json.dumps({'agency_years':report['agency_years'],'n_figures':len(report['saved_figures']),
                      'welch_2024':report['tests']['2024']['welch_p_two_sided'],
                      'welch_2025':report['tests']['2025']['welch_p_two_sided']},indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
