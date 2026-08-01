"""Model Packaging, Artifact Persistence, Versioning, and Metadata Management."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

logger = logging.getLogger(__name__)


def save_model_artifact(
    model_object: object,
    metadata: dict[str, object],
    output_dir: str | Path = "models",
    model_name: str = "champion_scorecard_v1",
) -> tuple[Path, Path]:
    """Package and persist model object alongside JSON metadata header."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    joblib_file = out_path / f"{model_name}.joblib"
    json_file = out_path / f"{model_name}_metadata.json"

    # Save model artifact
    joblib.dump(model_object, joblib_file)

    # Enrich metadata
    full_meta = {
        "model_name": model_name,
        "saved_at_utc": datetime.now(timezone.utc).isoformat(),
        "framework": "scikit-learn / statsmodels",
        **metadata,
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(full_meta, f, indent=2)

    logger.info(f"Saved model artifact to {joblib_file} and metadata to {json_file}")
    return joblib_file, json_file


def load_model_artifact(model_file: str | Path) -> tuple[object, dict[str, object]]:
    """Load model artifact and associated JSON metadata header."""
    j_path = Path(model_file)
    if not j_path.is_file():
        raise FileNotFoundError(f"Model artifact not found at {j_path}")

    model_obj = joblib.load(j_path)

    # Attempt to load matching metadata
    json_path = j_path.with_name(f"{j_path.stem}_metadata.json")
    metadata = {}
    if json_path.is_file():
        with open(json_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    return model_obj, metadata
