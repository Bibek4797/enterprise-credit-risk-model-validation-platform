"""Statistical tests module for banking-grade credit risk model validation."""

from __future__ import annotations

import os
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def calculate_descriptive_stats(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Calculate comprehensive descriptive statistics for specified numeric columns.

    Includes Mean, Median, Mode, Variance, Std Dev, Coeff of Variation, Range,
    Q1, Q3, IQR, Skewness, and Kurtosis.
    """
    stats_list = []
    for col in columns:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if series.empty:
            continue

        mean_val = series.mean()
        std_val = series.std()
        median_val = series.median()
        mode_val = series.mode().iloc[0] if not series.mode().empty else np.nan
        var_val = series.var()
        cv_val = std_val / abs(mean_val) if mean_val != 0 else np.nan
        min_val = series.min()
        max_val = series.max()
        range_val = max_val - min_val
        q1_val = series.quantile(0.25)
        q3_val = series.quantile(0.75)
        iqr_val = q3_val - q1_val
        skew_val = series.skew()
        kurt_val = series.kurtosis()

        stats_list.append({
            "feature": col,
            "count": len(series),
            "mean": round(float(mean_val), 4),
            "median": round(float(median_val), 4),
            "mode": round(float(mode_val), 4) if pd.notna(mode_val) else np.nan,
            "variance": round(float(var_val), 4),
            "std_dev": round(float(std_val), 4),
            "coef_variation": round(float(cv_val), 4) if pd.notna(cv_val) else np.nan,
            "min": round(float(min_val), 4),
            "max": round(float(max_val), 4),
            "range": round(float(range_val), 4),
            "q1": round(float(q1_val), 4),
            "q3": round(float(q3_val), 4),
            "iqr": round(float(iqr_val), 4),
            "skewness": round(float(skew_val), 4),
            "kurtosis": round(float(kurt_val), 4),
        })

    return pd.DataFrame(stats_list)


def run_normality_tests(
    df: pd.DataFrame, columns: list[str], sample_size: int = 5000, random_state: int = 42
) -> pd.DataFrame:
    """Perform Shapiro-Wilk, Jarque-Bera, Anderson-Darling, and D'Agostino K2 tests."""
    results = []
    np.random.seed(random_state)

    for col in columns:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if len(series) < 10:
            continue

        # Shapiro-Wilk on sample due to N<=5000 constraint
        sample_series = series.sample(n=min(len(series), sample_size), random_state=random_state)
        sw_stat, sw_p = stats.shapiro(sample_series)

        # Jarque-Bera (full series)
        jb_stat, jb_p = stats.jarque_bera(series)

        # D'Agostino K2 (full or max 50,000)
        dag_series = series.sample(n=min(len(series), 50000), random_state=random_state)
        dag_stat, dag_p = stats.normaltest(dag_series)

        # Anderson-Darling
        ad_res = stats.anderson(sample_series, dist="norm")
        ad_stat = ad_res.statistic
        ad_crit_5pct = ad_res.critical_values[2]  # 5% significance level

        is_normal = (sw_p > 0.05) and (jb_p > 0.05) and (dag_p > 0.05)

        results.append({
            "feature": col,
            "shapiro_stat": round(float(sw_stat), 5),
            "shapiro_pvalue": float(sw_p),
            "jarque_bera_stat": round(float(jb_stat), 2),
            "jarque_bera_pvalue": float(jb_p),
            "dagostino_stat": round(float(dag_stat), 2),
            "dagostino_pvalue": float(dag_p),
            "anderson_stat": round(float(ad_stat), 4),
            "anderson_crit_5pct": round(float(ad_crit_5pct), 4),
            "normality_holds_5pct": "Yes" if is_normal else "No",
        })

    return pd.DataFrame(results)


def generate_normality_plots(df: pd.DataFrame, columns: list[str], output_dir: Path | str) -> list[str]:
    """Generate QQ plot, density plot, and histogram for distributional inspection."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    generated_files = []

    for col in columns:
        if col not in df.columns:
            continue
        series = df[col].dropna()
        if series.empty:
            continue

        # Clean figure creation
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Subplot 1: Histogram + KDE
        sns.histplot(series, kde=True, ax=axes[0], color="#1f77b4", stat="density", bins=40)
        axes[0].set_title(f"{col} - Distribution & KDE")
        axes[0].set_xlabel(col)

        # Subplot 2: Normal Curve Overlay
        mu, std = series.mean(), series.std()
        x = np.linspace(series.min(), series.max(), 100)
        p = stats.norm.pdf(x, mu, std)
        axes[1].plot(x, p, 'r--', linewidth=2, label="Theoretical Normal")
        sns.kdeplot(series, ax=axes[1], color="#2ca02c", label="Observed KDE")
        axes[1].set_title(f"{col} - KDE vs Normal Overlay")
        axes[1].set_xlabel(col)
        axes[1].legend()

        # Subplot 3: QQ Plot
        sample = series.sample(n=min(len(series), 5000), random_state=42)
        stats.probplot(sample, dist="norm", plot=axes[2])
        axes[2].set_title(f"{col} - Q-Q Plot")

        plt.tight_layout()
        file_name = output_path / f"normality_{col}.png"
        plt.savefig(file_name, dpi=150, bbox_inches="tight")
        plt.close(fig)
        generated_files.append(str(file_name))

    return generated_files


def calculate_psi(
    expected: pd.Series, actual: pd.Series, bins: int = 10, is_categorical: bool = False
) -> tuple[float, pd.DataFrame]:
    """Calculate Population Stability Index (PSI) between expected (base) and actual (target) series."""
    exp_clean = expected.dropna()
    act_clean = actual.dropna()

    if is_categorical or exp_clean.dtype == "object":
        categories = set(exp_clean.unique()).union(set(act_clean.unique()))
        exp_counts = exp_clean.value_counts(normalize=True)
        act_counts = act_clean.value_counts(normalize=True)
        
        psi_records = []
        total_psi = 0.0
        for cat in categories:
            exp_pct = exp_counts.get(cat, 0.0001)
            act_pct = act_counts.get(cat, 0.0001)
            exp_pct = max(exp_pct, 0.0001)
            act_pct = max(act_pct, 0.0001)
            bin_psi = (act_pct - exp_pct) * np.log(act_pct / exp_pct)
            total_psi += bin_psi
            psi_records.append({
                "bin": cat,
                "expected_pct": round(exp_pct, 6),
                "actual_pct": round(act_pct, 6),
                "psi": round(bin_psi, 6),
            })
        return round(float(total_psi), 4), pd.DataFrame(psi_records)

    else:
        percentiles = np.linspace(0, 100, bins + 1)
        bin_edges = np.percentile(exp_clean, percentiles)
        bin_edges[0] = -np.inf
        bin_edges[-1] = np.inf
        bin_edges = np.unique(bin_edges)

        exp_cuts = pd.cut(exp_clean, bins=bin_edges)
        act_cuts = pd.cut(act_clean, bins=bin_edges)

        exp_dist = exp_cuts.value_counts(normalize=True, sort=False)
        act_dist = act_cuts.value_counts(normalize=True, sort=False)

        psi_records = []
        total_psi = 0.0
        for interval in exp_dist.index:
            exp_pct = max(exp_dist.get(interval, 0.0001), 0.0001)
            act_pct = max(act_dist.get(interval, 0.0001), 0.0001)
            bin_psi = (act_pct - exp_pct) * np.log(act_pct / exp_pct)
            total_psi += bin_psi
            psi_records.append({
                "bin": str(interval),
                "expected_pct": round(float(exp_pct), 6),
                "actual_pct": round(float(act_pct), 6),
                "psi": round(float(bin_psi), 6),
            })

        return round(float(total_psi), 4), pd.DataFrame(psi_records)


def calculate_csi(
    expected_df: pd.DataFrame, actual_df: pd.DataFrame, feature_columns: list[str]
) -> pd.DataFrame:
    """Compute Characteristic Stability Index across multiple features."""
    csi_summary = []
    for col in feature_columns:
        if col not in expected_df.columns or col not in actual_df.columns:
            continue
        is_cat = expected_df[col].dtype == "object" or expected_df[col].nunique() < 10
        psi_val, _ = calculate_psi(expected_df[col], actual_df[col], bins=10, is_categorical=is_cat)

        if psi_val < 0.10:
            status = "Stable (No action)"
        elif psi_val <= 0.25:
            status = "Moderate Shift (Monitor)"
        else:
            status = "Significant Shift (Action Required)"

        csi_summary.append({
            "feature": col,
            "psi_csi_value": psi_val,
            "stability_status": status,
        })

    return pd.DataFrame(csi_summary)
