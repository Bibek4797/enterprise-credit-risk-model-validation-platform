"""Master Model Comparison & Benchmark Engine for Credit Risk.

Evaluates Statistical Champion vs ML Challengers across ROC-AUC, Gini, KS, MCC,
Balanced Accuracy, Brier Score, inference latency, seed stability, and calibration.
"""

from __future__ import annotations

import logging
import time
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

logger = logging.getLogger(__name__)


def compute_comprehensive_metrics(
    y_true: np.ndarray | pd.Series,
    y_prob: np.ndarray | pd.Series,
    threshold: float = 0.50,
) -> dict[str, float]:
    """Compute comprehensive credit risk metrics including MCC and Balanced Accuracy."""
    y_arr = np.asarray(y_true, dtype=int)
    prob_arr = np.asarray(y_prob, dtype=float)
    pred_arr = (prob_arr >= threshold).astype(int)

    auc = float(roc_auc_score(y_arr, prob_arr))
    gini = float(2.0 * auc - 1.0)

    fpr, tpr, thresholds = roc_curve(y_arr, prob_arr)
    ks_idx = np.argmax(tpr - fpr)
    ks_stat = float((tpr[ks_idx] - fpr[ks_idx]) * 100.0)

    brier = float(brier_score_loss(y_arr, prob_arr))
    acc = float(accuracy_score(y_arr, pred_arr))
    bal_acc = float(balanced_accuracy_score(y_arr, pred_arr))
    mcc = float(matthews_corrcoef(y_arr, pred_arr))
    prec = float(precision_score(y_arr, pred_arr, zero_division=0))
    rec = float(recall_score(y_arr, pred_arr, zero_division=0))
    f1 = float(f1_score(y_arr, pred_arr, zero_division=0))

    tn, fp, fn, tp = confusion_matrix(y_arr, pred_arr).ravel()
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    return {
        "roc_auc": round(auc, 4),
        "gini": round(gini, 4),
        "ks_stat_pct": round(ks_stat, 2),
        "brier_score": round(brier, 5),
        "accuracy": round(acc, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "mcc": round(mcc, 4),
        "precision": round(prec, 4),
        "recall_sensitivity": round(rec, 4),
        "specificity": round(spec, 4),
        "f1_score": round(f1, 4),
    }


def measure_inference_latency(
    model: object,
    X_sample: pd.DataFrame,
    n_runs: int = 20,
) -> dict[str, float]:
    """Measure average inference prediction time per 1,000 samples in milliseconds."""
    sample_1k = X_sample.iloc[:1000] if len(X_sample) >= 1000 else X_sample
    times = []

    for _ in range(n_runs):
        t0 = time.time()
        if hasattr(model, "predict_proba"):
            _ = model.predict_proba(sample_1k)
        elif hasattr(model, "predict"):
            _ = model.predict(sample_1k)
        times.append((time.time() - t0) * 1000.0)  # ms

    mean_ms = float(np.mean(times))
    std_ms = float(np.std(times))

    return {
        "mean_latency_ms_per_1k": round(mean_ms, 3),
        "std_latency_ms_per_1k": round(std_ms, 3),
    }


def test_seed_sensitivity(
    model_builder_fn: callable,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    seeds: list[int] | None = None,
) -> dict[str, float]:
    """Evaluate performance variance across 5 different random seeds."""
    if seeds is None:
        seeds = [42, 100, 2023, 777, 999]

    auc_scores = []
    for seed in seeds:
        res = model_builder_fn(X_train, y_train, seed=seed)
        model = res["model"]
        if hasattr(model, "predict_proba"):
            preds = model.predict_proba(X_test)[:, 1]
        else:
            preds = model.predict(X_test)
        auc_scores.append(roc_auc_score(y_test, preds))

    return {
        "mean_seed_auc": round(float(np.mean(auc_scores)), 4),
        "std_seed_auc": round(float(np.std(auc_scores)), 5),
        "min_seed_auc": round(float(np.min(auc_scores)), 4),
        "max_seed_auc": round(float(np.max(auc_scores)), 4),
    }
