"""Business-consistent category normalisation and ordinal risk bands."""
from __future__ import annotations
import pandas as pd

def add_categorical_features(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    fico = (pd.to_numeric(df.get("fico_range_low"), errors="coerce") + pd.to_numeric(df.get("fico_range_high"), errors="coerce")) / 2
    df["fe_fico_midpoint"] = fico
    df["fe_fico_risk_band"] = pd.cut(fico, [-float("inf"), 660, 700, 740, 780, float("inf")], labels=["subprime", "near_prime", "prime", "super_prime", "exceptional"])
    grade = df.get("grade", pd.Series(index=df.index, dtype="object")).astype("string")
    df["fe_grade_ordinal"] = grade.map({"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}).astype("Int8")
    emp = df.get("emp_length", pd.Series(index=df.index, dtype="object")).astype("string")
    df["fe_employment_known_flag"] = emp.notna().astype("Int8")
    return df
