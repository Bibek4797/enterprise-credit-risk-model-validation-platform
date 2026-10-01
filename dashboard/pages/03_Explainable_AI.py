"""Page 03: Explainable AI & FCRA Adverse Action Engine."""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
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
model_engine = st.radio(
    "Select Model Explainability Architecture:",
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
        "📊  Scorecard Bin Points Inspector",
        "👤  Individual Borrower Underwriting & FCRA Adverse Action",
    ])

    with tab_inspect:
        label("Scorecard Bin Points Inspector")
        st.caption("Select a risk feature and bin to view its assigned score and maximum attainable score:")

        c_feat, c_bin = st.columns(2)
        with c_feat:
            sel_feat = st.selectbox("Select Risk Feature to Inspect", list(woe_maps.keys()))
        with c_bin:
            feat_sub = scorecard_df[scorecard_df["feature"] == sel_feat]
            sel_bin = st.selectbox("Select Bin Range", feat_sub["bin"].tolist())

        bin_row = feat_sub[feat_sub["bin"] == sel_bin].iloc[0]
        bin_score = int(bin_row["score_points"])
        max_pts_feat = int(feat_sub["score_points"].max())

        c1, c2 = st.columns(2)
        with c1:
            render_kpi_card("Selected Bin Score", f"{bin_score} pts", icon="🎯")
        with c2:
            render_kpi_card("Maximum Score for Feature", f"{max_pts_feat} pts", icon="⭐")

    with tab_borrower:
        label("Individual Borrower Underwriting & FCRA Adverse Action")
        borrower_idx = st.number_input(
            "Select Borrower Index for Individual Evaluation",
            min_value=0,
            max_value=len(df) - 1,
            value=0,
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
        total_score = fcra_res["total_score"]
        is_approved = fcra_res["is_approved"]

        if is_approved:
            st.success(
                f"✅ **Loan Application ACCEPTED** — Credit Score: **{total_score} pts** "
                f"(Meets or exceeds 600-point Underwriting Cutoff)"
            )
        else:
            st.error(
                f"❌ **Loan Application REJECTED** — Credit Score: **{total_score} pts** "
                f"(Below 600-point Underwriting Cutoff)"
            )
            st.markdown("#### 📋 FCRA Adverse Action Notice — Top 4 Key Factors Behind Decline")
            st.caption(
                "Ranked by Points Lost: $\\text{Points Lost}_j = \\text{MaxScore}_j - \\text{ActualScore}_{i, j}$"
            )

            top_4_lag = fcra_res["top_4_lagging"]

            # Clean horizontal bar chart
            fig_lag = px.bar(
                top_4_lag,
                x="points_lag",
                y="description",
                orientation="h",
                labels={"points_lag": "Points Lost (Deficit from Max)", "description": "FCRA Adverse Reason"},
                color="points_lag",
                color_continuous_scale=[[0, "#f59e0b"], [1, "#ef4444"]],
            )
            fig_lag.update_layout(
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
                height=260,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_lag, use_container_width=True)

            display_fcra_df = top_4_lag[[
                "reason_code", "feature", "raw_value", "points_earned",
                "max_possible_points", "points_lag", "description"
            ]].rename(columns={
                "reason_code": "Reason Code",
                "feature": "Risk Driver",
                "raw_value": "Applicant Value",
                "points_earned": "Actual Score",
                "max_possible_points": "Max Score",
                "points_lag": "Points Lost",
                "description": "FCRA Adverse Action Description",
            })
            render_styled_table(display_fcra_df)

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
        label("Local Individual Borrower TreeSHAP Inspector")
        borrower_idx = st.number_input(
            "Select Borrower Index for LightGBM Individual Evaluation",
            min_value=0,
            max_value=len(df) - 1,
            value=0,
            step=1,
        )

        borrower_row = df.iloc[borrower_idx]
        lgb_pred_pd = float(models["predict_lgb"](df.iloc[[borrower_idx]])[0])
        baseline_pd = float(np.mean(df["target"]))
        deviation_pct = lgb_pred_pd - baseline_pd
        cutoff = 0.20
        is_lgb_approved = bool(lgb_pred_pd <= cutoff)

        if is_lgb_approved:
            st.success(
                f"✅ **Loan Application ACCEPTED** — Predicted PD: **{lgb_pred_pd:.2%}** "
                f"(Cutoff: {cutoff:.2%} | Deviation from Baseline: **{deviation_pct:+.2%}**)"
            )
        else:
            st.error(
                f"❌ **Loan Application REJECTED** — Predicted PD: **{lgb_pred_pd:.2%}** "
                f"(Exceeds {cutoff:.2%} Cutoff | Deviation from Baseline: **{deviation_pct:+.2%}**)"
            )
            st.markdown("#### 📋 Local TreeSHAP Adverse Attribution — Top 4 Risk Drivers")
            st.caption(
                "Features causing the greatest increase in default probability (+log-odds push towards default risk):"
            )

            # Compute TreeSHAP values for this applicant
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

            # Sort descending by SHAP value (highest positive risk push)
            local_shap_df = pd.DataFrame(local_records).sort_values("shap_value", ascending=False).reset_index(drop=True)
            top_4_shap = local_shap_df.head(4)

            fig_local_shap = px.bar(
                top_4_shap,
                x="shap_value",
                y="description",
                orientation="h",
                labels={"shap_value": "SHAP Impact (+log-odds)", "description": "Top Lagging Risk Driver"},
                color="shap_value",
                color_continuous_scale=[[0, "#f59e0b"], [1, "#ef4444"]],
            )
            fig_local_shap.update_layout(
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
                height=260,
                margin=dict(l=10, r=10, t=10, b=10),
            )
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
