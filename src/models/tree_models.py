"""Enterprise tree-based machine learning models for credit risk.

Wrappers for Decision Tree, Random Forest, and Extra Trees classifiers
with feature importance extraction, Out-of-Bag (OOB) scoring, and pruning controls.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

logger = logging.getLogger(__name__)


def fit_decision_tree(
    X_train: pd.DataFrame,
    y_train: pd.Series | np.ndarray,
    max_depth: int | None = 6,
    min_samples_leaf: int = 50,
    ccp_alpha: float = 0.0,
    random_state: int = 42,
) -> dict[str, object]:
    """Fit a pruned Decision Tree classifier and extract tree depth and feature importances."""
    dt = DecisionTreeClassifier(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        ccp_alpha=ccp_alpha,
        random_state=random_state,
    )
    dt.fit(X_train, y_train)

    importance_df = pd.DataFrame({
        "feature": X_train.columns,
        "importance": dt.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    return {
        "model": dt,
        "max_depth": dt.get_depth(),
        "n_leaves": dt.get_n_leaves(),
        "feature_importances": importance_df,
    }


def fit_random_forest(
    X_train: pd.DataFrame,
    y_train: pd.Series | np.ndarray,
    n_estimators: int = 150,
    max_depth: int | None = 12,
    min_samples_leaf: int = 30,
    max_features: str | float = "sqrt",
    oob_score: bool = True,
    random_state: int = 42,
    n_jobs: int = -1,
) -> dict[str, object]:
    """Fit a Random Forest ensemble model and compute OOB score and Gini importances."""
    rf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        oob_score=oob_score,
        random_state=random_state,
        n_jobs=n_jobs,
    )
    rf.fit(X_train, y_train)

    importance_df = pd.DataFrame({
        "feature": X_train.columns,
        "importance": rf.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    return {
        "model": rf,
        "oob_score": float(rf.oob_score_) if oob_score else None,
        "n_estimators": n_estimators,
        "feature_importances": importance_df,
    }


def fit_extra_trees(
    X_train: pd.DataFrame,
    y_train: pd.Series | np.ndarray,
    n_estimators: int = 150,
    max_depth: int | None = 12,
    min_samples_leaf: int = 30,
    max_features: str | float = "sqrt",
    random_state: int = 42,
    n_jobs: int = -1,
) -> dict[str, object]:
    """Fit an Extra Trees ensemble model."""
    et = ExtraTreesClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        max_features=max_features,
        random_state=random_state,
        n_jobs=n_jobs,
    )
    et.fit(X_train, y_train)

    importance_df = pd.DataFrame({
        "feature": X_train.columns,
        "importance": et.feature_importances_,
    }).sort_values("importance", ascending=False).reset_index(drop=True)

    return {
        "model": et,
        "n_estimators": n_estimators,
        "feature_importances": importance_df,
    }
