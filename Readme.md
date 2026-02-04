# Ethiopia Financial Inclusion Forecasting System

## 📊 Project Overview

A comprehensive forecasting system that tracks Ethiopia's digital financial transformation using time series methods. Built for Selam Analytics to help development finance institutions, mobile money operators, and the National Bank of Ethiopia understand and predict financial inclusion trends.

### 🎯 Business Need

Ethiopia is undergoing rapid digital financial transformation with Telebirr growing to 54M+ users since 2021 and M-Pesa reaching 10M+ users since 2023. This system forecasts two core dimensions of financial inclusion as defined by World Bank's Global Findex:

1. **Access** — Account Ownership Rate
2. **Usage** — Digital Payment Adoption Rate

## 📈 Key Features

### 1. Data Management

- Unified schema for observations, events, and impact links
- Enriched dataset with Ethiopian financial inclusion indicators
- Reference codes for data standardization

### 2. Forecasting Models

- Baseline trend forecasting (linear regression)
- Event-augmented modeling
- Scenario analysis (optimistic/base/pessimistic)
- Confidence interval estimation

### 3. Impact Analysis

- Event-impact association matrices
- Historical event effect estimation
- Policy impact validation

### 4. Visualization & Reporting

- Interactive dashboard (Streamlit)
- Comprehensive forecast visualizations
- Automated report generation

## 🏗️ Project Structure

ethiopia-fi-forecast/
├── data/
│ ├── raw/ # Raw data files
│ │ ├── ethiopia_fi_unified_data.csv
│ │ └── reference_codes.csv
│ └── processed/ # Processed data
│ ├── enriched_data.csv
│ ├── event_impact_matrix.csv
│ └── forecasts_2025_2027.csv
├── notebooks/ # Analysis notebooks
│ ├── 01_data_enrichment.py
│ ├── 02_eda_analysis.py
│ ├── 03_event_impact_modeling.py
│ └── 04_forecasting.py
├── src/ # Source code
│ ├── init.py
│ ├── data_processor.py
│ ├── forecast_model.py
│ ├── impact_model.py
│ └── visualization.py
├── dashboard/ # Interactive dashboard
│ ├── app.py
│ ├── components/
│ └── assets/
├── tests/ # Unit tests
├── models/ # Trained models
├── reports/ # Reports and figures
│ └── figures/
├── requirements.txt # Dependencies
└── README.md # This file

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/SeniyaSultan/ethiopia-fi-forecast.git
cd ethiopia-fi-forecast
```

2. Install Dependencies
   bash
   pip install -r requirements.txt
3. Run Forecasting Analysis
   bash

# Run the complete forecasting pipeline

python notebooks/04_forecasting.py

# Or run specific components

python -c "from src.forecast_model import FinancialInclusionForecaster; f = FinancialInclusionForecaster()" 4. Launch Dashboard
bash
streamlit run dashboard/app.py
📊 Forecasting Results
Account Ownership (Access)
Current (2024): 49%

2027 Forecast (Base): 56.3%

NFIS-II Target (2027): 60%

Growth Required: +3.7pp acceleration

Digital Payment Usage
Current (2024): 35%

2027 Forecast (Base): 48.7%

Growth (2024-2027): +13.7pp

🔧 Technical Implementation
Models
FinancialInclusionForecaster

Time series preparation and interpolation

Linear regression forecasting

Scenario analysis (optimistic/base/pessimistic)

Confidence interval calculation

ImpactModel

Event-impact matrix creation

Historical effect estimation

Impact validation against observed data

Data Schema
Observations: Measured values (Findex surveys, operator reports)

Events: Policies, product launches, milestones

Impact Links: Modeled relationships between events and indicators

Targets: Official policy goals (NFIS-II targets)

📈 Key Insights

1. Growth Patterns
   Account ownership growth slowed to +3pp (2021-2024) despite 65M+ mobile money accounts

Digital payment usage accelerating rapidly (+13.7pp projected 2024-2027)

P2P digital transfers now exceed ATM withdrawals (1.3x ratio)

2. Key Drivers
   Mobile Money Expansion: Telebirr and M-Pesa adoption

Infrastructure: 4G coverage, agent networks, smartphone penetration

Policy Initiatives: NFIS-II, digital ID, interoperability

3. Gender Gap
   Women's account ownership lags men by ~10 percentage points

Targeted interventions needed for rural women

🎯 Policy Recommendations
Immediate Actions (3-6 months)
Simplify KYC requirements for account opening

Expand agent networks in rural areas

Launch targeted campaigns for women and youth

Medium-term Initiatives (6-18 months)
Boost digital payment adoption through merchant incentives

Digitalize government payments and transfers

Enhance interoperability between payment providers

Long-term Strategies (18+ months)
Develop alternative credit scoring models

Implement cross-border payment integration

Establish financial education programs

📋 Data Sources
World Bank Global Findex Database (2011-2024)

Account ownership rates

Digital payment usage

Gender disaggregation

National Bank of Ethiopia Reports

Mobile money statistics

Agent network data

Transaction volumes

GSMA Mobile Money Reports

Mobile money adoption rates

Transaction patterns

Market trends

ITU Statistics

Mobile penetration

Internet access

Smartphone adoption

🧪 Testing
Run the test suite:

bash
python -m pytest tests/
🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add some AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👥 Team
Kerod - Project Lead

Mahbubah - Data Science Tutor

Filimon - Methodology Advisor

Seniya Sultan - Implementation Lead

📞 Contact
For questions or collaboration opportunities:

Email: analytics@selam.com

GitHub: @SeniyaSultan

Project Repository: ethiopia-fi-forecast

📚 References
World Bank Global Findex Database

National Bank of Ethiopia Financial Inclusion Reports

GSMA State of the Industry Report on Mobile Money

IMF Financial Access Survey

Ethiopia's National Financial Inclusion Strategy II (NFIS-II)

Built with ❤️ by Selam Analytics for Ethiopia's financial inclusion journey

text

## Git Workflow Instructions

Now let me guide you through the git workflow to push all updates:

### Step 1: Save the README.md

Save the above content as `README.md` in your project root.

### Step 2: Git Commands to Push Updates

```bash
# 1. Navigate to your project directory
cd /c/Users/jkk/OneDrive/Desktop/ethiopia-fi-forecast

# 2. Check current status
git status

# 3. Add all new and modified files
git add .

# 4. Commit changes
git commit -m "Complete implementation: Forecasting system with models, data, notebooks, and dashboard

- Added enriched dataset with 57 records
- Implemented forecasting and impact models
- Created 4 analysis notebooks
- Built interactive Streamlit dashboard
- Added comprehensive README documentation
- Generated forecasts for 2025-2027
- Included scenario analysis and visualizations"

# 5. Create and switch to a new branch
git checkout -b final-implementation

# 6. Push to the new branch
git push origin final-implementation

# 7. Go back to main branch
git checkout main

# 8. Merge the final implementation branch
git merge final-implementation

# 9. Push merged changes to main
git push origin main

# 10. Create a pull request (optional - if you want to review before merging)
# Visit: https://github.com/SeniyaSultan/ethiopia-fi-forecast/pulls
```
