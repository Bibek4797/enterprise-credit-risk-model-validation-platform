"""Unit tests for Logistic Scorecard, LightGBM, and Probit Regression wrappers."""

import pytest
import numpy as np
import pandas as pd

from models.logistic_model import fit_logistic_regression, predict_logistic
from models.boosting_models import fit_lightgbm


@pytest.fixture
def model_dataset():
    np.random.seed(42)
    n = 200
    X = pd.DataFrame({
        "f1": np.random.uniform(0, 1, n),
        "f2": np.random.uniform(0, 1, n),
    })
    y = pd.Series(np.random.choice([0, 1], size=n, p=[0.8, 0.2]))
    return X, y


def test_fit_lightgbm(model_dataset):
    X, y = model_dataset
    res = fit_lightgbm(X, y, n_estimators=10)
    assert "model" in res
    assert "feature_importances" in res
    probs = res["model"].predict_proba(X)[:, 1]
    assert len(probs) == len(X)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()


def test_fit_logistic_regression(model_dataset):
    X, y = model_dataset
    res = fit_logistic_regression(X, y)
    assert "summary_table" in res
    probs = predict_logistic(res, X)
    assert len(probs) == len(X)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()
