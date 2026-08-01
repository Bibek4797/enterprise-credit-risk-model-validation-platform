"""Unit tests for model metrics and independent validation functions."""

import pytest
import numpy as np

from validation.model_metrics import evaluate_binary_model
from validation.model_validation import run_bootstrap_validation


def test_evaluate_binary_model():
    y_true = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_prob = np.array([0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9])

    metrics = evaluate_binary_model(y_true, y_prob)

    assert metrics["roc_auc"] == 1.0
    assert metrics["gini_index"] == 1.0
    assert metrics["ks_statistic_pct"] == 100.0
    assert "brier_score" in metrics


def test_bootstrap_validation():
    y_true = np.array([0, 0, 0, 1, 1, 1] * 10)
    y_prob = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9] * 10)

    boot_df = run_bootstrap_validation(y_true, y_prob, n_bootstraps=20)
    assert "metric" in boot_df.columns
    assert "mean" in boot_df.columns
    assert "ci_lower_95" in boot_df.columns
    assert "ci_upper_95" in boot_df.columns
