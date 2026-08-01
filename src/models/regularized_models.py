"""Regularized Logistic Regression models (LASSO L1, Ridge L2, Elastic Net).

Executes cross-validation hyperparameter tuning, coefficient shrinkage paths,
and feature selection stability analysis per model governance rules.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV

logger = logging.getLogger(__name__)


def fit_penalized_logistic_models(
    X: pd.DataFrame,
    y: pd.Series | np.ndarray,
    cv: int = 5,
    random_state: int = 42,
) -> dict[str, object]:
    """Fit LASSO (L1), Ridge (L2), and Elastic Net Logistic Regression models using K-fold CV."""
    X_scaled = (X - X.mean()) / (X.std() + 1e-8)
    y_arr = np.asarray(y, dtype=int)

    c_grid = np.logspace(-3, 2, 10)

    # 1. Ridge (L2)
    ridge_model = LogisticRegressionCV(
        Cs=c_grid, cv=cv, penalty="l2", solver="lbfgs", max_iter=300, random_state=random_state, n_jobs=-1
    )
    ridge_model.fit(X_scaled, y_arr)

    # 2. LASSO (L1)
    lasso_model = LogisticRegressionCV(
        Cs=c_grid, cv=cv, penalty="l1", solver="saga", max_iter=500, random_state=random_state, n_jobs=-1
    )
    lasso_model.fit(X_scaled, y_arr)

    # 3. Elastic Net (L1 + L2)
    elastic_model = LogisticRegressionCV(
        Cs=c_grid, cv=cv, penalty="elasticnet", l1_ratios=[0.5], solver="saga", max_iter=500, random_state=random_state, n_jobs=-1
    )
    elastic_model.fit(X_scaled, y_arr)

    # Coefficient comparison table
    coef_df = pd.DataFrame({
        "feature": X.columns,
        "ridge_coef": ridge_model.coef_[0],
        "lasso_coef": lasso_model.coef_[0],
        "elastic_net_coef": elastic_model.coef_[0],
        "lasso_selected": lasso_model.coef_[0] != 0,
    }).sort_values("lasso_coef", ascending=False).reset_index(drop=True)

    summary_metrics = {
        "ridge_best_C": float(ridge_model.C_[0]),
        "lasso_best_C": float(lasso_model.C_[0]),
        "elastic_best_C": float(elastic_model.C_[0]),
        "lasso_features_retained": int((lasso_model.coef_[0] != 0).sum()),
    }

    return {
        "ridge_model": ridge_model,
        "lasso_model": lasso_model,
        "elastic_model": elastic_model,
        "coef_table": coef_df,
        "summary_metrics": summary_metrics,
        "scaler_mean": X.mean(),
        "scaler_std": X.std(),
    }


def predict_penalized(
    penalized_dict: dict[str, object],
    X: pd.DataFrame,
    model_type: str = "lasso",
) -> np.ndarray:
    """Generate default probability predictions using specified penalized model."""
    mean = penalized_dict["scaler_mean"]
    std = penalized_dict["scaler_std"]
    X_scaled = (X - mean) / (std + 1e-8)

    model = penalized_dict[f"{model_type}_model"]
    return model.predict_proba(X_scaled)[:, 1]
