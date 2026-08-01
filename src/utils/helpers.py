"""Reusable helpers for data-understanding reporting and risk-data screening."""

from __future__ import annotations

from collections.abc import Iterable


LEAKAGE_PATTERNS = (
    "last_pymnt",
    "next_pymnt",
    "last_credit_pull",
    "out_prncp",
    "total_pymnt",
    "total_rec_",
    "recover",
    "collection_recovery",
    "collections_",
    "chargeoff",
    "delinq_2yrs",
    "mths_since_last_delinq",
    "mths_since_last_record",
    "hardship",
    "settlement",
    "debt_settlement",
    "payment_plan",
)

TARGET_CANDIDATE_PATTERNS = (
    "loan_status",
    "default",
    "chargeoff",
    "charged_off",
    "recover",
    "collection",
)


def classify_column_name(column: str) -> str:
    """Return a conservative business grouping based on a field name.

    The output is an initial screening classification; it must be confirmed against
    the data dictionary and a documented observation date.
    """

    name = column.lower()
    if any(token in name for token in ("id", "member", "url")):
        return "Identifier variables"
    if any(token in name for token in ("date", "issue_d", "earliest_cr", "pymnt")):
        return "Date variables"
    if any(token in name for token in ("desc", "title", "emp_title")):
        return "Text variables"
    if any(token in name for token in TARGET_CANDIDATE_PATTERNS):
        return "Target candidates"
    return "Requires dictionary-led classification"


def find_pattern_matches(columns: Iterable[str], patterns: Iterable[str]) -> list[str]:
    """Return observed columns matching one or more case-insensitive patterns."""

    normalized_patterns = tuple(pattern.lower() for pattern in patterns)
    return [
        column
        for column in columns
        if any(pattern in column.lower() for pattern in normalized_patterns)
    ]


def leakage_screen(columns: Iterable[str]) -> list[str]:
    """Flag fields requiring temporal leakage review before application modelling."""

    return find_pattern_matches(columns, LEAKAGE_PATTERNS)


def target_candidate_screen(columns: Iterable[str]) -> list[str]:
    """Flag outcome-like fields for business-definition review; does not select a target."""

    return find_pattern_matches(columns, TARGET_CANDIDATE_PATTERNS)


def format_bytes(value: int | None) -> str:
    """Format bytes for concise, human-readable reporting."""

    if value is None:
        return "Not available"
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    size = float(value)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TiB"
