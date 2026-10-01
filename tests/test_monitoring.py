"""Unit tests for Population Stability (PSI), CSI, Data Drift, and Retraining Triggers."""

import pytest
import numpy as np
import pandas as pd

from monitoring.psi import calculate_array_psi
from monitoring.csi import calculate_feature_csi
from monitoring.drift import ks_two_sample_drift_test
from monitoring.retraining import evaluate_retraining_triggers


def test_calculate_array_psi():
    exp = np.random.normal(10, 2, 500)
    act = np.random.normal(10, 2, 500)

    res = calculate_array_psi(exp, act, num_bins=10)
    assert "psi_value" in res
    assert "status" in res
    assert res["psi_value"] < 0.10
    assert "GREEN" in res["status"]


def test_ks_two_sample_drift_test():
    b = np.random.uniform(0, 1, 100)
    c = np.random.uniform(0, 1, 100)

    res = ks_two_sample_drift_test(b, c)
    assert "ks_statistic" in res
    assert "p_value" in res
    assert "is_drift_detected" in res


def test_evaluate_retraining_triggers():
    res_green = evaluate_retraining_triggers(psi_value=0.04, current_auc=0.7245, baseline_auc=0.7285, current_ks_pct=34.8)
    assert res_green["traffic_light_status"] == "GREEN"

    res_red = evaluate_retraining_triggers(psi_value=0.28, current_auc=0.6500, baseline_auc=0.7285, current_ks_pct=25.0)
    assert res_red["traffic_light_status"] == "RED"
    assert res_red["is_retraining_required"] is True


def test_calculate_feature_csi_numeric_and_categorical():
    from monitoring.csi import build_portfolio_csi_report

    # Numeric
    exp_num = pd.Series(np.random.normal(50, 10, 500))
    act_num = pd.Series(np.random.normal(50, 10, 500))
    res_num = calculate_feature_csi(exp_num, act_num, "annual_inc")
    assert res_num["feature_type"] == "Numeric"
    assert "csi_value" in res_num
    assert res_num["csi_value"] < 0.10

    # Categorical
    exp_cat = pd.Series(["RENT", "OWN", "MORTGAGE"] * 100)
    act_cat = pd.Series(["RENT", "OWN", "MORTGAGE"] * 100)
    res_cat = calculate_feature_csi(exp_cat, act_cat, "home_ownership")
    assert res_cat["feature_type"] == "Categorical"
    assert "csi_value" in res_cat
    assert res_cat["csi_value"] < 0.10

    # Portfolio report
    df_exp = pd.DataFrame({"annual_inc": exp_num, "home_ownership": exp_cat})
    df_act = pd.DataFrame({"annual_inc": act_num, "home_ownership": act_cat})
    csi_df = build_portfolio_csi_report(df_exp, df_act, ["annual_inc", "home_ownership"])
    assert len(csi_df) == 2
    assert "feature_name" in csi_df.columns
    assert "csi_value" in csi_df.columns

