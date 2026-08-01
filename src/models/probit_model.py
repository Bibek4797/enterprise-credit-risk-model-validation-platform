"""Probit Regression model wrapper and marginal effects calculator for credit risk benchmarking.

Fits Statsmodels Probit model, computes Average Marginal Effects (AME),
and evaluates scaling factor comparisons against Logistic Regression.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
import statsmodels.api as sm

logger = logging.getLogger(__name__)


def fit_probit_regression(
    X: pd.DataFrame,
    y: pd.Series | np.ndarray,
    add_constant: bool = True,
) -> dict[str, object]:
    """Fit Statsmodels Probit model and return coefficients, marginal effects, and fit diagnostics."""
    X_input = X.copy()
    if add_constant and "const" not in X_input.columns:
        X_input = sm.add_constant(X_input)

    model = sm.Probit(y, X_input)
    result = model.fit(disp=False, maxiter=200)

    # Calculate Average Marginal Effects (AME): AME_j = mean(phi(X*beta)) * beta_j
    lin_pred = result.predict(which="linear")  # X * beta
    phi_val = (1.0 / np.sqrt(2.0 * np.pi)) * np.exp(-0.5 * (lin_pred ** 2))
    scale_factor = float(np.mean(phi_val))
    ame_values = result.params.values * scale_factor
    ame_std_err = result.bse.values * scale_factor

    # Coefficient Summary Table
    conf_int = result.conf_int()
    summary_df = pd.DataFrame({
        "feature": X_input.columns,
        "probit_coefficient": result.params.values,
        "std_error": result.bse.values,
        "z_statistic": result.tvalues.values if hasattr(result, "tvalues") else result.params.values / result.bse.values,
        "p_value": result.pvalues.values,
        "ci_lower_95": conf_int[0].values,
        "ci_upper_95": conf_int[1].values,
        "marginal_effect_ame": ame_values,
        "ame_std_err": ame_std_err,
    })

    # Fit Diagnostics
    null_ll = result.llnull
    model_ll = result.llf
    mcfadden_r2 = 1.0 - (model_ll / null_ll)

    fit_metrics = {
        "log_likelihood": round(float(model_ll), 4),
        "null_log_likelihood": round(float(null_ll), 4),
        "mcfadden_pseudo_r2": round(float(mcfadden_r2), 4),
        "aic": round(float(result.aic), 2),
        "bic": round(float(result.bic), 2),
        "n_obs": int(result.nobs),
    }

    return {
        "model_result": result,
        "summary_table": summary_df,
        "fit_metrics": fit_metrics,
        "features": list(X_input.columns),
    }


def compare_logistic_probit(
    logit_summary: pd.DataFrame,
    probit_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Construct side-by-side comparison table of Logistic vs Probit coefficients and scaling ratios."""
    merged = pd.merge(
        logit_summary[["feature", "coefficient", "odds_ratio", "p_value"]],
        probit_summary[["feature", "probit_coefficient", "marginal_effect_ame", "p_value"]],
        on="feature",
        suffixes=("_logit", "_probit"),
    )

    # Scaling ratio (Logistic beta / Probit beta, theoretically ~ 1.60)
    merged["logit_probit_ratio"] = (
        merged["coefficient"] / (merged["probit_coefficient"] + 1e-8)
    ).round(4)

    return merged
