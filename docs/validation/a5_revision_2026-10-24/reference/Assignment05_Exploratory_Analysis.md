# Assignment 5: Exploratory Data Analysis Module

## Overview
This assignment focuses on developing a comprehensive exploratory data analysis (EDA) module that uncovers key insights from your business data. You'll create reusable analytical functions, generate meaningful visualizations, and conduct statistical analysis to inform business decision-making and prepare for advanced modeling.

## Learning Objectives
- Conduct thorough exploratory data analysis using Python statistical libraries
- Create professional data visualizations that communicate business insights effectively
- Develop reusable analysis modules and functions for reproducible analytics
- Apply statistical methods to identify patterns, trends, and anomalies in business data
- Generate actionable insights that inform business strategy and decision-making

## Requirements

### Core Deliverables
- Modular EDA Python package with reusable analysis functions
- Comprehensive statistical analysis report with business insights
- Professional data visualization suite using Matplotlib/Seaborn
- Statistical testing and hypothesis validation where appropriate

### Technical Specifications
- Reusable analysis functions or classes in importable modules with proper documentation
- Statistical analysis using SciPy, Statsmodels, or equivalent libraries
- Static Matplotlib and Seaborn visualizations appropriate for business stakeholders; dashboard interactivity belongs in Assignment 7
- Integration with existing database and data pipeline from Assignment 4
- Jupyter notebook demonstrating analysis workflow and findings

## Grading Rubric

Total: 100 points. Each criterion is scored against the descriptors below; the point
value shown is the maximum for that criterion.

| Criteria | Points | Requirements for Full Credit |
|----------|--------|------------------------------|
| **Statistical Analysis** | 30 pts | Univariate, bivariate, and multivariate analysis appropriate to the data. At least one hypothesis test with correctly stated hypotheses, assumptions checked, and results interpreted (not just reported). |
| **Data Visualization** | 25 pts | Publication-quality figures with labeled axes, titles, and legible legends. Chart types match the analytical question. Readable in grayscale or colorblind-safe. |
| **Code Architecture** | 25 pts | Reusable analysis functions or classes in an importable module, not only notebook cells. Docstrings present. The notebook imports the module rather than duplicating it. |
| **Business Insights** | 20 pts | Findings stated as business implications, not statistical output. Executive summary a non-technical stakeholder could act on. Insights connect to the research question from Assignment 3. |

### Partial-Credit Bands
Applied within each criterion:

| Band | Share of criterion points | Description |
|------|--------------------------|-------------|
| Excellent | 90-100% | Meets every requirement above, with professional polish |
| Good | 80-89% | Meets requirements with minor gaps or rough edges |
| Satisfactory | 70-79% | Functional and meets the minimum, but incomplete in places |
| Needs Improvement | Below 70% | Missing, non-functional, or substantially incomplete |

## Submission Guidelines
- **Due Date**: Sunday, October 25th, 11:59 PM
- **Submission Format**: GitHub repository update with EDA module, analysis notebook, and executive summary. Push to your existing repository before the due date; there is nothing to submit to a course platform.
- **Late Work**: Subject to standard course late policy (10 percentage points per day)
- **AI Use Disclosure**: `docs/AI_USE.md` must be present and current (see the AI policy in the syllabus)
- **Required Documentation**: Analysis methodology documentation, code documentation, and business insights summary
- **Template**: `ReferenceGuides/templates/Assignment05_EDA_template.md` provides an optional evidence map aligned to this rubric

## Getting Started
1. Connect to your database from Assignment 4 and validate data quality
2. Create modular analysis functions for different aspects of your business problem
3. Conduct univariate, bivariate, and multivariate analysis appropriate to your domain
4. Generate visualizations that tell a compelling story about your data
5. Document findings and insights that will inform your modeling approach
6. Prepare executive summary highlighting key business implications

## Resources
- `ReferenceGuides/Statistical_Analysis_Guide.md` - test selection, assumption checking, effect sizes, and module structure
- Matplotlib and Seaborn documentation
- Business analytics reporting best practices guide
- Statistical testing reference materials and interpretation guides
- Executive summary templates and examples
