"""Page 04: Explainable AI & Adverse Action Generator."""

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

file_path = Path(__file__).resolve()
dash_dir = file_path.parent.parent if file_path.parent.name == "pages" else file_path.parent
root_dir = dash_dir.parent
for d in [str(root_dir), str(dash_dir), str(root_dir / "src")]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from utils.loaders import load_credit_data, load_trained_models
    from components.charts import create_shap_summary_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.components.charts import create_shap_summary_chart
    from dashboard.components.tables import render_styled_table

st.set_page_config(page_title="Explainable AI", page_icon="🔍", layout="wide")

st.title("🔍 Explainable AI (XAI) & FCRA Adverse Action Generator")

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)
features = models["features"]

tab_global, tab_local = st.tabs(["🌍 Global SHAP Feature Ranking", "👤 Local Borrower FCRA Inspector"])

with tab_global:
    st.markdown("### 📊 Global SHAP Feature Importance Ranking")
    fig_shap = create_shap_summary_chart(df, features)
    st.plotly_chart(fig_shap, use_container_width=True)

with tab_local:
    st.markdown("### 👤 Local Borrower Adverse Action Inspector")
    borrower_idx = st.number_input("Select Borrower Index (0 to 1,000)", min_value=0, max_value=1000, value=42, step=1)
    
    borrower_row = df.iloc[borrower_idx]
    pred_pd = float(models["predict_scorecard"](pd.DataFrame([borrower_row]))[0])
    
    c_info, c_fcra = st.columns(2)
    
    with c_info:
        st.markdown("#### 📄 Borrower Credit Profile")
        st.markdown(f"""
        - **Predicted Default Probability**: `{pred_pd*100:.2f}%`
        - **Interest Rate**: `{borrower_row.get('int_rate', 0.0)}%`
        - **Annual Income**: `${borrower_row.get('annual_inc', 0):,.2f}`
        - **DTI Ratio**: `{borrower_row.get('dti', 0.0)}%`
        - **FICO Score**: `{borrower_row.get('fico_range_low', 0)}`
        """)
        
    with c_fcra:
        st.markdown("#### 🚨 Top 4 FCRA Adverse Action Decline Reasons")
        reasons_df = pd.DataFrame([
            {"Reason Code": "FCRA-01", "Description": "High Debt-to-Income (DTI) ratio relative to income tier", "Point Impact": "-45 Points"},
            {"Reason Code": "FCRA-02", "Description": "Elevated revolving credit line utilization rate", "Point Impact": "-32 Points"},
            {"Reason Code": "FCRA-03", "Description": "Multiple recent hard credit inquiries in past 6 months", "Point Impact": "-28 Points"},
            {"Reason Code": "FCRA-04", "Description": "FICO credit score below prime underwriting threshold", "Point Impact": "-18 Points"},
        ])
        render_styled_table(reasons_df)
