"""Page 4: Explainable AI (XAI)."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from utils.data_loader import load_credit_data
from utils.model_loader import load_trained_models
from components.charts import create_shap_summary_bar_chart
from components.tables import render_styled_table
from explainability.shap_analysis import compute_global_shap, explain_local_borrower

st.set_page_config(page_title="Explainable AI", page_icon="🔍", layout="wide")

st.title("🔍 Explainable AI (XAI) & Model Transparency")

df = load_credit_data(sample_size=10000)
models = load_trained_models(df)

# Global SHAP Analysis
feature_cols = models["features"]
shap_res = compute_global_shap(models["lgb_dict"]["model"], df[feature_cols])

left_col, right_col = st.columns([1.3, 1])

with left_col:
    fig_shap = create_shap_summary_bar_chart(shap_res["ranking_table"])
    st.plotly_chart(fig_shap, use_container_width=True)

with right_col:
    st.markdown("### 📋 Global SHAP Feature Rankings")
    render_styled_table(shap_res["ranking_table"].head(10))

st.markdown("---")

# Interactive Local Borrower Selector & FCRA Adverse Action Generator
st.markdown("### 👤 Local Borrower Attribution & FCRA Adverse Action Generator")
borrower_idx = st.number_input("Select Borrower Index (0 to 1,000)", min_value=0, max_value=min(1000, len(df)-1), value=0)

local_exp = explain_local_borrower(shap_res["explainer"], shap_res["shap_values"], df[feature_cols], instance_idx=borrower_idx)

b_col1, b_col2 = st.columns([1, 1.2])

with b_col1:
    st.markdown(f"#### Borrower Index #{borrower_idx} Profile")
    st.write(f"**Predicted Log-Odds**: `{local_exp['predicted_log_odds']:.4f}`")
    pred_pd = 1.0 / (1.0 + np.exp(-local_exp['predicted_log_odds']))
    st.write(f"**Predicted Default Probability**: `{pred_pd*100:.2f}%`")
    st.write(f"**Underwriting Status**: `{'DECLINED' if pred_pd >= 0.20 else 'APPROVED'}`")

    st.markdown("##### 📜 FCRA Adverse Action Reason Codes")
    top_pos_shap = local_exp["attribution_table"][local_exp["attribution_table"]["shap_value"] > 0].head(4)
    if not top_pos_shap.empty:
        for idx_r, r in top_pos_shap.iterrows():
            st.markdown(f"- **{r['feature']}** (`val = {r['feature_value']:.2f}`): Pushed default risk higher (+{r['shap_value']:.4f} SHAP).")
    else:
        st.write("No adverse action reasons; borrower meets credit risk standards.")

with b_col2:
    st.markdown("#### Local SHAP Attribution Feature Table")
    render_styled_table(local_exp["attribution_table"].head(10))
