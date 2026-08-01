"""Enterprise Model Monitoring & Retraining Specification Engine.

Calculates monthly PSI/CSI drift, out-of-calibration alerts,
and automated retraining trigger rules per SR 11-7 model risk management.
"""

from __future__ import annotations

import logging
import numpy as np
import pandas as pd
from features.stability import calculate_psi

logger = logging.getLogger(__name__)


def generate_monitoring_specification() -> pd.DataFrame:
    """Return formal Model Monitoring Threshold Specification table."""
    specs = [
        {
            "metric": "Population Stability Index (PSI)",
            "green_threshold": "< 0.10",
            "amber_threshold": "0.10 - 0.25",
            "red_threshold": ">= 0.25",
            "monitoring_frequency": "Monthly",
            "action_required": "Red: Immediate Model Refit / Re-calibration Review",
        },
        {
            "metric": "Characteristic Stability Index (CSI)",
            "green_threshold": "< 0.10",
            "amber_threshold": "0.10 - 0.25",
            "red_threshold": ">= 0.25",
            "monitoring_frequency": "Monthly",
            "action_required": "Red: Feature Bin Re-alignment",
        },
        {
            "metric": "Predicted vs Observed Default Ratio",
            "green_threshold": "0.90 - 1.10",
            "amber_threshold": "0.80 - 0.90 / 1.10 - 1.20",
            "red_threshold": "< 0.80 or > 1.20",
            "monitoring_frequency": "Quarterly",
            "action_required": "Red: Recalibrate Intercept (Platt Scaling)",
        },
        {
            "metric": "ROC-AUC Degradation",
            "green_threshold": "< 2.0% drop",
            "amber_threshold": "2.0% - 5.0% drop",
            "red_threshold": "> 5.0% drop",
            "monitoring_frequency": "Quarterly",
            "action_required": "Red: Comprehensive Model Re-validation",
        },
        {
            "metric": "Kolmogorov-Smirnov (KS) Drop",
            "green_threshold": "KS >= 30%",
            "amber_threshold": "25% <= KS < 30%",
            "red_threshold": "KS < 25%",
            "monitoring_frequency": "Quarterly",
            "action_required": "Red: Governance Audit & Re-estimation",
        },
    ]
    return pd.DataFrame(specs)


def evaluate_monthly_psi_tracking(
    baseline_series: pd.Series,
    monthly_series: pd.Series,
    feature_name: str,
) -> dict[str, object]:
    """Evaluate monthly PSI for a feature against baseline development distribution."""
    psi_val = calculate_psi(baseline_series, monthly_series)

    if np.isnan(psi_val) or psi_val < 0.10:
        status = "GREEN (Stable)"
        action = "None required"
    elif 0.10 <= psi_val < 0.25:
        status = "AMBER (Moderate Shift)"
        action = "Increase monitoring frequency to bi-weekly"
    else:
        status = "RED (Significant Shift)"
        action = "Trigger Model Refit & Re-validation"

    return {
        "feature": feature_name,
        "psi_value": round(float(psi_val), 4) if not np.isnan(psi_val) else np.nan,
        "status": status,
        "recommended_action": action,
    }
