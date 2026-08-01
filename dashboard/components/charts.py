"""Reusable Plotly Chart Components for Enterprise Risk Dashboard."""

from __future__ import annotations

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from config.theme import PRIMARY_BLUE, ACCENT_BLUE, SUCCESS_GREEN, DANGER_RED, WARNING_YELLOW, GRADE_COLORS, PLOTLY_THEME


def create_grade_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of loan exposure and count by Risk Grade."""
    grade_counts = df.groupby("grade", observed=False)["loan_amnt"].agg(["count", "sum"]).reset_index()
    grade_counts["exposure_m"] = grade_counts["sum"] / 1e6

    fig = px.bar(
        grade_counts,
        x="grade",
        y="exposure_m",
        color="grade",
        color_discrete_map=GRADE_COLORS,
        title="Portfolio Exposure ($ Millions) by Risk Grade",
        labels={"grade": "Risk Grade", "exposure_m": "Exposure ($M)"},
        text_auto=".1f",
    )
    fig.update_layout(**PLOTLY_THEME["layout"])
    return fig


def create_roc_curves_chart(y_true: np.ndarray, prob_dict: dict[str, np.ndarray]) -> go.Figure:
    """Multi-model ROC Curve Comparison chart."""
    from sklearn.metrics import roc_curve, roc_auc_score

    fig = go.Figure()
    # Diagonal baseline
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Random Baseline (AUC = 0.50)", line=dict(dash="dash", color="gray")))

    colors = [ACCENT_BLUE, SUCCESS_GREEN, WARNING_YELLOW, DANGER_RED]

    for idx, (name, probs) in enumerate(prob_dict.items()):
        fpr, tpr, _ = roc_curve(y_true, probs)
        auc_val = roc_auc_score(y_true, probs)
        fig.add_trace(go.Scatter(x=fpr, y=tpr, mode="lines", name=f"{name} (AUC = {auc_val:.4f})", line=dict(width=2.5, color=colors[idx % len(colors)])))

    fig.update_layout(
        title="ROC Discrimination Curves (Champion vs Challengers)",
        xaxis_title="False Positive Rate (1 - Specificity)",
        yaxis_title="True Positive Rate (Sensitivity)",
        **PLOTLY_THEME["layout"]
    )
    return fig


def create_vintage_seasoning_chart(vintage_summary_df: pd.DataFrame) -> go.Figure:
    """Origination Vintage Default Rate Trend chart."""
    fig = px.line(
        vintage_summary_df,
        x="vintage_year",
        y="observed_default_rate",
        markers=True,
        title="Origination Vintage Default Rate Trend (2007–2018)",
        labels={"vintage_year": "Origination Vintage", "observed_default_rate": "Observed Default Rate (%)"},
        color_discrete_sequence=[PRIMARY_BLUE],
    )
    fig.update_layout(**PLOTLY_THEME["layout"])
    return fig


def create_shap_summary_bar_chart(shap_ranking_df: pd.DataFrame) -> go.Figure:
    """SHAP Feature Ranking horizontal bar chart."""
    top_df = shap_ranking_df.head(10).sort_values("mean_abs_shap", ascending=True)

    fig = px.bar(
        top_df,
        y="feature",
        x="mean_abs_shap",
        orientation="h",
        title="Top 10 Global SHAP Feature Rankings (Mean |SHAP|)",
        labels={"feature": "Risk Driver", "mean_abs_shap": "Mean |SHAP| Value"},
        color_discrete_sequence=[ACCENT_BLUE],
    )
    fig.update_layout(**PLOTLY_THEME["layout"])
    return fig


def create_stress_testing_chart(stress_summary_df: pd.DataFrame) -> go.Figure:
    """Stress Scenario Delta Expected Loss comparison bar chart."""
    fig = px.bar(
        stress_summary_df,
        x="scenario_name",
        y="delta_expected_loss",
        title="Expected Loss Expansion ($) Across Stress Scenarios",
        labels={"scenario_name": "Stress Scenario", "delta_expected_loss": "Delta Expected Loss ($)"},
        color="delta_expected_loss",
        color_continuous_scale="Reds",
    )
    fig.update_layout(xaxis_tickangle=-30, **PLOTLY_THEME["layout"])
    return fig
