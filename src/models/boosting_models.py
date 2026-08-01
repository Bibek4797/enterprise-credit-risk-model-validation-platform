"""Enterprise Gradient Boosting models for credit risk (XGBoost, LightGBM, CatBoost).

Supports early stopping, class weighting, feature importance extraction,
and high-performance prediction generation.
"""

from __future__ import annotations

import logging
import time
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def fit_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series | np.ndarray,
    X_val: pd.DataFrame | None = None,
    y_val: pd.Series | np.ndarray | None = None,
    n_estimators: int = 200,
    learning_rate: float = 0.05,
    max_depth: int = 5,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    gamma: float = 0.1,
    reg_alpha: float = 0.1,
    reg_lambda: float = 1.0,
    early_stopping_rounds: int = 20,
    random_state: int = 42,
    n_jobs: int = -1,
) -> dict[str, object]:
    """Fit XGBoost gradient boosting classifier with optional early stopping on validation loss."""
    from xgboost import XGBClassifier

    start_time = time.time()
    model = XGBClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        max_depth=max_depth,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        gamma=gamma,
        reg_alpha=reg_alpha,
        reg_lambda=reg_lambda,
        early_stopping_rounds=early_stopping_rounds if X_val is not None else None,
        eval_metric="logloss",
        random_state=random_state,
        n_jobs=n_jobs,
    )

    eval_set = [(X_val, y_val)] if (X_val is not None and y_val is not None) else None
    model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
    fit_duration = time.time() - start_time

    importance_df = pd.DataFrame({
        "feature": X_train.columns,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    return {
        "model": model,
        "fit_time_seconds": round(fit_duration, 4),
        "best_iteration": getattr(model, "best_iteration", n_estimators),
        "feature_importances": importance_df,
    }


def fit_lightgbm(
    X_train: pd.DataFrame,
    y_train: pd.Series | np.ndarray,
    X_val: pd.DataFrame | None = None,
    y_val: pd.Series | np.ndarray | None = None,
    n_estimators: int = 200,
    learning_rate: float = 0.05,
    num_leaves: int = 31,
    max_depth: int = -1,
    min_child_samples: int = 50,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    early_stopping_rounds: int = 20,
    random_state: int = 42,
    n_jobs: int = -1,
) -> dict[str, object]:
    """Fit LightGBM gradient boosting classifier."""
    from lightgbm import LGBMClassifier

    start_time = time.time()
    model = LGBMClassifier(
        n_estimators=n_estimators,
        learning_rate=learning_rate,
        num_leaves=num_leaves,
        max_depth=max_depth,
        min_child_samples=min_child_samples,
        subsample=subsample,
        colsample_bytree=colsample_bytree,
        random_state=random_state,
        n_jobs=n_jobs,
        verbose=-1,
    )

    if X_val is not None and y_val is not None:
        import lightgbm as lgb
        callbacks = [lgb.early_stopping(stopping_rounds=early_stopping_rounds, verbose=False)]
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], callbacks=callbacks)
    else:
        model.fit(X_train, y_train)

    fit_duration = time.time() - start_time

    importance_df = pd.DataFrame({
        "feature": X_train.columns,
        "importance": model.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    return {
        "model": model,
        "fit_time_seconds": round(fit_duration, 4),
        "feature_importances": importance_df,
    }


def fit_catboost(
    X_train: pd.DataFrame,
    y_train: pd.Series | np.ndarray,
    X_val: pd.DataFrame | None = None,
    y_val: pd.Series | np.ndarray | None = None,
    iterations: int = 200,
    learning_rate: float = 0.05,
    depth: int = 6,
    l2_leaf_reg: float = 3.0,
    early_stopping_rounds: int = 20,
    random_state: int = 42,
) -> dict[str, object]:
    """Fit CatBoost gradient boosting classifier."""
    from catboost import CatBoostClassifier

    start_time = time.time()
    model = CatBoostClassifier(
        iterations=iterations,
        learning_rate=learning_rate,
        depth=depth,
        l2_leaf_reg=l2_leaf_reg,
        early_stopping_rounds=early_stopping_rounds if X_val is not None else None,
        random_seed=random_state,
        verbose=False,
    )

    eval_set = (X_val, y_val) if (X_val is not None and y_val is not None) else None
    model.fit(X_train, y_train, eval_set=eval_set, verbose=False)
    fit_duration = time.time() - start_time

    importance_df = pd.DataFrame({
        "feature": X_train.columns,
        "importance": model.get_feature_importance(),
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    return {
        "model": model,
        "fit_time_seconds": round(fit_duration, 4),
        "feature_importances": importance_df,
    }
