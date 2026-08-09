#!/usr/bin/env python3
"""Grade a Multi-Step Arithmetic Word Problems submission.

Metric: exact-match accuracy over canonical integer answers, in [0, 1].
Any structural or format violation returns the floor score 0.0 for the whole
submission; predictions are never repaired, coerced, or renormalized.
"""

from __future__ import annotations

import re

import pandas as pd

FLOOR = 0.0
REQUIRED_COLUMNS = ["id", "answer"]
CANONICAL_INT = re.compile(r"^(0|-?[1-9][0-9]*)$")


def grade(submission: pd.DataFrame, answers: pd.DataFrame) -> float:
    try:
        if list(submission.columns) != REQUIRED_COLUMNS:
            return FLOOR
        if len(submission) != len(answers):
            return FLOOR

        ids = submission["id"].astype(str)
        if ids.duplicated().any():
            return FLOOR
        truth_ids = answers["id"].astype(str)
        if set(ids) != set(truth_ids):
            return FLOOR

        predictions = submission["answer"].astype(str)
        if not predictions.map(lambda value: bool(CANONICAL_INT.match(value))).all():
            return FLOOR

        truth = pd.Series(
            answers["answer"].astype(str).values, index=truth_ids
        )
        aligned = pd.Series(predictions.values, index=ids).reindex(truth.index)
        return float((aligned == truth).mean())
    except Exception:
        return FLOOR
