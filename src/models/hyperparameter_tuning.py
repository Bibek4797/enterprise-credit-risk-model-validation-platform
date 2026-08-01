"""Optuna hyperparameter optimization framework for enterprise machine learning models.

Automates hyperparameter search for XGBoost, LightGBM, CatBoost, and Random Forest,
logging search histories, trial execution times, and validation ROC-AUC scores.
"""

from __future__ import annotations

import logging
import time
import pandas as pd
from sklearn.metrics import roc_auc_score

logger = logging.getLogger(__name__)


def optimize_xgboost_optuna(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_trials: int = 15,
    random_state: int = 42,
) -> dict[str, object]:
    """Tune XGBoost hyperparameters using Optuna over validation ROC-AUC."""
    import optuna
    from xgboost import XGBClassifier
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    history = []

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 300),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "gamma": trial.suggest_float("gamma", 0.0, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
        }
        t0 = time.time()
        model = XGBClassifier(**params, eval_metric="logloss", random_state=random_state, n_jobs=-1)
        model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        preds = model.predict_proba(X_val)[:, 1]
        score = float(roc_auc_score(y_val, preds))
        duration = time.time() - t0

        history.append({
            "trial": trial.number,
            "val_auc": score,
            "duration_sec": round(duration, 3),
            **params,
        })
        return score

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=random_state))
    study.optimize(objective, n_trials=n_trials)

    return {
        "best_params": study.best_params,
        "best_val_auc": float(study.best_value),
        "history_df": pd.DataFrame(history).sort_values("val_auc", ascending=False).reset_index(drop=True),
    }


def optimize_lightgbm_optuna(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_trials: int = 15,
    random_state: int = 42,
) -> dict[str, object]:
    """Tune LightGBM hyperparameters using Optuna."""
    import optuna
    from lightgbm import LGBMClassifier
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    history = []

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 300),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 15, 63),
            "max_depth": trial.suggest_int("max_depth", 3, 10),
            "min_child_samples": trial.suggest_int("min_child_samples", 20, 100),
            "subsample": trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        }
        t0 = time.time()
        model = LGBMClassifier(**params, random_state=random_state, n_jobs=-1, verbose=-1)
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_val)[:, 1]
        score = float(roc_auc_score(y_val, preds))
        duration = time.time() - t0

        history.append({
            "trial": trial.number,
            "val_auc": score,
            "duration_sec": round(duration, 3),
            **params,
        })
        return score

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=random_state))
    study.optimize(objective, n_trials=n_trials)

    return {
        "best_params": study.best_params,
        "best_val_auc": float(study.best_value),
        "history_df": pd.DataFrame(history).sort_values("val_auc", ascending=False).reset_index(drop=True),
    }


def optimize_catboost_optuna(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    n_trials: int = 15,
    random_state: int = 42,
) -> dict[str, object]:
    """Tune CatBoost hyperparameters using Optuna."""
    import optuna
    from catboost import CatBoostClassifier
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    history = []

    def objective(trial: optuna.Trial) -> float:
        params = {
            "iterations": trial.suggest_int("iterations", 100, 300),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True),
            "depth": trial.suggest_int("depth", 4, 8),
            "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1.0, 10.0),
        }
        t0 = time.time()
        model = CatBoostClassifier(**params, random_seed=random_state, verbose=False)
        model.fit(X_train, y_train)
        preds = model.predict_proba(X_val)[:, 1]
        score = float(roc_auc_score(y_val, preds))
        duration = time.time() - t0

        history.append({
            "trial": trial.number,
            "val_auc": score,
            "duration_sec": round(duration, 3),
            **params,
        })
        return score

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=random_state))
    study.optimize(objective, n_trials=n_trials)

    return {
        "best_params": study.best_params,
        "best_val_auc": float(study.best_value),
        "history_df": pd.DataFrame(history).sort_values("val_auc", ascending=False).reset_index(drop=True),
    }
