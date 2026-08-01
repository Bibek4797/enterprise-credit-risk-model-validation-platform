"""Independent Model Validation engine for credit risk models.

Implements bootstrap confidence interval estimation, input sensitivity perturbation,
and fair lending bias/disparate impact proxy audits per SR 11-7 and ECOA guidelines.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from sklearn.metrics import brier_score_loss, roc_auc_score, roc_curve

logger = logging.getLogger(__name__)


def run_bootstrap_validation(
    y_true: pd.Series | np.ndarray,
    y_prob: pd.Series | np.ndarray,
    n_bootstraps: int = 500,
    ci_level: float = 0.95,
    random_state: int = 42,
) -> pd.DataFrame:
    """Calculate non-parametric bootstrap confidence intervals for key performance metrics."""
    np.random.seed(random_state)
    y_true_arr = np.asarray(y_true, dtype=int)
    y_prob_arr = np.asarray(y_prob, dtype=float)

    n_samples = len(y_true_arr)
    auc_scores = []
    gini_scores = []
    ks_stats = []
    brier_scores = []

    for _ in range(n_bootstraps):
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        y_b = y_true_arr[indices]
        p_b = y_prob_arr[indices]

        if len(np.unique(y_b)) < 2:
            continue

        auc = roc_auc_score(y_b, p_b)
        gini = 2.0 * auc - 1.0
        fpr, tpr, _ = roc_curve(y_b, p_b)
        ks = float(np.max(tpr - fpr) * 100.0)
        brier = brier_score_loss(y_b, p_b)

        auc_scores.append(auc)
        gini_scores.append(gini)
        ks_stats.append(ks)
        brier_scores.append(brier)

    alpha_lower = (1.0 - ci_level) / 2.0 * 100.0
    alpha_upper = (1.0 + ci_level) / 2.0 * 100.0

    metrics = {
        "roc_auc": auc_scores,
        "gini": gini_scores,
        "ks_stat_pct": ks_stats,
        "brier_score": brier_scores,
    }

    records = []
    for mname, vals in metrics.items():
        records.append({
            "metric": mname,
            "mean": round(float(np.mean(vals)), 4),
            "std_error": round(float(np.std(vals)), 5),
            "ci_lower_95": round(float(np.percentile(vals, alpha_lower)), 4),
            "ci_upper_95": round(float(np.percentile(vals, alpha_upper)), 4),
        })

    return pd.DataFrame(records)


def run_sensitivity_perturbation(
    predict_fn: callable,
    X_sample: pd.DataFrame,
    features: list[str],
    perturbations: list[float] | None = None,
) -> pd.DataFrame:
    """Measure mean predicted PD shift (delta PD) when perturbing numerical inputs."""
    if perturbations is None:
        perturbations = [-0.20, -0.10, 0.0, 0.10, 0.20]

    baseline_preds = predict_fn(X_sample)
    baseline_mean_pd = float(np.mean(baseline_preds))

    records = []
    for feat in features:
        if feat not in X_sample.columns or not pd.api.types.is_numeric_dtype(X_sample[feat]):
            continue

        for factor in perturbations:
            X_pert = X_sample.copy()
            X_pert[feat] = X_pert[feat] * (1.0 + factor)
            new_preds = predict_fn(X_pert)
            new_mean_pd = float(np.mean(new_preds))
            delta_pd = new_mean_pd - baseline_mean_pd

            records.append({
                "feature": feat,
                "perturbation_pct": f"{factor * 100:+.0f}%",
                "baseline_mean_pd": round(baseline_mean_pd, 4),
                "perturbed_mean_pd": round(new_mean_pd, 4),
                "delta_pd": round(delta_pd, 4),
                "relative_change_pct": round((delta_pd / (baseline_mean_pd + 1e-6)) * 100.0, 2),
            })

    return pd.DataFrame(records)


def evaluate_fairness_proxies(
    df: pd.DataFrame,
    target_col: str,
    prob_col: str,
    group_col: str,
    cutoff_threshold: float = 0.20,
) -> pd.DataFrame:
    """Audit disparate impact and selection rates across demographic/income proxy groups."""
    valid = df.dropna(subset=[target_col, prob_col, group_col]).copy()
    valid["prediction_binary"] = (valid[prob_col] >= cutoff_threshold).astype(int)

    # Reference group is group with lowest default rate or highest count
    groups = valid[group_col].unique()

    records = []
    overall_approval_rate = (valid["prediction_binary"] == 0).mean()

    for g in groups:
        sub = valid[valid[group_col] == g]
        if len(sub) == 0:
            continue

        count = len(sub)
        observed_bad_rate = sub[target_col].mean()
        mean_predicted_pd = sub[prob_col].mean()
        approval_rate = (sub["prediction_binary"] == 0).mean()
        disparate_impact_ratio = approval_rate / (overall_approval_rate + 1e-6)

        records.append({
            "group": str(g),
            "sample_count": count,
            "sample_share_pct": round((count / len(valid)) * 100.0, 2),
            "observed_bad_rate": round(float(observed_bad_rate), 4),
            "mean_predicted_pd": round(float(mean_predicted_pd), 4),
            "approval_rate": round(float(approval_rate), 4),
            "disparate_impact_ratio": round(float(disparate_impact_ratio), 4),
            "ecoa_status": "PASS (>= 0.80 Rule)" if disparate_impact_ratio >= 0.80 else "AUDIT REQUIRED (< 0.80)",
        })

    return pd.DataFrame(records).sort_values("sample_count", ascending=False).reset_index(drop=True)
