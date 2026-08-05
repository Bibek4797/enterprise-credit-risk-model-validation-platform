"""Cached Model Loader utility for Dashboard pages."""

from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path.cwd() / "src"))

from models.logistic_model import fit_logistic_regression, predict_logistic
from models.boosting_models import fit_lightgbm
from features.woe_iv import calculate_woe_iv, transform_to_woe


@st.cache_resource(ttl=7200)
def load_trained_models(df: pd.DataFrame) -> dict[str, object]:
    """Fit and cache Champion Statistical & Machine Learning models for interactive inference."""
    features_to_bin = ["int_rate", "annual_inc", "dti", "fico_range_low", "revol_util", "inq_last_6mths"]

    # WoE Transformation for Logistic Scorecard
    woe_maps = {}
    for feat in features_to_bin:
        if feat in df.columns:
            res = calculate_woe_iv(df, feature=feat, target="target", bins=8)
            woe_maps[feat] = dict(zip(res["woe_table"]["bin"], res["woe_table"]["woe"]))

    df_woe = transform_to_woe(df, woe_maps)
    woe_cols = [f"{f}_woe" for f in features_to_bin if f"{f}_woe" in df_woe.columns]

    # Fit Champion Logistic Scorecard
    is_sklearn_fallback = False
    try:
        logit_model = fit_logistic_regression(df_woe[woe_cols], df_woe["target"])
    except Exception:
        is_sklearn_fallback = True
        from sklearn.linear_model import LogisticRegression
        sk_model = LogisticRegression(C=1e5, solver="lbfgs", max_iter=500)
        sk_model.fit(df_woe[woe_cols].fillna(0), df_woe["target"])

        class SklearnWrapper:
            def __init__(self, m, cols):
                self.m = m
                self.cols = cols
            def predict(self, X):
                return self.m.predict_proba(X[self.cols].fillna(0))[:, 1]

        sk_wrapper = SklearnWrapper(sk_model, woe_cols)
        summary_tbl = pd.DataFrame({"feature": woe_cols, "coef": sk_model.coef_[0], "odds_ratio": np.exp(sk_model.coef_[0])})
        logit_model = {"model_result": sk_wrapper, "summary_table": summary_tbl}

    # Fit Champion LightGBM Classifier
    lgb_cols = [c for c in features_to_bin if c in df.columns]
    lgb_model = fit_lightgbm(df[lgb_cols], df["target"], n_estimators=100, learning_rate=0.05)

    def predict_scorecard(df_input: pd.DataFrame) -> np.ndarray:
        df_t = transform_to_woe(df_input, woe_maps)
        if is_sklearn_fallback:
            return logit_model["model_result"].predict(df_t)
        else:
            return predict_logistic(logit_model, df_t[woe_cols].fillna(0))

    def predict_lgb(df_input: pd.DataFrame) -> np.ndarray:
        return lgb_model["model"].predict_proba(df_input[lgb_cols].fillna(0))[:, 1]

    return {
        "logit_dict": logit_model,
        "lgb_dict": lgb_model,
        "woe_maps": woe_maps,
        "predict_scorecard": predict_scorecard,
        "predict_lgb": predict_lgb,
        "features": lgb_cols,
    }
