"""Chunked, reproducible, application-time feature engineering pipeline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from features.aggregation_features import add_aggregation_features
from features.behaviour_features import add_behaviour_features
from features.categorical_features import add_categorical_features
from features.feature_validation import validate_features
from features.financial_features import add_financial_features
from features.interaction_features import add_interaction_features
from features.time_features import add_time_features

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "accepted_2007_to_2018Q4.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "accepted_2007_to_2018Q4_feature_engineered.csv.gz"
VALIDATION_PATH = ROOT / "reports" / "feature_validation_summary.csv"
MANIFEST_PATH = ROOT / "reports" / "feature_engineering_manifest.json"

POST_ORIGINATION_PREFIXES = ("out_prncp", "total_pymnt", "total_rec", "recover", "collection_recovery", "last_pymnt", "next_pymnt", "last_credit_pull", "hardship", "payment_plan", "settlement", "debt_settlement")

def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Create application-time candidate features while retaining all source columns."""
    result = frame.copy()
    for transformer in (add_categorical_features, add_time_features, add_financial_features, add_aggregation_features, add_behaviour_features, add_interaction_features):
        result = transformer(result)
    return result

def run_pipeline(chunksize: int = 50_000, overwrite: bool = False) -> dict[str, object]:
    """Process every raw row in chunks and save a separate gzip-compressed CSV."""
    if not RAW_PATH.is_file():
        raise FileNotFoundError(f"Missing raw source: {RAW_PATH}")
    if OUTPUT_PATH.exists() and not overwrite:
        raise FileExistsError(f"Output already exists: {OUTPUT_PATH}. Use overwrite=True only for an approved rerun.")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    if OUTPUT_PATH.exists(): OUTPUT_PATH.unlink()
    validation = []
    rows = 0; first = True; source_columns: list[str] = []; feature_columns: list[str] = []
    for raw_chunk in pd.read_csv(RAW_PATH, chunksize=chunksize, low_memory=False):
        source_columns = raw_chunk.columns.tolist()
        engineered = build_features(raw_chunk)
        feature_columns = [column for column in engineered.columns if column.startswith("fe_")]
        validation.append(validate_features(engineered))
        engineered.to_csv(OUTPUT_PATH, index=False, mode="w" if first else "a", header=first, compression={"method": "gzip", "compresslevel": 1})
        first = False; rows += len(engineered)
    checks = pd.concat(validation, ignore_index=True).groupby(["feature", "dtype"], dropna=False).agg(missing_count=("missing_count", "sum"), infinite_count=("infinite_count", "sum"), min=("min", "min"), max=("max", "max"), unique_count_chunk_sum=("unique_count", "sum")).reset_index()
    checks["missing_pct"] = (checks["missing_count"] / rows * 100).round(4)
    checks.to_csv(VALIDATION_PATH, index=False)
    manifest = {"raw_source": str(RAW_PATH), "processed_output": str(OUTPUT_PATH), "raw_rows": rows, "raw_columns_retained": len(source_columns), "engineered_feature_count": len(feature_columns), "engineered_features": feature_columns, "post_origination_fields_not_used_for_engineering": [c for c in source_columns if c.lower().startswith(POST_ORIGINATION_PREFIXES)]}
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunksize", type=int, default=50_000)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_pipeline(args.chunksize, args.overwrite), indent=2))
