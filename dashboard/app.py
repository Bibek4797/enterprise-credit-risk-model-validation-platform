"""Main Entry Point & Landing Page for Enterprise Credit Risk Analytics Platform."""

import os
import sys
from pathlib import Path
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Enterprise Credit Risk Analytics Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load CSS Stylesheet
styles_path = Path.cwd() / "dashboard" / "assets" / "styles.css"
if styles_path.is_file():
    with open(styles_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Custom Banner Header
st.markdown("""
<div class="main-header">
    <h1>🏦 Enterprise Credit Risk Analytics & Model Governance Platform</h1>
    <p>Independent Model Validation, Portfolio Risk Monitoring, Stress Testing & XAI Governance Suite</p>
</div>
""", unsafe_allow_html=True)

# Welcome Overview Card
st.markdown("""
### Welcome to the Institutional Credit Risk Analytics Platform
This multi-page enterprise application serves **Credit Risk Analytics**, **Portfolio Management**, **Model Risk Management (MRM)**, **Independent Model Validation**, and **Executive Risk Committees**.

---

### 📌 Navigation Sitemaps & Available Pages
Use the sidebar on the left to navigate across the 8 specialized analytics modules:

1. **📊 Executive Dashboard**: Macro portfolio KPI metrics, Exposure summaries, Traffic Light Risk Status, and Executive Overview.
2. **📈 Portfolio Analytics**: Interactive filtering, Risk Grade segmentation, Geographic State Concentration (HHI Index), Vintage seasoning curves, and Recovery Rate analysis.
3. **🎯 Model Performance**: Champion (Logistic Scorecard) vs Challenger (LightGBM) discrimination, ROC-AUC, KS, Gini, Calibration curves, and interactive classification threshold slider.
4. **🔍 Explainable AI (XAI)**: Global SHAP feature rankings, local borrower attributions, interactive borrower selector, and FCRA Adverse Action reason codes.
5. **⚡ Stress Testing**: Interactive scenario simulator (adjusting Income, Interest Rate, Loan Amount, DTI, FICO, Utilization) displaying real-time $\Delta \text{PD}$ shift, expected loss ($\Delta \text{EL}$), and grade migration.
6. **🛡️ Model Monitoring**: Population Stability Index ($\text{PSI}$), Characteristic Stability Index ($\text{CSI}$), KS Data Drift, Concept Drift, and automated retraining triggers.
7. **🤖 Deep Learning Benchmark**: Triangulation benchmark comparing Scorecard vs LightGBM vs PyTorch MLP across 9 evaluation dimensions.
8. **📄 Governance Reports**: Document repository providing downloadable reports, Model Cards, and audit documentation.
""")

st.info("👈 Please select a page from the sidebar to launch the analytics suite.")
