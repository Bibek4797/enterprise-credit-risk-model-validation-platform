"""Reusable Plotly Chart Components — Premium Dark-Mode Theme."""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

dash_dir = Path(__file__).resolve().parent.parent
root_dir = dash_dir.parent
for d in [str(root_dir), str(dash_dir), str(root_dir / "src")]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from config.theme import (
        PRIMARY_BLUE, ACCENT_BLUE, ACCENT_PURPLE,
        SUCCESS_GREEN, DANGER_RED, WARNING_YELLOW,
        GRADE_COLORS, PLOTLY_THEME, TITLE_STYLE,
    )
except ImportError:
    from dashboard.config.theme import (
        PRIMARY_BLUE, ACCENT_BLUE, ACCENT_PURPLE,
        SUCCESS_GREEN, DANGER_RED, WARNING_YELLOW,
        GRADE_COLORS, PLOTLY_THEME, TITLE_STYLE,
    )


def _t(text: str) -> dict:
    """Build a Plotly title dict with consistent premium styling."""
    return {"text": text, **TITLE_STYLE}


def _apply_theme(fig: go.Figure, title: str | None = None) -> go.Figure:
    """Apply shared theme layout + optional title to a figure."""
    kwargs = dict(PLOTLY_THEME["layout"])
    if title:
        kwargs["title"] = _t(title)
    fig.update_layout(**kwargs)
    return fig


# ── Grade Distribution Bar ────────────────────────────────────
def create_grade_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of loan exposure and count by Risk Grade."""
    if "grade" not in df.columns:
        fig = go.Figure()
        return _apply_theme(fig, "Grade data not available")

    grade_counts = (
        df.groupby("grade", observed=False)["loan_amnt"]
        .agg(["count", "sum"])
        .reset_index()
    )
    grade_counts["exposure_m"] = grade_counts["sum"] / 1e6

    fig = px.bar(
        grade_counts,
        x="grade",
        y="exposure_m",
        color="grade",
        color_discrete_map=GRADE_COLORS,
        labels={"grade": "Risk Grade", "exposure_m": "Exposure ($M)"},
        text_auto=".1f",
    )
    fig.update_traces(marker_line_width=0)
    return _apply_theme(fig, "Portfolio Exposure ($M) by Risk Grade")


# ── ROC Curves ────────────────────────────────────────────────
def create_roc_curve_chart(
    y_true: np.ndarray,
    sc_probs: np.ndarray | dict[str, np.ndarray],
    lgb_probs: np.ndarray | None = None,
) -> go.Figure:
    """ROC Curve Comparison — Champion vs Challengers."""
    from sklearn.metrics import roc_curve, roc_auc_score

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines",
        name="Random Baseline (AUC = 0.50)",
        line=dict(dash="dash", color="rgba(100,116,139,0.6)", width=1.5),
    ))

    colors = [PRIMARY_BLUE, ACCENT_PURPLE, SUCCESS_GREEN, DANGER_RED, WARNING_YELLOW]

    if isinstance(sc_probs, dict):
        prob_dict = sc_probs
    else:
        prob_dict = {"Champion Scorecard": sc_probs}
        if lgb_probs is not None:
            prob_dict["Challenger LightGBM"] = lgb_probs

    for idx, (name, probs) in enumerate(prob_dict.items()):
        try:
            fpr, tpr, _ = roc_curve(y_true, probs)
            auc_val = float(roc_auc_score(y_true, probs))
            fig.add_trace(go.Scatter(
                x=fpr, y=tpr, mode="lines",
                name=f"{name} (AUC = {auc_val:.4f})",
                line=dict(width=2.5, color=colors[idx % len(colors)]),
                fill="tozeroy",
                fillcolor=f"rgba({','.join(str(int(c*255)) for c in _hex_to_rgb(colors[idx % len(colors)]))},0.05)",
            ))
        except Exception:
            pass

    fig.update_layout(
        xaxis_title="False Positive Rate (1 − Specificity)",
        yaxis_title="True Positive Rate (Sensitivity)",
    )
    return _apply_theme(fig, "ROC Discrimination Curves — Champion vs Challengers")


# ── Vintage Curve ──────────────────────────────────────────────
def create_vintage_chart(vintage_df: pd.DataFrame) -> go.Figure:
    """Origination Vintage Default Rate Trend chart."""
    x_col = "vintage_year" if "vintage_year" in vintage_df.columns else vintage_df.columns[0]
    y_col = "observed_default_rate" if "observed_default_rate" in vintage_df.columns else vintage_df.columns[1]

    fig = px.line(
        vintage_df, x=x_col, y=y_col, markers=True,
        labels={x_col: "Origination Vintage", y_col: "Observed Default Rate (%)"},
        color_discrete_sequence=[PRIMARY_BLUE],
    )
    fig.update_traces(line_width=2.5, marker_size=7)
    return _apply_theme(fig, "Origination Vintage Default Rate Trend")


create_vintage_seasoning_chart = create_vintage_chart


# ── SHAP Summary ──────────────────────────────────────────────
def create_shap_summary_chart(
    df_or_ranking: pd.DataFrame,
    features: list[str] | None = None,
) -> go.Figure:
    """SHAP Feature Ranking horizontal bar chart."""
    if "mean_abs_shap" in df_or_ranking.columns:
        top_df = df_or_ranking.head(10).sort_values("mean_abs_shap", ascending=True)
    else:
        feat_list = (
            features
            if features
            else [c for c in df_or_ranking.select_dtypes(include=[np.number]).columns if c != "target"][:10]
        )
        records = []
        for f in feat_list:
            if f in df_or_ranking.columns:
                val = float(np.std(df_or_ranking[f].dropna()))
                records.append({"feature": f, "mean_abs_shap": round(val, 4)})
        top_df = pd.DataFrame(records).sort_values("mean_abs_shap", ascending=True)

    fig = px.bar(
        top_df, y="feature", x="mean_abs_shap", orientation="h",
        labels={"feature": "Risk Driver", "mean_abs_shap": "Mean |SHAP| Value"},
        color="mean_abs_shap",
        color_continuous_scale=[[0, "#1d4ed8"], [0.5, "#3b82f6"], [1.0, "#60a5fa"]],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_coloraxes(showscale=False)
    return _apply_theme(fig, "Top Global SHAP Feature Rankings (Mean |SHAP|)")


create_shap_summary_bar_chart = create_shap_summary_chart


# ── Stress Testing ────────────────────────────────────────────
def create_stress_testing_chart(stress_summary_df: pd.DataFrame) -> go.Figure:
    """Stress Scenario Delta Expected Loss comparison bar chart."""
    x_col = "scenario_name" if "scenario_name" in stress_summary_df.columns else stress_summary_df.columns[0]
    y_col = "delta_expected_loss" if "delta_expected_loss" in stress_summary_df.columns else stress_summary_df.columns[-1]

    fig = px.bar(
        stress_summary_df, x=x_col, y=y_col,
        labels={x_col: "Stress Scenario", y_col: "Delta Expected Loss ($)"},
        color=y_col,
        color_continuous_scale=[[0, "#7c3aed"], [0.5, "#ef4444"], [1.0, "#dc2626"]],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(xaxis_tickangle=-30, coloraxis_showscale=False)
    return _apply_theme(fig, "Expected Loss Expansion ($) Across Stress Scenarios")


# ── Helper ────────────────────────────────────────────────────
def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    """Convert #rrggbb to (r, g, b) floats 0-1."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))


# Aliases kept for backward compat
create_roc_curves_chart = create_roc_curve_chart
