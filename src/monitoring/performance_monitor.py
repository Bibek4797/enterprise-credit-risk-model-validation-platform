"""Longitudinal performance tracking, ROC-AUC decay, and threshold stability engine."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, brier_score_loss, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)


def compute_performance_metrics_snapshot(
    y_true: pd.Series | np.ndarray,
    y_prob: pd.Series | np.ndarray,
    threshold: float = 0.20,
) -> dict[str, float]:
    """Compute comprehensive credit risk model evaluation metrics for a monitoring snapshot."""
    y_arr = np.asarray(y_true, dtype=int)
    p_arr = np.asarray(y_prob, dtype=float)

    auc = float(roc_auc_score(y_arr, p_arr))
    gini = float(2.0 * auc - 1.0)
    brier = float(brier_score_loss(y_arr, p_arr))

    # Kolmogorov-Smirnov (KS) statistic
    data = pd.DataFrame({"target": y_arr, "prob": p_arr}).sort_values("prob", ascending=False)
    data["cum_goods"] = (data["target"] == 0).cumsum() / (sum(data["target"] == 0) + 1e-6)
    data["cum_bads"] = (data["target"] == 1).cumsum() / (sum(data["target"] == 1) + 1e-6)
    ks_stat = float(np.max(np.abs(data["cum_bads"] - data["cum_goods"])))

    # Binary metrics at threshold
    y_pred = (p_arr >= threshold).astype(int)
    prec = float(precision_score(y_arr, y_pred, zero_division=0))
    rec = float(recall_score(y_arr, y_pred, zero_division=0))
    f1 = float(f1_score(y_arr, y_pred, zero_division=0))

    return {
        "roc_auc": round(auc, 4),
        "gini_index": round(gini, 4),
        "ks_statistic_pct": round(ks_stat * 100.0, 2),
        "brier_score": round(brier, 5),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "approval_rate_pct": round(float(np.mean(y_pred == 0)) * 100.0, 2),
    }


def track_longitudinal_vintage_performance(
    df: pd.DataFrame,
    vintage_col: str = "vintage_year",
    target_col: str = "target",
    prob_col: str = "y_prob",
) -> pd.DataFrame:
    """Evaluate ROC-AUC, Gini, and KS performance decay across annual/quarterly origination vintages."""
    records = []
    for vintage, group in df.groupby(vintage_col, observed=False):
        if len(group["target"].unique()) > 1:
            res = compute_performance_metrics_snapshot(group[target_col], group[prob_col])
            res["vintage"] = vintage
            records.append(res)

    df_perf = pd.DataFrame(records)
    if not df_perf.empty:
        df_perf = df_perf.sort_values("vintage").reset_index(drop=True)

    return df_perf
