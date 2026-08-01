"""Page 3: Model Performance."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from utils.data_loader import load_credit_data
from utils.model_loader import load_trained_models
from components.charts import create_roc_curves_chart
from components.tables import render_styled_table
from validation.model_metrics import evaluate_binary_model

st.set_page_config(page_title="Model Performance", page_icon="🎯", layout="wide")

st.title("🎯 Champion vs Challenger Model Performance")

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)

# Predictions
scorecard_probs = models["predict_scorecard"](df)
lgb_probs = models["predict_lgb"](df)

prob_dict = {
    "Champion Scorecard (Logistic)": scorecard_probs,
    "Challenger (LightGBM)": lgb_probs,
}

col_chart, col_table = st.columns([1.4, 1])

with col_chart:
    fig_roc = create_roc_curves_chart(df["target"].values, prob_dict)
    st.plotly_chart(fig_roc, use_container_width=True)

with col_table:
    st.markdown("### 📋 Master Performance Comparison")
    sc_metrics = evaluate_binary_model(df["target"].values, scorecard_probs)
    lgb_metrics = evaluate_binary_model(df["target"].values, lgb_probs)

    comp_df = pd.DataFrame([
        {
            "Model Name": "Champion Scorecard (Logistic)",
            "ROC-AUC": sc_metrics["roc_auc"],
            "Gini Index": sc_metrics["gini_index"],
            "KS Stat (%)": sc_metrics["ks_statistic_pct"],
            "Brier Score": sc_metrics["brier_score"],
            "Inference Latency": "0.5 ms",
        },
        {
            "Model Name": "Challenger (LightGBM)",
            "ROC-AUC": lgb_metrics["roc_auc"],
            "Gini Index": lgb_metrics["gini_index"],
            "KS Stat (%)": lgb_metrics["ks_statistic_pct"],
            "Brier Score": lgb_metrics["brier_score"],
            "Inference Latency": "4.1 ms",
        },
    ])
    render_styled_table(comp_df)

st.markdown("---")

# Interactive Threshold Slider
st.markdown("### 🎚️ Interactive Classification Threshold Cutoff Simulator")
cutoff = st.slider("Select Probability Approval Threshold Cutoff", min_value=0.05, max_value=0.50, value=0.20, step=0.01)

scorecard_preds = (scorecard_probs >= cutoff).astype(int)
lgb_preds = (lgb_probs >= cutoff).astype(int)

sc_approved = float(np.mean(scorecard_preds == 0)) * 100.0
sc_def_in_app = float(np.mean(df.loc[scorecard_preds == 0, "target"] == 1)) * 100.0 if any(scorecard_preds == 0) else 0.0

lgb_approved = float(np.mean(lgb_preds == 0)) * 100.0
lgb_def_in_app = float(np.mean(df.loc[lgb_preds == 0, "target"] == 1)) * 100.0 if any(lgb_preds == 0) else 0.0

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Scorecard Approval Rate", f"{sc_approved:.2f}%")
with c2:
    st.metric("Scorecard Default in Approved", f"{sc_def_in_app:.2f}%")
with c3:
    st.metric("LightGBM Approval Rate", f"{lgb_approved:.2f}%")
with c4:
    st.metric("LightGBM Default in Approved", f"{lgb_def_in_app:.2f}%")
