#!/usr/bin/env python3
"""Grade a Surface Damage Extent Estimation submission.

Metric: root-mean-square error of the base-10 logarithm of the predicted damage
extent, in parts per million of image area.

    Score range      0.0 upwards, unbounded above
    Grade direction  MINIMIZE - lower is better
    Perfect score    0.0, every prediction exactly right
    Reference        a constant-value baseline scores about 0.78

The target spans three orders of magnitude, from a couple of hundred parts per
million to a fifth of the image, so error is measured in log space: predicting
2,000 where the truth is 1,000 costs exactly as much as predicting 20,000 where
the truth is 10,000. A submission that violates a structural or format rule is
rejected outright rather than scored; predictions are never clipped, rounded or
otherwise repaired.
"""

from __future__ import annotations

import math
import re

import pandas as pd

SCORE_MIN = 0.0            # perfect score
SCORE_MAX = math.inf       # unbounded: an arbitrarily bad guess scores arbitrarily high
GRADE_DIRECTION = "minimize"
REQUIRED_COLUMNS = ["id", "extent_ppm"]
TARGET = "extent_ppm"
MIN_EXTENT = 1
MAX_EXTENT = 1_000_000
POSITIVE_INT = re.compile(r"^[1-9][0-9]*$")


def grade(submission: pd.DataFrame, answers: pd.DataFrame) -> float:
    """Score a submission against the withheld answers. Lower is better."""
    if list(submission.columns) != REQUIRED_COLUMNS:
        raise ValueError(
            f"submission columns must be exactly {REQUIRED_COLUMNS}, "
            f"got {list(submission.columns)}"
        )
    if len(submission) != len(answers):
        raise ValueError(
            f"submission has {len(submission)} rows, expected {len(answers)}"
        )

    ids = submission["id"].astype(str)
    if ids.duplicated().any():
        raise ValueError("submission contains a duplicated id")
    truth_ids = answers["id"].astype(str)
    if set(ids) != set(truth_ids):
        raise ValueError("submission ids do not match the test ids exactly")

    values = submission[TARGET].astype(str)
    if not values.map(lambda v: bool(POSITIVE_INT.match(v))).all():
        raise ValueError(
            f"every {TARGET} must be a canonical positive integer: digits only, "
            "no sign, no decimal point, no leading zeros"
        )

    predicted = pd.Series([int(v) for v in values], index=list(ids))
    if predicted.lt(MIN_EXTENT).any() or predicted.gt(MAX_EXTENT).any():
        raise ValueError(f"every {TARGET} must lie in [{MIN_EXTENT}, {MAX_EXTENT}]")

    truth_index = list(truth_ids)
    predicted = predicted.reindex(truth_index)
    actual = pd.Series(
        [int(v) for v in answers[TARGET].astype(str)], index=truth_index
    )

    error = predicted.map(math.log10) - actual.map(math.log10)
    return float((error.pow(2).mean()) ** 0.5)
