"""Streamlit Application Entry Point for Enterprise Credit Risk Analytics Platform."""

import sys
from pathlib import Path
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

st.set_page_config(
    page_title="Credit Risk Analytics Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏦 Enterprise Credit Risk Analytics & Model Risk Governance Platform")
st.subheader("Tier-1 Banking Model Risk Management (SR 11-7 / Basel III / FCRA / ECOA)")

st.markdown("---")

st.markdown(r"""
### Welcome to the Enterprise Credit Risk Analytics Platform

This multi-page platform provides end-to-end quantitative risk analytics, independent model validation, explainability, stress testing, and real-time model stability monitoring for consumer credit portfolios.

#### 📍 Platform Navigation Guide
1. **📊 Executive Dashboard (`01_Executive_Dashboard.py`)**: High-level portfolio KPIs, exposure, empirical default rate, and Traffic Light health banner.
2. **📈 Portfolio Analytics (`02_Portfolio_Analytics.py`)**: Dynamic multi-variate filters (Grade, State, Purpose, FICO, Loan Amount), origination vintage default seasoning curves, and HHI concentration index.
3. **🎯 Model Performance (`03_Model_Performance.py`)**: Champion Scorecard (`PD-SCORECARD-2026-V1`) vs Challenger LightGBM (`PD-LIGHTGBM-2026-CHALLENGER`) ROC curves and interactive cutoff threshold simulator.
4. **🔍 Explainable AI (`04_Explainable_AI.py`)**: Global SHAP feature rankings, local borrower waterfall attributions, and automated FCRA Adverse Action decline reason codes.
5. **⚡ Stress Testing (`05_Stress_Testing.py`)**: Macro Adverse / Severe Adverse scenarios and interactive stress simulator computing real-time $\Delta \text{PD}$ and $\Delta \text{EL}$.
6. **🛡️ Model Monitoring (`06_Model_Monitoring.py`)**: Population Stability Index ($\text{PSI}$), CSI, KS data drift, and automated retraining status.
7. **🤖 Model Validation (`07_Model_Validation.py`)**: Master benchmark triangulation matrix documenting the governance decision to reject neural networks for origination.
8. **📄 Documentation (`08_Documentation.py`)**: Governance document center with downloadable audit reports.
""")

st.markdown("---")

st.info("👈 Use the left sidebar navigation menu to explore individual analytics modules.")
