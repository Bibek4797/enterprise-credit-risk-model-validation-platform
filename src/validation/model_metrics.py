"""Comprehensive model evaluation metrics for credit risk models.

Implements ROC-AUC, Gini coefficient, Kolmogorov-Smirnov (KS) statistic,
Brier score, Hosmer-Lemeshow calibration test, Lift/Gain tables,
and confusion matrix diagnostics per Basel III and SR 11-7 standards.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from scipy.stats import chi2
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

logger = logging.getLogger(__name__)


def calculate_roc_auc(y_true: np.ndarray | pd.Series, y_prob: np.ndarray | pd.Series) -> float:
    """Calculate Receiver Operating Characteristic Area Under Curve (ROC-AUC)."""
    return float(roc_auc_score(y_true, y_prob))


def calculate_gini(y_true: np.ndarray | pd.Series, y_prob: np.ndarray | pd.Series) -> float:
    """Calculate Gini Coefficient (2 * AUC - 1)."""
    auc = calculate_roc_auc(y_true, y_prob)
    return float(2.0 * auc - 1.0)


def calculate_ks_statistic(
    y_true: np.ndarray | pd.Series, y_prob: np.ndarray | pd.Series
) -> dict[str, float]:
    """Calculate Kolmogorov-Smirnov (KS) statistic and optimal score cutoff threshold."""
    fpr, tpr, thresholds = roc_curve(y_true, y_prob)
    ks_values = tpr - fpr
    max_idx = np.argmax(ks_values)
    ks_stat = float(ks_values[max_idx])
    opt_threshold = float(thresholds[max_idx])

    return {
        "ks_stat": round(ks_stat * 100.0, 2),  # Expressed as percentage
        "ks_decimal": round(ks_stat, 4),
        "optimal_threshold": round(opt_threshold, 4),
    }


def calculate_brier_score(y_true: np.ndarray | pd.Series, y_prob: np.ndarray | pd.Series) -> float:
    """Calculate Brier Score (Mean Squared Error of probability predictions)."""
    return float(brier_score_loss(y_true, y_prob))


def calculate_confusion_matrix_metrics(
    y_true: np.ndarray | pd.Series,
    y_prob: np.ndarray | pd.Series,
    threshold: float = 0.50,
) -> dict[str, float]:
    """Compute confusion matrix components, sensitivity, specificity, precision, recall, and F1."""
    y_true_arr = np.asarray(y_true, dtype=int)
    y_pred = (np.asarray(y_prob) >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true_arr, y_pred).ravel()

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = precision_score(y_true_arr, y_pred, zero_division=0)
    recall = recall_score(y_true_arr, y_pred, zero_division=0)
    f1 = f1_score(y_true_arr, y_pred, zero_division=0)
    acc = accuracy_score(y_true_arr, y_pred)

    return {
        "threshold": threshold,
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "accuracy": round(float(acc), 4),
        "sensitivity_recall": round(float(sensitivity), 4),
        "specificity": round(float(specificity), 4),
        "precision": round(float(precision), 4),
        "f1_score": round(float(f1), 4),
    }


def hosmer_lemeshow_test(
    y_true: np.ndarray | pd.Series,
    y_prob: np.ndarray | pd.Series,
    g: int = 10,
) -> dict[str, float]:
    """Perform Hosmer-Lemeshow Goodness-of-Fit test for binary logistic models."""
    y_true_arr = np.asarray(y_true, dtype=int)
    y_prob_arr = np.asarray(y_prob, dtype=float)

    data = pd.DataFrame({"y": y_true_arr, "prob": y_prob_arr})
    try:
        data["decile"] = pd.qcut(data["prob"], q=g, duplicates="drop")
    except ValueError:
        data["decile"] = pd.cut(data["prob"], bins=g)

    hl_stat = 0.0
    for _, group in data.groupby("decile", observed=False):
        n_g = len(group)
        if n_g == 0:
            continue
        obs_events = group["y"].sum()
        obs_non_events = n_g - obs_events
        exp_events = group["prob"].sum()
        exp_non_events = n_g - exp_events

        e_term = ((obs_events - exp_events) ** 2) / (exp_events + 1e-6)
        ne_term = ((obs_non_events - exp_non_events) ** 2) / (exp_non_events + 1e-6)
        hl_stat += e_term + ne_term

    dof = max(g - 2, 1)
    p_val = float(1.0 - chi2.cdf(hl_stat, dof))

    return {
        "hl_statistic": round(float(hl_stat), 4),
        "degrees_of_freedom": dof,
        "p_value": round(p_val, 4),
        "is_calibrated": bool(p_val >= 0.05),
    }


def calculate_lift_gain(
    y_true: np.ndarray | pd.Series,
    y_prob: np.ndarray | pd.Series,
    quantiles: int = 10,
) -> pd.DataFrame:
    """Construct Cumulative Lift and Gain table across score deciles."""
    df_lg = pd.DataFrame({"y": np.asarray(y_true, dtype=int), "prob": np.asarray(y_prob, dtype=float)})
    df_lg = df_lg.sort_values("prob", ascending=False).reset_index(drop=True)

    df_lg["decile"] = pd.qcut(df_lg.index, q=quantiles, labels=list(range(1, quantiles + 1)))

    total_bads = df_lg["y"].sum()
    total_count = len(df_lg)

    summary = (
        df_lg.groupby("decile", observed=False)
        .agg(
            total_loans=("y", "count"),
            bads=("y", "sum"),
            min_prob=("prob", "min"),
            max_prob=("prob", "max"),
        )
        .reset_index()
    )

    summary["cum_loans"] = summary["total_loans"].cumsum()
    summary["cum_bads"] = summary["bads"].cumsum()

    summary["gain_pct"] = round((summary["cum_bads"] / total_bads) * 100.0, 2)
    summary["decile_bad_rate"] = round((summary["bads"] / summary["total_loans"]) * 100.0, 2)
    summary["lift"] = round(summary["decile_bad_rate"] / ((total_bads / total_count) * 100.0), 2)

    return summary


def evaluate_all_metrics(
    y_true: np.ndarray | pd.Series,
    y_prob: np.ndarray | pd.Series,
    threshold: float = 0.50,
) -> dict[str, float]:
    """Execute complete suite of credit risk validation metrics."""
    auc = calculate_roc_auc(y_true, y_prob)
    gini = calculate_gini(y_true, y_prob)
    ks_info = calculate_ks_statistic(y_true, y_prob)
    brier = calculate_brier_score(y_true, y_prob)
    conf_info = calculate_confusion_matrix_metrics(y_true, y_prob, threshold=threshold)
    hl_info = hosmer_lemeshow_test(y_true, y_prob)

    return {
        "roc_auc": round(auc, 4),
        "gini": round(gini, 4),
        "ks_stat": ks_info["ks_stat"],
        "ks_optimal_threshold": ks_info["optimal_threshold"],
        "brier_score": round(brier, 5),
        "accuracy": conf_info["accuracy"],
        "sensitivity": conf_info["sensitivity_recall"],
        "specificity": conf_info["specificity"],
        "precision": conf_info["precision"],
        "f1_score": conf_info["f1_score"],
        "hl_stat": hl_info["hl_statistic"],
        "hl_p_value": hl_info["p_value"],
        "hl_is_calibrated": hl_info["is_calibrated"],
    }


def evaluate_binary_model(
    y_true: np.ndarray | pd.Series,
    y_prob: np.ndarray | pd.Series,
    threshold: float = 0.50,
) -> dict[str, float]:
    """Alias for evaluate_all_metrics matching dashboard & testing requirements."""
    res = evaluate_all_metrics(y_true, y_prob, threshold=threshold)
    res["gini_index"] = res["gini"]
    res["ks_statistic_pct"] = res["ks_stat"]
    return res
