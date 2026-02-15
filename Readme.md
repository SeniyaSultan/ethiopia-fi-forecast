# Ethiopia Financial Inclusion Forecasting

[![CI](https://github.com/yourusername/ethiopia-fi-forecast/actions/workflows/unittests.yml/badge.svg)](https://github.com/yourusername/ethiopia-fi-forecast/actions/workflows/unittests.yml)

## Business Problem

A consortium of development finance institutions, mobile money operators (Telebirr, M-Pesa), and the National Bank of Ethiopia needs to understand and predict the trajectory of financial inclusion in Ethiopia. Despite a massive expansion of mobile money—Telebirr surpassing 54 million users and M-Pesa reaching over 10 million—formal account ownership only grew from 46% (2021) to 49% (2024). This slowdown raises critical questions:

- What factors drive (or hinder) financial inclusion in Ethiopia?
- How do specific events—policy changes, product launches, infrastructure investments—affect inclusion indicators?
- What will account ownership and digital payment usage look like in 2025–2027?

The consortium needs data‑driven insights to guide investments, policy, and product strategies.

## Solution Overview

We developed an end‑to‑end forecasting system that:

- **Enriches** the provided unified dataset with additional observations (e.g., gender‑disaggregated Findex data, infrastructure metrics) and events (regulatory changes, new market entries).
- **Models** the impact of events using an association matrix derived from `impact_link` records and comparable country evidence.
- **Forecasts** two core Global Findex indicators:
  - **Access** – Account ownership rate (% of adults)
  - **Usage** – Digital payment adoption rate (% of adults)
  - For the years 2025–2027, with uncertainty bounds.
- **Presents** results through an interactive Streamlit dashboard that allows stakeholders to explore trends, event impacts, and scenarios.

## Key Results

- **Account ownership** is projected to reach **52–55% by 2027** under a base scenario (up from 49% in 2024). The optimistic scenario, incorporating stronger mobile money adoption, could push it to 58%.
- **Digital payment usage** is forecasted to rise to **40–45% by 2027**, driven by continued expansion of agent networks and interoperability.
- The **gender gap** persists: female ownership lags male ownership by ~12 percentage points. Without targeted interventions, this gap may narrow only slowly.
- **Event impact analysis** confirms that the Telebirr launch (May 2021) contributed an estimated +4.75 pp to mobile money account ownership, while M‑Pesa’s entry (Aug 2023) added approximately +2 pp to digital payment usage.

## Project Structure

ethiopia-fi-forecast/
├── .github/workflows/ # CI (unittests.yml)
├── data/
│ ├── raw/ # Starter dataset + enriched data
│ └── processed/ # Cleaned, merged data
├── notebooks/ # Jupyter notebooks for each task
│ ├── 01_data_enrichment.ipynb
│ ├── 02_exploratory_analysis.ipynb
│ ├── 03_event_impact_modeling.ipynb
│ └── 04_forecasting.ipynb
├── src/ # Reusable Python modules
│ ├── data_loader.py
│ ├── data_enrichment.py
│ ├── eda_utils.py
│ ├── impact_model.py
│ └── forecast.py
├── dashboard/ # Streamlit app
│ └── app.py
├── tests/ # Unit tests (pytest)
├── reports/ # Generated figures
├── requirements.txt
├── README.md
└── .gitignore

text

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ethiopia-fi-forecast.git
   cd ethiopia-fi-forecast
   Install dependencies
   ```

bash
pip install -r requirements.txt
Run the dashboard

bash
streamlit run dashboard/app.py
Explore the notebooks (optional)

bash
jupyter notebook notebooks/
Technical Details
Data
Primary source: Provided unified dataset (ethiopia_fi_unified_data.csv) with observations (2011–2024 Findex surveys, operator reports), events, and impact links.

Enrichment: Added gender‑disaggregated Findex microdata, IMF FAS infrastructure indicators (ATMs, bank branches), GSMA mobile adoption stats, and key events from news archives (e.g., Safaricom entry, EthSwitch interoperability launch).

Data quality: All additions are documented with source_url, confidence, and notes in the enrichment log.

Event Impact Modeling
Approach: Built an association matrix linking each event to affected indicators, using impact_magnitude and lag_months from impact_link records. For events without direct links, we borrowed evidence from comparable countries (e.g., Kenya’s M‑Pesa experience).

Validation: Compared model predictions against actual changes after the Telebirr and M‑Pesa launches; errors were within acceptable ranges (e.g., Telebirr impact error < 1 pp).

Forecasting
Method: Linear trend + event adjustments, with separate models for Access and Usage.

Uncertainty: 80% confidence intervals generated via bootstrapping residual errors.

Scenarios: Base (current trends continue), Optimistic (accelerated adoption due to new policies), Pessimistic (delayed infrastructure or regulatory hurdles).

Dashboard
Framework: Streamlit

Key pages:

Overview: Summary metrics (current rates, growth since last survey).

Trends: Interactive time series of key indicators with event markers.

Forecasts: Projections to 2027 with confidence bands and scenario toggles.

Event Impact: Heatmap of event‑indicator associations.

Interactivity: Date range selectors, scenario dropdowns, and tooltips explaining each chart.

Limitations and Assumptions
Sparse historical data: Only five Findex surveys (2011–2024) are available; therefore forecasts have wide confidence intervals.

Event impacts are static: We assume the effect of a past event remains constant over the forecast horizon; in reality, impacts may decay or amplify.

No interaction effects: Events are treated independently; combined effects may not be purely additive.

External factors: Macroeconomic shocks, political instability, or unforeseen technological shifts are not modelled.

For a full list of assumptions and validation checks, see docs/model_assumptions.md.

Future Improvements
Incorporate high‑frequency proxy data (e.g., mobile transaction volumes) to nowcast between survey years.

Refine event impacts using Bayesian structural time series to better estimate causal effects.

Add sub‑national forecasts (urban/rural, regional) to target interventions more precisely.

Deploy the dashboard on a public cloud (e.g., Streamlit Sharing, Heroku) for wider access.

## Author

**Seniya Sultan**  
[LinkedIn](https://www.linkedin.com/in/seniya-sultan-464486324/)  
[GitHub](https://github.com/SeniyaSultan)
