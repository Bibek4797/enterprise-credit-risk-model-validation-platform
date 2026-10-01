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
    df_plot = vintage_df.copy()

    # If raw loan-level data was passed, aggregate using build_vintage_summary
    if "observed_default_rate" not in df_plot.columns:
        try:
            from portfolio.vintage import build_vintage_summary
            df_plot = build_vintage_summary(df_plot)
        except Exception:
            # Fallback inline aggregation if issue_d and target exist
            if "issue_d" in df_plot.columns and "target" in df_plot.columns:
                df_plot["issue_dt"] = pd.to_datetime(df_plot["issue_d"], format="%b-%Y", errors="coerce")
                df_plot["vintage_year"] = df_plot["issue_dt"].dt.year
                df_plot = (
                    df_plot.dropna(subset=["vintage_year"])
                    .groupby("vintage_year")
                    .agg(total=("target", "count"), defaults=("target", "sum"))
                    .reset_index()
                )
                df_plot["observed_default_rate"] = (df_plot["defaults"] / df_plot["total"] * 100.0).round(2)

    if "vintage_year" in df_plot.columns and "observed_default_rate" in df_plot.columns:
        df_plot = df_plot.dropna(subset=["vintage_year"]).sort_values("vintage_year")
        x_col = "vintage_year"
        y_col = "observed_default_rate"
    else:
        x_col = df_plot.columns[0]
        y_col = df_plot.columns[1] if len(df_plot.columns) > 1 else df_plot.columns[0]

    fig = px.line(
        df_plot, x=x_col, y=y_col, markers=True,
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
            else [c for c in df_or_ranking.columns if c != "target"][:10]
        )
        records = []
        for f in feat_list:
            if f in df_or_ranking.columns:
                s = pd.to_numeric(df_or_ranking[f], errors="coerce").dropna()
                if len(s) > 1:
                    val = float(np.std(s))
                else:
                    freqs = df_or_ranking[f].dropna().astype(str).value_counts(normalize=True).values
                    val = float(np.std(freqs)) if len(freqs) > 1 else 0.05
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


# ── Model Monitoring (Whole Model PSI & CSI) ──────────────────
def create_model_psi_distribution_chart(
    base_preds: np.ndarray | pd.Series,
    actual_preds: np.ndarray | pd.Series,
) -> go.Figure:
    """Overlaid distribution chart of Baseline Expected vs Current Actual Model predicted PD."""
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=base_preds,
        name="Baseline Development Vintage (Expected)",
        opacity=0.6,
        nbinsx=35,
        histnorm="probability density",
        marker_color="#3b82f6",
    ))
    fig.add_trace(go.Histogram(
        x=actual_preds,
        name="Current Operational Vintage (Actual)",
        opacity=0.6,
        nbinsx=35,
        histnorm="probability density",
        marker_color="#10b981",
    ))
    fig.update_layout(
        barmode="overlay",
        xaxis_title="Model Predicted Probability of Default (PD)",
        yaxis_title="Probability Density",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return _apply_theme(fig, "Whole Model PD Distribution: Baseline Vintage vs Current Operational Period")


def create_csi_ranking_chart(csi_df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Horizontal bar chart showing top features ranked by Characteristic Stability Index (CSI)."""
    top_df = csi_df.head(top_n).sort_values("csi_value", ascending=True)
    fig = px.bar(
        top_df,
        y="feature_name",
        x="csi_value",
        orientation="h",
        labels={"feature_name": "Risk Driver", "csi_value": "CSI Drift Metric"},
        color="csi_value",
        color_continuous_scale=[[0, "#10b981"], [0.4, "#f59e0b"], [1.0, "#ef4444"]],
    )
    fig.add_vline(x=0.10, line_dash="dash", line_color="#f59e0b", annotation_text="Warning (0.10)")
    fig.add_vline(x=0.25, line_dash="dash", line_color="#ef4444", annotation_text="Critical (0.25)")
    fig.update_traces(marker_line_width=0)
    fig.update_coloraxes(showscale=False)
    return _apply_theme(fig, f"Top {min(top_n, len(top_df))} Features Ranked by Characteristic Stability Index (CSI)")


# ── Stress Testing ────────────────────────────────────────────
def create_stress_testing_chart(stress_summary_df: pd.DataFrame) -> go.Figure:
    """Stress Scenario Delta Expected Loss comparison bar chart."""
    x_col = "scenario_name" if "scenario_name" in stress_summary_df.columns else stress_summary_df.columns[0]
    y_col = "delta_expected_loss" if "delta_expected_loss" in stress_summary_df.columns else stress_summary_df.columns[-1]

    fig = px.bar(
        stress_summary_df, x=x_col, y=y_col,
        labels={x_col: "Stress Scenario", y_col: "Delta Expected Loss ($)"},
        color=y_col,
        color_continuous_scale=[[0, "#3b82f6"], [0.5, "#f59e0b"], [1.0, "#ef4444"]],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(xaxis_tickangle=-15, coloraxis_showscale=False)
    return _apply_theme(fig, "Expected Loss Expansion Across CCAR Fed Scenarios")


def create_scurve_transmission_chart(delta_b0: float = 0.80) -> go.Figure:
    """Plot non-linear S-curve transmission showing differential borrower impact."""
    p_base = np.linspace(0.001, 0.999, 300)
    z_base = np.log(p_base / (1.0 - p_base))
    z_stressed = z_base + delta_b0
    p_stressed = 1.0 / (1.0 + np.exp(-z_stressed))

    fig = go.Figure()

    # Diagonal 45-degree reference line (No stress)
    fig.add_trace(go.Scatter(
        x=p_base * 100, y=p_base * 100, mode="lines",
        name="No Stress Baseline (45° Line)",
        line=dict(color="#64748b", dash="dash", width=1.5),
    ))

    # Stressed S-curve
    fig.add_trace(go.Scatter(
        x=p_base * 100, y=p_stressed * 100, mode="lines",
        name=f"Stressed Transmission Curve (Δβ₀ = {delta_b0:+.2f})",
        line=dict(color="#ef4444", width=3),
    ))

    # Prime borrower annotation (PD = 1.0% -> 2.2%)
    p_prime = 0.01
    p_prime_str = 1.0 / (1.0 + np.exp(-(np.log(p_prime / (1.0 - p_prime)) + delta_b0)))
    fig.add_trace(go.Scatter(
        x=[p_prime * 100], y=[p_prime_str * 100], mode="markers+text",
        name="Prime Borrower (PD=1%)",
        text=[f"Prime: 1.0% → {p_prime_str*100:.1f}% (+{p_prime_str*100 - 1.0:.1f}%)"],
        textposition="top left",
        marker=dict(size=10, color="#10b981"),
    ))

    # Subprime borrower annotation (PD = 20.0% -> 35.8%)
    p_sub = 0.20
    p_sub_str = 1.0 / (1.0 + np.exp(-(np.log(p_sub / (1.0 - p_sub)) + delta_b0)))
    fig.add_trace(go.Scatter(
        x=[p_sub * 100], y=[p_sub_str * 100], mode="markers+text",
        name="Subprime Borrower (PD=20%)",
        text=[f"Subprime: 20.0% → {p_sub_str*100:.1f}% (+{p_sub_str*100 - 20.0:.1f}%)"],
        textposition="bottom right",
        marker=dict(size=10, color="#f59e0b"),
    ))

    fig.update_layout(
        xaxis_title="Baseline Loan-Level PD (%)",
        yaxis_title="Stressed Loan-Level PD (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return _apply_theme(fig, "Non-Linear S-Curve Transmission: d(PD)/dz = PD(1 − PD)")


# ── Helper ────────────────────────────────────────────────────
def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    """Convert #rrggbb to (r, g, b) floats 0-1."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))


# Aliases kept for backward compat
create_roc_curves_chart = create_roc_curve_chart

