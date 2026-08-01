"""Unit tests for feature engineering, WoE/IV, and stability modules."""

import pytest
import numpy as np
import pandas as pd

from features.woe_iv import calculate_woe_iv, transform_to_woe
from features.stability import calculate_psi


@pytest.fixture
def synthetic_credit_df():
    np.random.seed(42)
    n = 200
    return pd.DataFrame({
        "int_rate": np.random.uniform(5, 25, n),
        "annual_inc": np.random.uniform(20000, 150000, n),
        "target": np.random.choice([0, 1], size=n, p=[0.8, 0.2]),
    })


def test_calculate_woe_iv(synthetic_credit_df):
    res = calculate_woe_iv(synthetic_credit_df, feature="int_rate", target="target", bins=5)
    assert "woe_table" in res
    assert "total_iv" in res
    assert isinstance(res["total_iv"], float)
    assert len(res["woe_table"]) > 0


def test_transform_to_woe(synthetic_credit_df):
    res = calculate_woe_iv(synthetic_credit_df, feature="int_rate", target="target", bins=5)
    woe_map = dict(zip(res["woe_table"]["bin"], res["woe_table"]["woe"]))
    
    df_woe = transform_to_woe(synthetic_credit_df, {"int_rate": woe_map})
    assert "int_rate_woe" in df_woe.columns
    assert df_woe["int_rate_woe"].isna().sum() == 0


def test_calculate_psi():
    exp = pd.Series(np.random.uniform(10, 20, 100))
    act = pd.Series(np.random.uniform(10, 20, 100))
    psi_val = calculate_psi(exp, act, bins=5)
    assert isinstance(psi_val, float)
    assert psi_val >= 0.0
