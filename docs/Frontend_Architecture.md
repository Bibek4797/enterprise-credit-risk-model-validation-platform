# Streamlit Frontend Architecture & Standardization Blueprint

**Document Control & UI/UX Software Engineering**
- **System Scope**: Pure Python + Streamlit Multi-Page Frontend Architecture & Standardization Manual
- **Target Audience**: Quantitative Software Engineers, Lead Architects, Maintainers
- **Template Application**: Standardized UI Template for Enterprise Credit Risk & Q-RiskNet Projects
- **Author**: Quantitative Software Engineering & Frontend Architecture Team

---

## 1. Architecture Overview & Pure-Python Design Philosophy

The **Enterprise Credit Risk Analytics Platform** implements a **100% Pure Python + Streamlit** frontend architecture.

### Core Principles
1. **Zero External SPA Frameworks**: Excludes React, Next.js, Vue, Angular, or complex JavaScript build tools, eliminating Node.js npm dependency bloat.
2. **Modular Reusable Design**: Component-based directory layout (`dashboard/components/`, `dashboard/utils/`) separating UI cards, Plotly charts, filters, tables, and cached data loaders.
3. **Optimized Caching & Zero-Rerun Latency**: Leverages `@st.cache_data` for data transformations and `@st.cache_resource` for model weights.
4. **Standard Template for Future Risk Projects**: Serves as the standardized architecture blueprint for all quantitative risk platforms (including Q-RiskNet India).

---

## 2. Directory Layout & Subsystem Blueprint

```
dashboard/
├── app.py                         # Main Entry Point & Landing Page
├── assets/
│   ├── logo.png                   # Institutional Logo Asset
│   └── styles.css                 # Enterprise CSS Theme & Card Styles
├── config/
│   ├── constants.py               # KPI Benchmarks & Target Limits
│   └── theme.py                   # Plotly Theme & Color Palettes
├── components/
│   ├── cards.py                   # Metric Cards & Traffic Light Banners
│   ├── charts.py                  # Reusable Plotly Chart Generators
│   ├── filters.py                 # Multi-variate Sidebar Filter Controls
│   ├── metrics.py                 # High-density Portfolio Metrics
│   ├── sidebar.py                 # Sidebar Navigation & Branding
│   └── tables.py                  # Styled DataTables & Export Controls
├── utils/
│   ├── export.py                  # Report Exporter & CSV Download Utilities
│   ├── loaders.py                 # Cached Data & Model Loaders (@st.cache_data / @st.cache_resource)
│   ├── plotting.py                # Plotly Styling & Layout Utilities
│   └── theme.py                   # Streamlit Theme Helpers
└── pages/
    ├── 01_Executive_Dashboard.py  # Portfolio KPIs & Health Banner
    ├── 02_Portfolio_Analytics.py  # Dynamic Filters, HHI Index & Seasoning
    ├── 03_Model_Performance.py    # Champion vs Challenger ROC & Threshold Slider
    ├── 04_Explainable_AI.py      # Global SHAP, Local Inspector & FCRA Reason Codes
    ├── 05_Stress_Testing.py      # Macro Scenario Simulator & Delta EL
    ├── 06_Model_Monitoring.py    # PSI, CSI, KS Data Drift & Retraining Triggers
    ├── 07_Model_Validation.py    # Independent Model Validation Audit & CIs
    └── 08_Documentation.py       # Governance Reports Center & Downloadable Audits
```

---

## 3. Reusable Components & Caching Strategy

### 3.1 Caching Architecture (`dashboard/utils/loaders.py`)
- **Data Caching (`@st.cache_data(ttl=3600)`)**: Caches processed dataframes in memory, avoiding disk I/O on page navigation.
- **Model Resource Caching (`@st.cache_resource(ttl=7200)`)**: Loads binary model pipeline weights once into memory across user sessions.

### 3.2 UI Component Libraries
- **KPI Cards (`components/cards.py`)**: Standardized metric cards with optional traffic light indicator badges (`GREEN` / `YELLOW` / `RED`).
- **Plotly Styling (`utils/plotting.py`)**: Applies uniform Dark Slate theme (`#0F172A`), inter-line typography, and responsive hover cards.
- **Multi-Variate Filters (`components/filters.py`)**: Shared sidebar filter controls returning filtered DataFrames to child pages.
