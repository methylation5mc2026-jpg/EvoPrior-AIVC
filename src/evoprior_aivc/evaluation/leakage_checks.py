"""Leakage checks for perturbation-response evaluation."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

import pandas as pd

from evoprior_aivc.data.splits import assert_holdout_values_absent

DEFAULT_FORBIDDEN_FEATURE_TOKENS: tuple[str, ...] = (
    "post_perturbation",
    "target_delta",
    "observed_delta",
    "observed_post",
    "test_target",
)


def assert_holdout_split_has_no_train_leakage(
    metadata: pd.DataFrame,
    split: Sequence[str] | pd.Series,
    *,
    holdout: Mapping[str, Iterable[object]],
) -> None:
    """Assert held-out values do not appear in train or validation rows."""
    for column, values in holdout.items():
        assert_holdout_values_absent(metadata, split, column=column, values=values)


def assert_required_split_labels(
    split: Sequence[str] | pd.Series,
    *,
    required_labels: Iterable[str] = ("train", "test"),
) -> None:
    """Assert the split contains required labels."""
    observed = set(pd.Series(split, dtype="object").dropna())
    missing = set(required_labels).difference(observed)
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"split is missing required labels: {missing_list}")


def assert_no_target_derived_features(
    feature_columns: Iterable[str],
    *,
    forbidden_tokens: Iterable[str] = DEFAULT_FORBIDDEN_FEATURE_TOKENS,
) -> None:
    """Reject feature names that look derived from target post-perturbation data."""
    lower_features = {str(column).lower() for column in feature_columns}
    leaks = sorted(
        feature
        for feature in lower_features
        if any(token.lower() in feature for token in forbidden_tokens)
    )
    if leaks:
        leaked = ", ".join(leaks)
        raise ValueError(f"target-derived feature columns are not allowed: {leaked}")

