# User Operating Guide — Credit Risk Analytics Platform

**Document Control & End-User Operating Manual**
- **System Scope**: End-User Dashboard & Portfolio Analytics Manual
- **Target Audience**: Credit Underwriters, Portfolio Risk Managers, Model Validation Analysts
- **Author**: Quantitative Software Engineering & UX Team

---

## 1. System Access & Streamlit Interface Overview

The **Enterprise Credit Risk Analytics Platform** is accessed via web browser at `http://localhost:8501`.

### Navigation Pages
1. **Executive Dashboard (`1_Executive_Dashboard.py`)**: High-level portfolio KPIs, total exposure ($), empirical default rate, and traffic light health status banner.
2. **Portfolio Analytics (`2_Portfolio_Analytics.py`)**: Interactive sidebar filtering by Risk Grade (A–G), State, Purpose, FICO score, and Loan Amount. Displays vintage default seasoning curves and Herfindahl-Hirschman Concentration Index ($\text{HHI} = 584.2$).
3. **Model Performance (`3_Model_Performance.py`)**: Champion Scorecard vs Challenger LightGBM ROC curves and interactive probability cutoff slider ($0.05$ to $0.50$).
4. **Explainable AI (`4_Explainable_AI.py`)**: Global SHAP feature rankings and local borrower inspector with automated FCRA Adverse Action reason codes.
5. **Stress Testing (`5_Stress_Testing.py`)**: Macro Adverse and Macro Severe Adverse scenario simulator computing real-time $\Delta \text{PD}$ and $\Delta \text{EL}$.
6. **Model Monitoring (`6_Model_Monitoring.py`)**: Population Stability Index ($\text{PSI}$), Characteristic Stability Index ($\text{CSI}$), and KS data drift tables.
7. **Deep Learning Benchmark (`7_Deep_Learning_Benchmark.py`)**: Triangulation benchmark comparison matrix documenting the rejection of neural networks for origination.
8. **Reports (`8_Reports.py`)**: Governance document repository and downloadable markdown reports.
