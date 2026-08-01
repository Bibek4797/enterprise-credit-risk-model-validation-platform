"""Data Drift and Concept Drift Audit Engine using non-parametric statistical tests."""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


def ks_two_sample_drift_test(
    baseline_series: pd.Series | np.ndarray,
    current_series: pd.Series | np.ndarray,
    alpha: float = 0.05,
) -> dict[str, float | str | bool]:
    """Perform Kolmogorov-Smirnov 2-sample test to detect numerical feature distribution drift."""
    b_clean = np.asarray(baseline_series, dtype=float)
    c_clean = np.asarray(current_series, dtype=float)

    b_clean = b_clean[~np.isnan(b_clean)]
    c_clean = c_clean[~np.isnan(c_clean)]

    if len(b_clean) == 0 or len(c_clean) == 0:
        return {"ks_statistic": np.nan, "p_value": np.nan, "is_drift_detected": False}

    ks_res = stats.ks_2samp(b_clean, c_clean)
    is_drift = bool(ks_res.pvalue < alpha)

    return {
        "ks_statistic": round(float(ks_res.statistic), 4),
        "p_value": round(float(ks_res.pvalue), 6),
        "is_drift_detected": is_drift,
        "drift_status": "DRIFT DETECTED" if is_drift else "STABLE (No Drift)",
    }


def audit_concept_and_calibration_drift(
    baseline_prob: np.ndarray | pd.Series,
    current_prob: np.ndarray | pd.Series,
    baseline_target: np.ndarray | pd.Series | None = None,
    current_target: np.ndarray | pd.Series | None = None,
) -> dict[str, float | str]:
    """Audit prediction distribution shift and observed default rate calibration drift."""
    base_mean_p = float(np.mean(baseline_prob))
    curr_mean_p = float(np.mean(current_prob))

    prob_shift_pct = ((curr_mean_p - base_mean_p) / (base_mean_p + 1e-6)) * 100.0

    res = {
        "baseline_mean_predicted_pd": round(base_mean_p * 100.0, 2),
        "current_mean_predicted_pd": round(curr_mean_p * 100.0, 2),
        "probability_shift_pct": round(float(prob_shift_pct), 2),
    }

    if baseline_target is not None and current_target is not None:
        base_obs_rate = float(np.mean(baseline_target))
        curr_obs_rate = float(np.mean(current_target))

        base_cal_error = abs(base_obs_rate - base_mean_p)
        curr_cal_error = abs(curr_obs_rate - curr_mean_p)

        res.update({
            "baseline_observed_default_rate": round(base_obs_rate * 100.0, 2),
            "current_observed_default_rate": round(curr_obs_rate * 100.0, 2),
            "baseline_calibration_error": round(base_cal_error * 100.0, 2),
            "current_calibration_error": round(curr_cal_error * 100.0, 2),
            "calibration_drift_status": "HIGH DRIFT" if curr_cal_error > 0.05 else "STABLE",
        })

    return res
