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
if "beta_0" in models and "beta_dict" in models:
    beta_0 = float(models["beta_0"])
    beta_dict = dict(models["beta_dict"])
elif hasattr(model_res, "params"):
    beta_0 = float(model_res.params["const"]) if "const" in model_res.params else float(np.log(df["target"].mean() / (1.0 - df["target"].mean() + 1e-9)))
    beta_dict = {col: float(model_res.params[col]) for col in model_res.params.index if col != "const"}
else:
    beta_0 = float(getattr(model_res.m, "intercept_", [0.0])[0])
    beta_dict = {col: float(coef) for col, coef in zip(model_res.cols, model_res.m.coef_[0])}

# Guarantee dual key lookup (both "int_rate" and "int_rate_woe")
for feat in woe_maps.keys():
    clean_k = feat.replace("_woe", "")
    w_k = f"{clean_k}_woe"
    if w_k in beta_dict and clean_k not in beta_dict:
        beta_dict[clean_k] = beta_dict[w_k]
    elif clean_k in beta_dict and w_k not in beta_dict:
        beta_dict[w_k] = beta_dict[clean_k]

# Scorecard scaling parameters
PDO = 20.0
TARGET_SCORE = 600.0
TARGET_ODDS = 50.0
FACTOR = PDO / np.log(2.0)
OFFSET = TARGET_SCORE - (FACTOR * np.log(TARGET_ODDS))
NUM_FEATURES = len(woe_maps)

# Build scorecard points table across all 29 features using exact Siddiqi formula
scorecard_df = build_scorecard_points_table(
    woe_maps=woe_maps,
    beta_0=beta_0,
    beta_dict=beta_dict,
    pdo=PDO,
    target_score=TARGET_SCORE,
    target_odds=TARGET_ODDS,
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
        label("Scorecard Bin Points Inspector (All 29 Risk Features)")
        st.caption("Select any feature and risk bin to view its assigned score and maximum attainable score:")

        c_feat, c_bin = st.columns(2)
        with c_feat:
            # Sorted list of all 29 risk features
            all_feats = sorted(list(woe_maps.keys()))
            sel_feat = st.selectbox("Select Risk Feature to Inspect (29 Features Available)", all_feats)
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

        # Watermark Parameter Callout Container
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(59, 130, 246, 0.25); border-radius: 8px; padding: 14px 18px; margin-top: 24px;">
                <div style="font-weight: 600; color: #60a5fa; font-size: 0.90rem; margin-bottom: 8px;">
                    📐 Regulatory Scorecard Calibration Parameters (Siddiqi Basel Framework)
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; font-size: 0.85rem; color: #cbd5e1;">
                    <div><strong>• Points to Double Odds (PDO):</strong> {PDO:.1f} pts</div>
                    <div><strong>• Factor:</strong> PDO / ln(2) = {FACTOR:.4f}</div>
                    <div><strong>• Target Benchmark:</strong> {TARGET_SCORE:.0f} pts @ {TARGET_ODDS:.0f}:1 Odds</div>
                    <div><strong>• Calibrated Offset:</strong> TargetScore − Factor × ln(TargetOdds) = {OFFSET:.3f}</div>
                    <div><strong>• Model Risk Drivers (m):</strong> {NUM_FEATURES} Features</div>
                </div>
                <div style="margin-top: 8px; font-size: 0.80rem; color: #94a3b8; font-style: italic;">
                    Score formula per bin: Points<sub>j, k</sub> = [(Offset / m − Factor × β<sub>0</sub> / m) − (Factor × β<sub>j</sub> × WoE<sub>j, k</sub>)]
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

            top_4_lag = fcra_res["top_4_lagging"].copy()

            def _fmt_val(v):
                if pd.isna(v):
                    return "N/A"
                try:
                    fv = float(v)
                    return f"{int(fv)}" if fv.is_integer() else f"{fv:.2f}"
                except (ValueError, TypeError):
                    return str(v)

            top_4_lag["raw_value"] = top_4_lag["raw_value"].apply(_fmt_val)

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
        st.caption("Calculates Mean |SHAP| values across the portfolio to evaluate macro risk drivers per SR 11-7.")
        try:
            sample_X = df[features].head(250).copy()
            for c in sample_X.select_dtypes(include=["object"]).columns:
                sample_X[c] = sample_X[c].astype("category")
            explainer = shap.TreeExplainer(models["lgb_dict"]["model"])
            vals = explainer.shap_values(sample_X)
            if isinstance(vals, list) and len(vals) > 1:
                shap_mat = vals[1]
            elif hasattr(vals, "ndim") and vals.ndim == 3:
                shap_mat = vals[:, :, 1]
            else:
                shap_mat = vals
            mean_abs = np.mean(np.abs(shap_mat), axis=0)
            ranking_df = pd.DataFrame({
                "feature": features,
                "mean_abs_shap": np.round(mean_abs, 4),
            }).sort_values("mean_abs_shap", ascending=False).reset_index(drop=True)
            fig_shap = create_shap_summary_chart(ranking_df)
        except Exception:
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
            row_X = df[features].copy().iloc[[borrower_idx]]
            for col in row_X.select_dtypes(include=["object"]).columns:
                row_X[col] = row_X[col].astype("category")

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
                labels={"shap_value": "SHAP Impact (+log-odds)", "description": "Top Adverse Risk Driver"},
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
