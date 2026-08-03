"""Page 03: Model Performance."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path.cwd()))
sys.path.append(str(Path.cwd() / "dashboard"))

from utils.loaders import load_credit_data, load_trained_models
from components.charts import create_roc_curve_chart
from components.tables import render_styled_table
from validation.model_metrics import evaluate_binary_model

st.set_page_config(page_title="Model Performance", page_icon="🎯", layout="wide")

st.title("🎯 Champion vs Challenger Model Discrimination")

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)

# Predictions
y_true = df["target"].values
sc_probs = models["predict_scorecard"](df)
lgb_probs = models["predict_lgb"](df)

col_chart, col_metrics = st.columns([1.5, 1])

with col_chart:
    st.markdown("### 📈 Out-of-Time Receiver Operating Characteristic (ROC) Curves")
    fig_roc = create_roc_curve_chart(y_true, sc_probs, lgb_probs)
    st.plotly_chart(fig_roc, use_container_width=True)

with col_metrics:
    st.markdown("### 📋 Statistical Discrimination Metrics")
    sc_m = evaluate_binary_model(y_true, sc_probs)
    lgb_m = evaluate_binary_model(y_true, lgb_probs)

    metrics_df = pd.DataFrame([
        {
            "Model Architecture": "Champion Logistic Scorecard (PD-SCORECARD-2026-V1)",
            "OOT ROC-AUC": sc_m["roc_auc"],
            "Gini Index": sc_m["gini_index"],
            "KS Stat (%)": sc_m["ks_statistic_pct"],
            "Brier Score": sc_m["brier_score"],
        },
        {
            "Model Architecture": "Challenger LightGBM (PD-LIGHTGBM-2026-CHALLENGER)",
            "OOT ROC-AUC": lgb_m["roc_auc"],
            "Gini Index": lgb_m["gini_index"],
            "KS Stat (%)": lgb_m["ks_statistic_pct"],
            "Brier Score": lgb_m["brier_score"],
        },
    ])
    render_styled_table(metrics_df)

st.markdown("---")

# Cutoff Threshold Simulator
st.markdown("### 🎛️ Interactive Score Cutoff Threshold Simulator")

cutoff_val = st.slider("Select Probability Cutoff Threshold (PD)", min_value=0.05, max_value=0.50, value=0.20, step=0.01)

approved_mask = sc_probs <= cutoff_val
approval_rate = (np.sum(approved_mask) / len(sc_probs)) * 100.0
approved_def_rate = (np.mean(y_true[approved_mask]) * 100.0) if np.sum(approved_mask) > 0 else 0.0

m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Selected Cutoff PD", f"{cutoff_val:.2f}")
with m2:
    st.metric("Applicant Approval Yield", f"{approval_rate:.2f}%")
with m3:
    st.metric("Approved Population Default Rate", f"{approved_def_rate:.2f}%", delta=f"{approved_def_rate - (np.mean(y_true)*100):+.2f}%", delta_color="inverse")
