(() => {
  'use strict';

  const initDetails = (root) => {
    if (root.dataset.scorecardsInitialized === 'true') {
      return;
    }

    root.dataset.scorecardsInitialized = 'true';

    const form = root.querySelector('.agency-scorecards-form');
    const agencySelect = root.querySelector('.agency-scorecards-agency');
    const yearSelect = root.querySelector('.agency-scorecards-year');
    const gradeElement = root.querySelector('.grade');
    const submitButton = form?.querySelector('[type="submit"]');
    const errorElement = root.querySelector('.agency-scorecards-error');
    const dataPath = String(root.dataset.dataPath || '').replace(/\/$/, '');
    const latestYear = root.dataset.latestYear;

    if (!form || !agencySelect || !yearSelect || !gradeElement || !dataPath) {
      console.error('Agency scorecards details is missing required markup or configuration.');
      return;
    }

    const chartsAvailable = typeof charter !== 'undefined' && typeof Chart !== 'undefined';

    if (chartsAvailable) {
      charter.init(
        root.querySelector('#primeBarChart'),
        root.querySelector('#primeLineChart'),
        root.querySelector('#subBarChart'),
        root.querySelector('#subLineChart'),
        root.querySelector('#comparisonBarChart'),
        root.querySelector('#active8aBarChart'),
        root.querySelector('#awardDollarsBarChart'),
        root.querySelector('#awardShareBarChart')
      );
    }

    const setLoading = (loading) => {
      root.setAttribute('aria-busy', loading ? 'true' : 'false');
      if (submitButton) {
        submitButton.disabled = loading;
      }
    };

    const showError = (message = '') => {
      if (!errorElement) {
        return;
      }

      errorElement.textContent = message;
      errorElement.hidden = !message;
    };

    const fetchYear = async (year) => {
      const response = await fetch(`${dataPath}/agency-scorecards-${encodeURIComponent(year)}.json`, {
        credentials: 'same-origin',
        headers: { Accept: 'application/json' },
      });

      if (!response.ok) {
        throw new Error(`Unable to load scorecard data (${response.status}).`);
      }

      return response.json();
    };

    const styleGrade = (grade = '') => {
      const formattedGrade = String(grade).replace(/[\W_]+/g, '');
      const colors = {
        A: '#C4E9B3',
        B: '#CCEAFF',
        C: '#FFFFB3',
        D: '#FEE3C2',
        F: '#F1A9A9',
      };

      gradeElement.style.backgroundColor = colors[formattedGrade] || '#E2EFD9';
    };

    const hydrate = (agencyData) => {
      Object.entries(agencyData).forEach(([key, value]) => {
        root.querySelectorAll(`[data-${key}]`).forEach((element) => {
          if (key === 'prime_footnotes' || key === 'sub_footnotes') {
            element.innerHTML = value ?? '';
          } else {
            element.textContent = value ?? '';
            element.setAttribute(`data-${key}`, value ?? '');
          }
        });
      });

      root.querySelectorAll('[data-fiscal_year_previous]').forEach((element) => {
        element.textContent = Number(agencyData.fiscal_year) - 1;
      });

      const setAsideSection = root.querySelector('section#set-aside');
      if (setAsideSection) {
        setAsideSection.hidden = !Object.prototype.hasOwnProperty.call(agencyData, 'set_aside_8a_dollars');
      }

      const newSetAsideSection = root.querySelector('section#set-aside-new');
      if (newSetAsideSection) {
        newSetAsideSection.hidden = !Object.prototype.hasOwnProperty.call(agencyData, 'set_aside_new_8a_dollars');
      }

      agencySelect.value = agencyData.department_acronym;
      yearSelect.value = String(agencyData.fiscal_year);
      styleGrade(agencyData.agency_grade);

      if (chartsAvailable) {
        try {
          charter.destroyCharts();
          charter.hydrateCharts(agencyData);
        } catch (error) {
          console.error('Unable to render agency scorecard charts.', error);
        }
      }
    };

    const loadDetails = async (year, agency, updateUrl = false) => {
      setLoading(true);
      showError();

      try {
        const data = await fetchYear(year);

        if (!Array.isArray(data)) {
          throw new Error('The scorecard data file is not an array.');
        }

        const agencyData = data.find((item) => item.department_acronym === agency)
          || data.find((item) => item.department_acronym === agencySelect.value)
          || data[0];

        if (!agencyData) {
          throw new Error(`No scorecard data found for ${agency} in ${year}.`);
        }

        hydrate(agencyData);

        if (updateUrl) {
          const url = new URL(window.location.href);
          url.searchParams.set('agency', agencyData.department_acronym);
          url.searchParams.delete('year');
          url.searchParams.set('scorecard_year', agencyData.fiscal_year || year);
          window.history.pushState({}, '', url);
        }
      } catch (error) {
        console.error('Unable to load the selected agency scorecard.', error);
        showError('Unable to load the selected agency scorecard data.');
      } finally {
        setLoading(false);
      }
    };

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      await loadDetails(yearSelect.value, agencySelect.value, true);
    });

    const params = new URLSearchParams(window.location.search);
    const requestedAgency = params.get('agency');
    const requestedYear = params.get('scorecard_year');

    const hasOption = (select, value) => value !== null
      && Array.from(select.options).some((option) => option.value === value);

    if (hasOption(agencySelect, requestedAgency)) {
      agencySelect.value = requestedAgency;
    }

    if (hasOption(yearSelect, requestedYear)) {
      yearSelect.value = requestedYear;
    } else if (hasOption(yearSelect, latestYear)) {
      yearSelect.value = latestYear;
    }

    void loadDetails(yearSelect.value, agencySelect.value);
  };

  const init = () => {
    document.querySelectorAll('.sba-agency-scorecards-details').forEach(initDetails);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
