"""Smoke test for Dashboard data and model loaders."""

import pytest
import pandas as pd
from dashboard.utils.data_loader import load_credit_data
from dashboard.utils.model_loader import load_trained_models


def test_dashboard_data_loader():
    df = load_credit_data(sample_size=200)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "target" in df.columns


def test_dashboard_model_loader():
    df = load_credit_data(sample_size=300)
    models = load_trained_models(df)
    assert "predict_scorecard" in models
    assert "predict_lgb" in models

    sc_preds = models["predict_scorecard"](df)
    lgb_preds = models["predict_lgb"](df)

    assert len(sc_preds) == len(df)
    assert len(lgb_preds) == len(df)
