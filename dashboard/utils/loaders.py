"""Cached Data and Model Loaders Utility Module."""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import streamlit as st

sys.path.append(str(Path.cwd() / "dashboard"))

from utils.data_loader import load_credit_data as _load_credit_data
from utils.model_loader import load_trained_models as _load_trained_models


@st.cache_data(ttl=3600)
def load_credit_data(sample_size: int | None = 30000) -> pd.DataFrame:
    """Cached credit dataset loader."""
    return _load_credit_data(sample_size=sample_size)


@st.cache_resource(ttl=7200)
def load_trained_models(df: pd.DataFrame) -> dict[str, object]:
    """Cached model loader for Scorecard and LightGBM models."""
    return _load_trained_models(df)
