# Enterprise Credit Risk Analytics Dashboard — User & Administrator Guide

**Document Control & Technical Architecture**
- **System Scope**: Multi-Page Streamlit Analytics & Model Risk Governance Application
- **Target Audience**: Credit Risk Analytics, Portfolio Risk Managers, Independent Model Validation, Executive Risk Committee
- **Technology Stack**: Python, Streamlit, Plotly, Pandas, PyTorch, LightGBM, Statsmodels
- **Author**: Quantitative Risk Analytics & Dashboard Engineering Team

---

## 1. Executive Summary & Dashboard Architecture

The **Enterprise Credit Risk Analytics Dashboard** is a production-quality, multi-page web platform designed for institutional credit risk monitoring, model governance, explainability, stress testing, and model risk compliance under **Federal Reserve SR 11-7**, **OCC 2011-12**, and **FCRA** guidelines.

### Directory Structure & Modular Design
```
c:\Users\BIBEK\OneDrive\Desktop\Credit-Risk-Modelling\dashboard/
├── app.py                         # Landing Page & Application Entry Point
├── assets/
│   └── styles.css                 # Custom Institutional CSS Theme
├── config/
│   ├── constants.py               # Constants, Thresholds & Target Benchmarks
│   └── theme.py                   # Plotly & Streamlit Color Palettes
├── utils/
│   ├── data_loader.py             # Cached Data Loader (@st.cache_data)
│   └── model_loader.py            # Cached Model Loader & Inference Engine (@st.cache_resource)
├── components/
│   ├── kpi_cards.py               # Metric Cards & Traffic Light Badges
│   ├── charts.py                  # Reusable Plotly Chart Generators
│   ├── sidebar.py                 # Multi-variate Sidebar Filter Controls
│   └── tables.py                  # Styled DataTables & CSV Downloads
└── pages/
    ├── 1_Executive_Dashboard.py    # Portfolio KPIs & Traffic Light Status Banner
    ├── 2_Portfolio_Analytics.py    # Portfolio Filtering, HHI Concentration & Seasoning
    ├── 3_Model_Performance.py      # Champion vs Challenger ROC, KS & Cutoff Slider
    ├── 4_Explainable_AI.py        # Global/Local SHAP & FCRA Adverse Action Generator
    ├── 5_Stress_Testing.py        # Interactive Scenario Simulator & Expected Loss Delta
    ├── 6_Model_Monitoring.py      # PSI, CSI, Data Drift & Retraining Decision Engine
    ├── 7_Deep_Learning_Benchmark.py# Triangulation Benchmark (Scorecard vs LightGBM vs MLP)
    └── 8_Reports.py               # Governance Document Center & Downloadable Audits
```

---

## 2. Navigation & Module Functionality

### 2.1 Page 1: Executive Dashboard
- **Key Metrics**: Total Loans, Total Exposure ($), Average Interest Rate, Empirical Default Rate, Average FICO, Average DTI, Average Income, Portfolio Health Score.
- **Executive Banner**: Traffic Light Status Badge (`GREEN (PASS)` / `YELLOW (WARN)` / `RED (ALERT)`).
- **Charts**: Portfolio Exposure ($ Millions) by Risk Grade.

### 2.2 Page 2: Portfolio Analytics
- **Sidebar Filters**: Filter portfolio dynamically by Risk Grade (A–G), State, Purpose, FICO Score, and Loan Amount.
- **Vintage Seasoning**: Historical default rate trends across 2007–2018 origination cohorts.
- **Concentration Risk**: Herfindahl-Hirschman Concentration Index ($\text{HHI} = 584.2$, Unconcentrated).
- **Recovery Analysis**: Mean post-default recovery rate ($6.97\%$) and implied $\text{LGD}$ ($93.03\%$).

### 2.3 Page 3: Model Performance
- **Model Comparison**: Champion Logistic Scorecard vs Challenger LightGBM.
- **Interactive Threshold Slider**: Adjust probability cutoff ($0.05$ to $0.50$) to evaluate real-time approval rates and default rates in approved population.

### 2.4 Page 4: Explainable AI (XAI)
- **Global SHAP**: Rank top 10 risk drivers by Mean $| \text{SHAP} |$.
- **Local Borrower Inspector**: Select borrower index ($0$ to $1,000$) to view exact waterfall attribution and top 4 FCRA Adverse Action reason codes.

### 2.5 Page 5: Stress Testing & Scenario Simulator
- **Preset Scenarios**: Macro Adverse and Macro Severe Adverse Expected Loss expansion.
- **Interactive Simulator**: Adjust Income shock (%), Interest rate (bps), DTI shift (%), and FICO drop (pts) to compute real-time $\Delta \text{PD}$ and $\Delta \text{EL}$.

### 2.6 Page 6: Model Monitoring
- **Population Stability Index (PSI)**: Overall portfolio $\text{PSI} = 0.0412$ ($\text{Green} < 0.10$).
- **Characteristic Stability (CSI)**: Per-feature distribution drift audit.
- **Data Drift**: Kolmogorov-Smirnov 2-sample statistical tests ($D_{\text{stat}}$, $p$-value).
- **Automated Retraining Status**: Evaluates multi-criterion triggers ($\text{PSI} \ge 0.25$, $\Delta \text{AUC} > -0.05$, $\text{KS} < 30.0\%$).

### 2.7 Page 7: Deep Learning Benchmark
- **Master Benchmark Matrix**: Scorecard vs LightGBM vs PyTorch MLP across 9 evaluation dimensions.
- **Governance Decision**: Formally documents the rejection of Deep Learning for production credit origination.

### 2.8 Page 8: Governance Reports
- **Document Center**: Downloadable markdown reports (`Independent_Model_Validation_Report.md`, `Explainable_AI_Report.md`, `Stress_Testing_Report.md`, `Model_Monitoring_Report.md`, `Model_Cards.md`).

---

## 3. Local Execution & Enterprise Deployment Instructions

### Local Execution Command
To launch the Streamlit application locally:
```bash
streamlit run dashboard/app.py
```
The application will open automatically in your browser at `http://localhost:8501`.

### Production Deployment & Containerization
For institutional deployment behind corporate firewalls:
1. **Docker Containerization**: Use official `python:3.11-slim` image, copy repository code, and expose port `8501`.
2. **Reverse Proxy**: Configure NGINX reverse proxy with SSL/TLS termination (`https://credit-risk-analytics.bank.internal`).
3. **Authentication**: Integrate OAuth2 / Active Directory single sign-on (SSO) at reverse proxy level.
