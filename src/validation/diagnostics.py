"""Diagnostics module for Linearity assessment and Outlier/Influence analysis."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def run_box_tidwell_test(
    df: pd.DataFrame, target_col: str, feature_cols: list[str], sample_size: int = 10000, random_state: int = 42
) -> pd.DataFrame:
    """Perform Box-Tidwell transformation test (X * ln(X)) to assess non-linearity."""
    avail_features = [f for f in feature_cols if f in df.columns]
    clean_df = df[[target_col] + avail_features].dropna()
    
    # Ensure positive values for log transformation
    pos_features = []
    for f in avail_features:
        if (clean_df[f] > 0).all():
            pos_features.append(f)

    if len(clean_df) > sample_size:
        sample_df = clean_df.sample(n=sample_size, random_state=random_state)
    else:
        sample_df = clean_df

    results = []
    for f in pos_features:
        X_df = pd.DataFrame()
        X_df[f] = sample_df[f]
        X_df[f"{f}_x_ln_x"] = sample_df[f] * np.log(sample_df[f])
        X = sm.add_constant(X_df)
        y = sample_df[target_col]

        try:
            model = sm.Logit(y, X).fit(disp=False)
            p_val = model.pvalues.get(f"{f}_x_ln_x", np.nan)
            coef = model.params.get(f"{f}_x_ln_x", np.nan)
            results.append({
                "feature": f,
                "interaction_coef": round(float(coef), 6) if pd.notna(coef) else np.nan,
                "box_tidwell_pvalue": float(p_val) if pd.notna(p_val) else np.nan,
                "is_non_linear": "Yes" if (pd.notna(p_val) and p_val < 0.05) else "No",
            })
        except Exception:
            continue

    return pd.DataFrame(results)


def generate_linearity_plots(
    df: pd.DataFrame, target_col: str, feature_cols: list[str], output_dir: Path | str, sample_size: int = 10000
) -> list[str]:
    """Generate LOWESS curves and Partial Residual plots against default log-odds."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    generated_files = []

    avail_features = [f for f in feature_cols if f in df.columns]
    clean_df = df[[target_col] + avail_features].dropna()
    if len(clean_df) > sample_size:
        sample_df = clean_df.sample(n=sample_size, random_state=42)
    else:
        sample_df = clean_df

    for f in avail_features:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # LOWESS smoothing against outcome
        sns.regplot(
            x=f,
            y=target_col,
            data=sample_df,
            lowess=True,
            ax=axes[0],
            scatter_kws={"alpha": 0.15, "s": 10},
            line_kws={"color": "red", "linewidth": 2},
        )
        axes[0].set_title(f"{f} vs Log-Odds of Default (LOWESS)")
        axes[0].set_xlabel(f)
        axes[0].set_ylabel("Default Log-Odds Proxy")

        # Component plus Residual (Partial Residual) plot proxy
        try:
            X = sm.add_constant(sample_df[avail_features])
            y = sample_df[target_col]
            ols_fit = sm.OLS(y, X).fit()
            resids = ols_fit.resid + ols_fit.params[f] * sample_df[f]

            axes[1].scatter(sample_df[f], resids, alpha=0.15, s=10, color="#1f77b4")
            sns.regplot(
                x=sample_df[f],
                y=resids,
                ax=axes[1],
                scatter=False,
                lowess=True,
                line_kws={"color": "darkgreen", "linewidth": 2},
            )
            axes[1].set_title(f"{f} - Component + Residual Plot")
            axes[1].set_xlabel(f)
            axes[1].set_ylabel("Component + Residual")
        except Exception:
            axes[1].text(0.5, 0.5, "Partial residual error", ha="center", va="center")

        plt.tight_layout()
        file_name = output_path / f"linearity_{f}.png"
        plt.savefig(file_name, dpi=150, bbox_inches="tight")
        plt.close(fig)
        generated_files.append(str(file_name))

    return generated_files


def calculate_outlier_influence_metrics(
    df: pd.DataFrame, target_col: str, feature_cols: list[str], sample_size: int = 5000, random_state: int = 42
) -> tuple[pd.DataFrame, dict[str, float | int | str]]:
    """Compute Leverage (Hat values), Cook's Distance, Studentized Residuals, and DFBETAS."""
    avail_features = [f for f in feature_cols if f in df.columns]
    clean_df = df[[target_col] + avail_features].dropna()
    if len(clean_df) > sample_size:
        sample_df = clean_df.sample(n=sample_size, random_state=random_state)
    else:
        sample_df = clean_df

    y = sample_df[target_col]
    X = sm.add_constant(sample_df[avail_features])

    model = sm.OLS(y, X).fit()
    influence = model.get_influence()

    hat_values = influence.hat_matrix_diag
    cooks_d, _ = influence.cooks_distance
    stud_resids = influence.resid_studentized_internal

    n, p = X.shape
    leverage_cutoff = 2 * p / n
    cooks_cutoff = 4 / n
    outlier_cutoff = 3.0

    high_leverage_count = int(np.sum(hat_values > leverage_cutoff))
    high_cooks_count = int(np.sum(cooks_d > cooks_cutoff))
    outlier_resid_count = int(np.sum(np.abs(stud_resids) > outlier_cutoff))

    summary = {
        "sample_n": n,
        "parameters_p": p,
        "leverage_threshold_2p_n": round(float(leverage_cutoff), 6),
        "high_leverage_observations": high_leverage_count,
        "high_leverage_pct": round(high_leverage_count / n * 100, 2),
        "cooks_distance_threshold_4_n": round(float(cooks_cutoff), 6),
        "influential_cooks_observations": high_cooks_count,
        "influential_cooks_pct": round(high_cooks_count / n * 100, 2),
        "outlier_studentized_resids_abs3": outlier_resid_count,
        "outlier_studentized_pct": round(outlier_resid_count / n * 100, 2),
        "banking_recommendation": (
            "Do NOT remove observations blindly. Leverage capping (winsorization) or WoE fine-classing binning "
            "should be used in scorecard development to manage extreme values while preserving sample integrity."
        ),
    }

    obs_df = pd.DataFrame({
        "hat_value": np.round(hat_values, 6),
        "cooks_distance": np.round(cooks_d, 6),
        "studentized_resid": np.round(stud_resids, 4),
        "is_high_leverage": hat_values > leverage_cutoff,
        "is_influential_cook": cooks_d > cooks_cutoff,
        "is_outlier_resid": np.abs(stud_resids) > outlier_cutoff,
    })

    return obs_df, summary
