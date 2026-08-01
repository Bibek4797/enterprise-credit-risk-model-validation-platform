"""Feature-level data-quality checks for bank-style pipeline controls."""
from __future__ import annotations
import numpy as np
import pandas as pd

def validate_features(frame: pd.DataFrame, feature_prefix: str = "fe_") -> pd.DataFrame:
    rows = []
    for column in [c for c in frame.columns if c.startswith(feature_prefix)]:
        series = frame[column]
        numeric = pd.api.types.is_numeric_dtype(series)
        rows.append({"feature": column, "dtype": str(series.dtype), "missing_count": int(series.isna().sum()), "missing_pct": round(float(series.isna().mean() * 100), 4), "infinite_count": int(np.isinf(series.to_numpy(dtype=float, na_value=np.nan)).sum()) if numeric else 0, "min": float(series.min()) if numeric and series.notna().any() else None, "max": float(series.max()) if numeric and series.notna().any() else None, "unique_count": int(series.nunique(dropna=True))})
    return pd.DataFrame(rows)
