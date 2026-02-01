# 🇪🇹 Forecasting Financial Inclusion in Ethiopia

**Interim Submission – Tasks 1 & 2**

This project builds a data-driven system to forecast Ethiopia’s financial inclusion using
time series data, national events, and policy interventions.

It follows the **Global Findex framework** and models two core pillars:

- **ACCESS** — Account Ownership
- **USAGE** — Digital Payment Adoption

---

## 📂 Project Structure

ethiopia-fi-forecast/

├── data/  
│ ├── raw/ # Starter dataset  
│ ├── processed/ # Enriched + cleaned data  
│  
├── notebooks/ # Analysis notebooks  
│ ├── 01_data_exploration.ipynb  
│ └── 02_eda_analysis.ipynb  
│  
├── reports/  
│ ├── figures/ # Charts from EDA  
│ └── data_enrichment_log.md  
│  
├── dashboard/ # (Future task)  
├── models/ # (Future task)  
├── src/  
├── requirements.txt  
├── README.md  
└── .gitignore

---

## 🧠 Unified Data Design

This dataset follows a **neutral schema**:

> **Events are NOT assigned to pillars.**  
> Their effects are captured using `impact_link` records.

| record_type | category | pillar  | Meaning                  |
| ----------- | -------- | ------- | ------------------------ |
| observation | (empty)  | YES     | Measured indicator       |
| target      | (empty)  | YES     | Policy goal              |
| event       | YES      | (empty) | Neutral event            |
| impact_link | (empty)  | YES     | Event → indicator effect |

This avoids bias and allows **one event to affect many pillars**.

---

## 🧪 Task 1 – Data Exploration & Enrichment

### ✔ Completed

- Loaded unified dataset
- Reviewed schema & reference codes
- Analyzed:
  - record types
  - pillars
  - sources
  - confidence levels
  - time coverage
- Added new indicators & events
- Documented all changes in:
