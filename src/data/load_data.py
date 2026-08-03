"""Read-only, chunked loaders and profilers for LendingClub source files."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator

import pandas as pd


REQUIRED_RAW_FILES = (
    "accepted_2007_to_2018Q4.csv",
)


@dataclass(frozen=True)
class RawFileStatus:
    """Availability and size metadata for an expected raw source file."""

    name: str
    path: str
    exists: bool
    size_bytes: int | None


def raw_file_status(raw_dir: str | Path) -> list[RawFileStatus]:
    """Return expected-source availability without reading or changing file contents."""

    base_path = Path(raw_dir)
    return [
        RawFileStatus(
            name=name,
            path=str(base_path / name),
            exists=(base_path / name).is_file(),
            size_bytes=(base_path / name).stat().st_size if (base_path / name).is_file() else None,
        )
        for name in REQUIRED_RAW_FILES
    ]


def iter_csv_chunks(path: str | Path, chunksize: int = 100_000) -> Iterator[pd.DataFrame]:
    """Yield CSV chunks without writing to or otherwise modifying the source file."""

    return pd.read_csv(
        Path(path),
        chunksize=chunksize,
        low_memory=False,
        on_bad_lines="warn",
    )


def count_csv_rows(path: str | Path) -> int:
    """Count data rows with the standard-library CSV reader, excluding the header row."""

    with Path(path).open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for _ in reader)


def profile_csv(
    path: str | Path,
    *,
    chunksize: int = 100_000,
    sample_rows: int = 5,
) -> dict[str, Any]:
    """Produce a compact, read-only structural profile of a potentially large CSV file."""

    source = Path(path)
    total_rows = 0
    total_memory_bytes = 0
    missing_counts: Counter[str] = Counter()
    non_null_counts: Counter[str] = Counter()
    distinct_samples: dict[str, set[str]] = {}
    dtype_observations: dict[str, Counter[str]] = {}
    head: pd.DataFrame | None = None
    columns: list[str] = []

    for chunk in iter_csv_chunks(source, chunksize=chunksize):
        if head is None:
            head = chunk.head(sample_rows).copy()
            columns = chunk.columns.tolist()
            distinct_samples = {column: set() for column in columns}
            dtype_observations = {column: Counter() for column in columns}

        total_rows += len(chunk)
        total_memory_bytes += int(chunk.memory_usage(deep=True).sum())
        nulls = chunk.isna().sum()
        missing_counts.update({column: int(value) for column, value in nulls.items()})
        non_null_counts.update({column: int(len(chunk) - value) for column, value in nulls.items()})

        for column, dtype in chunk.dtypes.items():
            dtype_observations[column][str(dtype)] += 1
            values = chunk[column].dropna().astype(str).head(1_000)
            distinct_samples[column].update(values.tolist())
            if len(distinct_samples[column]) > 10_000:
                distinct_samples[column] = set(list(distinct_samples[column])[:10_000])

    if head is None:
        return {
            "file_name": source.name,
            "rows": 0,
            "columns": 0,
            "file_size_bytes": source.stat().st_size,
            "estimated_memory_bytes": 0,
            "column_profile": [],
            "sample_records": [],
        }

    column_profile = [
        {
            "column": column,
            "inferred_dtype": dtype_observations[column].most_common(1)[0][0],
            "missing_count": missing_counts[column],
            "missing_pct": round((missing_counts[column] / total_rows) * 100, 4),
            "non_null_count": non_null_counts[column],
            "distinct_values_sampled": len(distinct_samples[column]),
        }
        for column in columns
    ]
    return {
        "file_name": source.name,
        "rows": total_rows,
        "columns": len(columns),
        "file_size_bytes": source.stat().st_size,
        "estimated_memory_bytes": total_memory_bytes,
        "column_profile": column_profile,
        "sample_records": head.where(pd.notna(head), None).to_dict(orient="records"),
    }


def serialise_status(statuses: list[RawFileStatus]) -> list[dict[str, Any]]:
    """Convert file-status dataclasses to notebook-friendly dictionaries."""

    return [asdict(status) for status in statuses]
