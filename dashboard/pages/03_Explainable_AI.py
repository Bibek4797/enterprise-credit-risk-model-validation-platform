"""Page 03: Explainable AI & FCRA Adverse Action Engine."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import shap

file_path = Path(__file__).resolve()
dash_dir = file_path.parent.parent if file_path.parent.name == "pages" else file_path.parent
root_dir = dash_dir.parent
for d in [str(root_dir), str(dash_dir), str(root_dir / "src")]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from utils.loaders import load_credit_data, load_trained_models
    from utils.ui_helpers import page_header, section_divider, label
    from components.cards import render_kpi_card
    from components.charts import create_shap_summary_chart
    from components.tables import render_styled_table
except ImportError:
    from dashboard.utils.loaders import load_credit_data, load_trained_models
    from dashboard.utils.ui_helpers import page_header, section_divider, label
    from dashboard.components.cards import render_kpi_card
    from dashboard.components.charts import create_shap_summary_chart
    from dashboard.components.tables import render_styled_table

try:
    from explainability.adverse_action import (
        REASON_CODE_MAPPING,
        build_scorecard_points_table,
        evaluate_borrower_scorecard_fcra,
    )
except ImportError:
    from src.explainability.adverse_action import (
        REASON_CODE_MAPPING,
        build_scorecard_points_table,
        evaluate_borrower_scorecard_fcra,
    )

st.set_page_config(page_title="Explainable AI | Credit Risk Platform", page_icon="🔍", layout="wide")

page_header(
    "🔍  Explainable AI (XAI) & FCRA Adverse Action Engine",
    "SR 11-7 · FCRA · ECOA — Dual-Engine Scorecard & TreeSHAP Transparency",
)

df = load_credit_data(sample_size=30000)
models = load_trained_models(df)
features = models["features"]
woe_maps = models["woe_maps"]
logit_dict = models["logit_dict"]
model_res = logit_dict["model_result"]

# Extract logistic regression parameters
if hasattr(model_res, "params"):
    beta_0 = float(model_res.params["const"])
    beta_dict = {col: float(model_res.params[col]) for col in model_res.params.index if col != "const"}
else:
    beta_0 = float(model_res.m.intercept_[0])
    beta_dict = {f"{c}_woe": float(w) for c, w in zip(model_res.cols, model_res.m.coef_[0])}

# Build scorecard points table using exact Siddiqi / Basel formula
scorecard_df = build_scorecard_points_table(
    woe_maps=woe_maps,
    beta_0=beta_0,
    beta_dict=beta_dict,
    pdo=20.0,
    target_score=600.0,
    target_odds=50.0,
)

# ── Model Engine Selector ──────────────────────────────────────
st.markdown("### 🎛️ Select Model Explainability Architecture")
model_engine = st.radio(
    "Choose between the Regulatory Additive Scorecard or Gradient Boosted TreeSHAP:",
    [
        "Champion Scorecard (Logistic Regression — Additive Bin Points)",
        "Challenger LightGBM (TreeSHAP Feature Attribution)",
    ],
    horizontal=True,
)

section_divider()

# ==============================================================================
# OPTION 1: CHAMPION SCORECARD (LOGISTIC REGRESSION)
# ==============================================================================
if model_engine.startswith("Champion"):
    tab_inspect, tab_borrower = st.tabs([
        "📊  Scorecard Points Matrix & Bin Inspector",
        "👤  Individual Borrower Underwriting & FCRA Adverse Action",
    ])

    with tab_inspect:
        label("Interactive Scorecard Bin Points Inspector (Siddiqi Scorecard Scaling)")
        st.caption(
            "Points formula: Points_{j,k} = [ (Offset / m - Factor * beta_0 / m) - (Factor * beta_j * WoE_{j,k}) ]  "
            "|  PDO = 20 pts  |  Target Score = 600 pts @ 50:1 Odds"
        )

        c_feat, c_bin = st.columns(2)
        with c_feat:
            sel_feat = st.selectbox("Select Risk Feature to Inspect", list(woe_maps.keys()))
        with c_bin:
            feat_sub = scorecard_df[scorecard_df["feature"] == sel_feat]
            sel_bin = st.selectbox("Select Bin Range", feat_sub["bin"].tolist())

        bin_row = feat_sub[feat_sub["bin"] == sel_bin].iloc[0]
        max_pts_feat = int(feat_sub["score_points"].max())
        pts_deficit = max_pts_feat - int(bin_row["score_points"])

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            render_kpi_card("Selected Bin Points", f"{int(bin_row['score_points'])} pts", icon="🎯")
        with c2:
            render_kpi_card("Bin WoE Value", f"{bin_row['woe']:+.4f}", icon="📐")
        with c3:
            render_kpi_card("Max Possible Feature Points", f"{max_pts_feat} pts", icon="⭐")
        with c4:
            render_kpi_card("Points Deficit from Max", f"-{pts_deficit} pts", icon="📉", is_positive_good=(pts_deficit == 0))

        st.markdown(f"#### Score Distribution across Bins for `{sel_feat}`")
        fig_feat = px.bar(
            feat_sub,
            x="bin",
            y="score_points",
            labels={"bin": "Risk Bin Range", "score_points": "Scorecard Points"},
            color="score_points",
            color_continuous_scale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1.0, "#10b981"]],
        )
        fig_feat.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_feat, use_container_width=True)

        with st.expander("📋 View Complete Credit Risk Scorecard Points Table (All Bins)"):
            render_styled_table(scorecard_df)

    with tab_borrower:
        label("Individual Borrower Underwriting Evaluation & FCRA Audit")
        borrower_idx = st.number_input(
            "Select Borrower Index for Individual Evaluation",
            min_value=0,
            max_value=len(df) - 1,
            value=42,
            step=1,
        )

        borrower_row = df.iloc[borrower_idx]
        fcra_res = evaluate_borrower_scorecard_fcra(
            borrower_row=borrower_row,
            scorecard_df=scorecard_df,
            woe_maps=woe_maps,
            approval_threshold=600,
            top_n=4,
        )
        sc_pd = float(models["predict_scorecard"](df.iloc[[borrower_idx]])[0])
        total_score = fcra_res["total_score"]
        is_approved = fcra_res["is_approved"]

        cb1, cb2, cb3, cb4 = st.columns(4)
        with cb1:
            render_kpi_card("Total Credit Score", f"{total_score} pts", icon="💳")
        with cb2:
            status_text = "APPROVED" if is_approved else "REJECTED"
            render_kpi_card("Underwriting Decision", status_text, icon="✅" if is_approved else "❌", is_positive_good=is_approved)
        with cb3:
            render_kpi_card("Predicted PD (Scorecard)", f"{sc_pd:.2%}", icon="📊", is_positive_good=is_approved)
        with cb4:
            render_kpi_card("FICO / DTI", f"{int(borrower_row.get('fico_range_low', 700))} / {borrower_row.get('dti', 15.0):.1f}%", icon="⚖️")

        section_divider()

        top_4_lag = fcra_res["top_4_lagging"]

        if not is_approved:
            st.error(
                f"❌ **Loan Application REJECTED** (Score: {total_score} pts < 600-point Underwriting Cutoff). "
                "Per the Fair Credit Reporting Act (FCRA Section 615(a)), the applicant must be provided with the "
                "top 4 key factors that adversely affected their credit score."
            )
            st.markdown("### 📋 FCRA Adverse Action Notice — Top 4 Key Lagging Factors")
            st.caption(
                "Lagging factors are ranked by **Score Points Deficit**: [ Max Possible Feature Points - Points Earned by Applicant ]."
            )
        else:
            st.success(
                f"✅ **Loan Application APPROVED** (Score: {total_score} pts ≥ 600-point Underwriting Cutoff). "
                "Below are the top 4 opportunity areas where the borrower's score had the highest point deficits."
            )
            st.markdown("### 📋 Underwriting Risk Attribution — Top 4 Point Deficits")

        # Horizontal Bar Chart of Points Deficit
        fig_lag = px.bar(
            top_4_lag,
            x="points_lag",
            y="description",
            orientation="h",
            labels={"points_lag": "Score Points Deficit (Lag from Maximum Bin)", "description": "FCRA Adverse Reason"},
            color="points_lag",
            color_continuous_scale=[[0, "#f59e0b"], [1, "#ef4444"]],
        )
        fig_lag.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig_lag, use_container_width=True)

        display_fcra_df = top_4_lag[[
            "reason_code", "feature", "raw_value", "assigned_bin",
            "points_earned", "max_possible_points", "points_lag", "description"
        ]].rename(columns={
            "reason_code": "Reason Code",
            "feature": "Risk Driver",
            "raw_value": "Borrower Value",
            "assigned_bin": "Applicant Bin",
            "points_earned": "Score Earned",
            "max_possible_points": "Max Possible",
            "points_lag": "Points Deficit (Lag)",
            "description": "FCRA Adverse Action Description",
        })
        render_styled_table(display_fcra_df)

        with st.expander("🔍 View Complete Feature-by-Feature Scorecard Breakdown"):
            render_styled_table(fcra_res["breakdown"][[
                "feature", "raw_value", "assigned_bin", "points_earned",
                "max_possible_points", "points_lag", "reason_code", "description"
            ]])

# ==============================================================================
# OPTION 2: CHALLENGER LIGHTGBM (TREESHAP)
# ==============================================================================
else:
    tab_global, tab_local = st.tabs([
        "🌍  Global TreeSHAP Feature Ranking",
        "👤  Local Individual Borrower TreeSHAP Inspector",
    ])

    with tab_global:
        label("Global TreeSHAP Feature Importance (Overall Model Drivers)")
        st.caption("Calculates Mean |SHAP| values across the portfolio to evaluate macro risk drivers.")
        fig_shap = create_shap_summary_chart(df, features)
        st.plotly_chart(fig_shap, use_container_width=True)

    with tab_local:
        label("Local Borrower TreeSHAP Attribution (Top 4 Lagging Risk Drivers)")
        borrower_idx = st.number_input(
            "Select Borrower Index for LightGBM Individual Evaluation",
            min_value=0,
            max_value=len(df) - 1,
            value=42,
            step=1,
        )

        borrower_row = df.iloc[borrower_idx]
        lgb_pred_pd = float(models["predict_lgb"](df.iloc[[borrower_idx]])[0])
        is_lgb_approved = bool(lgb_pred_pd <= 0.20)

        cl1, cl2, cl3, cl4 = st.columns(4)
        with cl1:
            render_kpi_card("Predicted PD (LightGBM)", f"{lgb_pred_pd:.2%}", icon="🤖", is_positive_good=is_lgb_approved)
        with cl2:
            status_text = "APPROVED" if is_lgb_approved else "REJECTED"
            render_kpi_card("Underwriting Decision", status_text, icon="✅" if is_lgb_approved else "❌", is_positive_good=is_lgb_approved)
        with cl3:
            render_kpi_card("FICO Score", f"{int(borrower_row.get('fico_range_low', 700))}", icon="📊")
        with cl4:
            render_kpi_card("DTI Ratio", f"{borrower_row.get('dti', 15.0):.2f}%", icon="⚖️")

        section_divider()

        # Compute TreeSHAP values for this specific applicant
        explainer = shap.TreeExplainer(models["lgb_dict"]["model"])
        row_X = df[features].fillna(0).iloc[[borrower_idx]]
        shap_out = explainer.shap_values(row_X)
        row_shap = shap_out[1][0] if isinstance(shap_out, list) else shap_out[0]

        local_records = []
        for feat, s_val in zip(features, row_shap):
            raw_val = borrower_row.get(feat, np.nan)
            code, desc = REASON_CODE_MAPPING.get(feat, (f"{feat.upper()[:4]}-01", f"Risk contribution from {feat}"))
            local_records.append({
                "feature": feat,
                "raw_value": raw_val,
                "shap_value": float(s_val),
                "reason_code": code,
                "description": desc,
            })

        # Sort descending by SHAP value (positive SHAP pushes default probability UP / makes applicant lag)
        local_shap_df = pd.DataFrame(local_records).sort_values("shap_value", ascending=False).reset_index(drop=True)
        top_4_shap = local_shap_df.head(4)

        if not is_lgb_approved:
            st.error(
                f"❌ **Loan Application REJECTED** (Predicted PD: {lgb_pred_pd:.2%} > 20.00% Underwriting Cutoff). "
                "Below are the **Top 4 primary features where this applicant is lagging** (pushing default risk highest):"
            )
        else:
            st.success(
                f"✅ **Loan Application APPROVED** (Predicted PD: {lgb_pred_pd:.2%} ≤ 20.00% Underwriting Cutoff). "
                "Below are the **Top 4 adverse features** that most strongly pushed the applicant's default probability upwards:"
            )

        st.markdown("### 📋 Local TreeSHAP Attribution — Top 4 Adverse Risk Contributors")

        fig_local_shap = px.bar(
            top_4_shap,
            x="shap_value",
            y="description",
            orientation="h",
            labels={"shap_value": "SHAP Impact (+log-odds push towards default)", "description": "Top Lagging Risk Driver"},
            color="shap_value",
            color_continuous_scale=[[0, "#3b82f6"], [1, "#ef4444"]],
        )
        fig_local_shap.update_layout(yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig_local_shap, use_container_width=True)

        display_shap_df = top_4_shap[[
            "reason_code", "feature", "raw_value", "shap_value", "description"
        ]].rename(columns={
            "reason_code": "Reason Code",
            "feature": "Risk Driver",
            "raw_value": "Applicant Value",
            "shap_value": "Adverse SHAP Impact (+log-odds)",
            "description": "FCRA Adverse Action Description",
        })
        render_styled_table(display_shap_df)
