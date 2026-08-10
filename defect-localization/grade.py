#!/usr/bin/env python3
"""Grade an Industrial Defect Localization submission.

Metric: mean intersection-over-union between the submitted box and the
reference defect box, averaged over all scored images, in [0, 1].
Any structural or format violation returns the floor score 0.0 for the whole
submission; boxes are never clipped, repaired, or coerced.
"""

from __future__ import annotations

import re

import pandas as pd

FLOOR = 0.0
REQUIRED_COLUMNS = ["id", "x_min", "y_min", "x_max", "y_max"]
COORD_COLUMNS = ["x_min", "y_min", "x_max", "y_max"]
CANONICAL_INT = re.compile(r"^(0|[1-9][0-9]*)$")


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

        submitted_index = list(ids)
        truth_index = list(truth_ids)

        coords = {}
        for column in COORD_COLUMNS:
            values = submission[column].astype(str)
            if not values.map(lambda v: bool(CANONICAL_INT.match(v))).all():
                return FLOOR
            coords[column] = pd.Series(
                [int(v) for v in values], index=submitted_index
            ).reindex(truth_index)

        truth = answers.set_index(pd.Index(truth_index))

        px0, py0 = coords["x_min"], coords["y_min"]
        px1, py1 = coords["x_max"], coords["y_max"]
        if (px1 < px0).any() or (py1 < py0).any():
            return FLOOR
        if (px1 >= truth["width"].astype(int)).any():
            return FLOOR
        if (py1 >= truth["height"].astype(int)).any():
            return FLOOR

        tx0 = truth["x_min"].astype(int)
        ty0 = truth["y_min"].astype(int)
        tx1 = truth["x_max"].astype(int)
        ty1 = truth["y_max"].astype(int)

        iw = (pd.concat([px1, tx1], axis=1).min(axis=1)
              - pd.concat([px0, tx0], axis=1).max(axis=1) + 1).clip(lower=0)
        ih = (pd.concat([py1, ty1], axis=1).min(axis=1)
              - pd.concat([py0, ty0], axis=1).max(axis=1) + 1).clip(lower=0)
        intersection = iw * ih

        parea = (px1 - px0 + 1) * (py1 - py0 + 1)
        tarea = (tx1 - tx0 + 1) * (ty1 - ty0 + 1)
        union = parea + tarea - intersection
        return float((intersection / union).mean())
    except Exception:
        return FLOOR
