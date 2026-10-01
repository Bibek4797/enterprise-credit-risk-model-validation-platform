"""Cached Model Loader utility for Dashboard pages."""

from __future__ import annotations

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

sys.path.append(str(Path.cwd() / "src"))

from models.logistic_model import fit_logistic_regression
from models.boosting_models import fit_lightgbm
from features.woe_iv import calculate_woe_iv, transform_to_woe
from dashboard.utils.data_loader import SELECTED_29_FEATURES


@st.cache_resource(ttl=7200)
def load_trained_models(df: pd.DataFrame, model_version: str = "v4_29_features_recalibrated") -> dict[str, object]:
    """Fit and cache Champion Statistical & Machine Learning models for interactive inference across 29 features."""
    features_to_bin = [f for f in SELECTED_29_FEATURES if f in df.columns]

    # WoE Transformation across all 29 features
    woe_maps: dict[str, dict[str, float]] = {}
    for feat in features_to_bin:
        try:
            res = calculate_woe_iv(df, feature=feat, target="target", bins=6)
            woe_maps[feat] = dict(zip(res["woe_table"]["bin"], res["woe_table"]["woe"]))
        except Exception:
            pass

    df_woe = transform_to_woe(df, woe_maps)
    woe_cols = [f"{f}_woe" for f in woe_maps.keys() if f"{f}_woe" in df_woe.columns]

    # Fit Champion Logistic Scorecard
    is_sklearn_fallback = False
    try:
        import statsmodels.api as sm
        X_logit = sm.add_constant(df_woe[woe_cols].fillna(0), has_constant="add")
        logit_res = sm.Logit(df_woe["target"], X_logit).fit(disp=False, maxiter=200)
        beta_0 = float(logit_res.params["const"])
        beta_dict = {col: float(logit_res.params[col]) for col in logit_res.params.index if col != "const"}
        logit_model = {"model_result": logit_res}
    except Exception:
        is_sklearn_fallback = True
        from sklearn.linear_model import LogisticRegression
        sk_model = LogisticRegression(C=1.0, solver="lbfgs", max_iter=500)
        sk_model.fit(df_woe[woe_cols].fillna(0), df_woe["target"])

        class SklearnWrapper:
            def __init__(self, m, cols):
                self.m = m
                self.cols = cols
            def predict(self, X):
                cols_present = [c for c in self.cols if c in X.columns]
                return self.m.predict_proba(X[cols_present].fillna(0))[:, 1]

        sk_wrapper = SklearnWrapper(sk_model, woe_cols)
        logit_model = {"model_result": sk_wrapper}
        beta_0 = float(sk_model.intercept_[0])
        beta_dict = {col: float(coef) for col, coef in zip(woe_cols, sk_model.coef_[0])}

    # Ensure dual lookup in beta_dict: both "int_rate" and "int_rate_woe" resolve properly
    for feat in woe_maps.keys():
        wcol = f"{feat}_woe"
        if wcol in beta_dict and feat not in beta_dict:
            beta_dict[feat] = beta_dict[wcol]
        elif feat in beta_dict and wcol not in beta_dict:
            beta_dict[wcol] = beta_dict[feat]

    # Fit Champion LightGBM Classifier across all 29 features
    lgb_cols = [c for c in features_to_bin if c in df.columns]
    X_lgb = df[lgb_cols].copy()
    for col in X_lgb.select_dtypes(include=["object"]).columns:
        X_lgb[col] = X_lgb[col].astype("category")

    lgb_model = fit_lightgbm(X_lgb, df["target"], n_estimators=100, learning_rate=0.05)

    def predict_scorecard(df_input: pd.DataFrame) -> np.ndarray:
        df_t = transform_to_woe(df_input, woe_maps)
        if is_sklearn_fallback:
            return logit_model["model_result"].predict(df_t)
        import statsmodels.api as sm
        X_eval = sm.add_constant(df_t[woe_cols].fillna(0), has_constant="add")
        return logit_model["model_result"].predict(X_eval)

    def predict_lgb(df_input: pd.DataFrame) -> np.ndarray:
        X_eval = df_input[lgb_cols].copy()
        for col in X_eval.select_dtypes(include=["object"]).columns:
            X_eval[col] = X_eval[col].astype("category")
        return lgb_model["model"].predict_proba(X_eval)[:, 1]

    return {
        "features": lgb_cols,
        "woe_maps": woe_maps,
        "logit_dict": logit_model,
        "beta_0": beta_0,
        "beta_dict": beta_dict,
        "lgb_dict": lgb_model,
        "predict_scorecard": predict_scorecard,
        "predict_lgb": predict_lgb,
    }
