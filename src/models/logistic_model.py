"""Production-grade Logistic Regression model wrapper for enterprise credit risk scorecards.

Provides full statistical inference, Odds Ratio calculation, Wald statistics,
Likelihood Ratio tests, McFadden Pseudo R-squared, AIC, BIC, and confidence intervals.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)


def fit_logistic_regression(
    X: pd.DataFrame,
    y: pd.Series | np.ndarray,
    add_constant: bool = True,
) -> dict[str, object]:
    """Fit Statsmodels Logit model and return model object, summary table, and fit diagnostics."""
    X_input = X.copy()
    if add_constant and "const" not in X_input.columns:
        X_input = sm.add_constant(X_input)

    model = sm.Logit(y, X_input)
    result = model.fit(disp=False, maxiter=200)

    # Coefficient Summary Table
    conf_int = result.conf_int()
    summary_df = pd.DataFrame({
        "feature": X_input.columns,
        "coefficient": result.params.values,
        "std_error": result.bse.values,
        "z_statistic": result.tvalues.values if hasattr(result, "tvalues") else result.params.values / result.bse.values,
        "p_value": result.pvalues.values,
        "ci_lower_95": conf_int[0].values,
        "ci_upper_95": conf_int[1].values,
        "odds_ratio": np.exp(result.params.values),
        "or_ci_lower_95": np.exp(conf_int[0].values),
        "or_ci_upper_95": np.exp(conf_int[1].values),
    })

    # Fit Diagnostics
    null_ll = result.llnull
    model_ll = result.llf
    mcfadden_r2 = 1.0 - (model_ll / null_ll)
    llr_pvalue = result.llr_pvalue

    fit_metrics = {
        "log_likelihood": round(float(model_ll), 4),
        "null_log_likelihood": round(float(null_ll), 4),
        "llr_pvalue": round(float(llr_pvalue), 6),
        "mcfadden_pseudo_r2": round(float(mcfadden_r2), 4),
        "aic": round(float(result.aic), 2),
        "bic": round(float(result.bic), 2),
        "n_obs": int(result.nobs),
        "df_model": int(result.df_model),
    }

    return {
        "model_result": result,
        "summary_table": summary_df,
        "fit_metrics": fit_metrics,
        "features": list(X_input.columns),
    }


def predict_logistic(
    fitted_model_dict: dict[str, object],
    X: pd.DataFrame,
) -> np.ndarray:
    """Generate probability of default predictions using fitted Logit model."""
    result = fitted_model_dict["model_result"]
    X_input = X.copy()
    if "const" not in X_input.columns and "const" in fitted_model_dict["features"]:
        X_input = sm.add_constant(X_input)

    return result.predict(X_input)
