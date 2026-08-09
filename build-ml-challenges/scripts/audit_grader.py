#!/usr/bin/env python3
"""Audit strict submission validation in a challenge grade.py."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd


def load_grade(path: Path) -> Callable[[pd.DataFrame, pd.DataFrame], float]:
    spec = importlib.util.spec_from_file_location("challenge_grade", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import grader from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    grade_fn = getattr(module, "grade", None)
    if not callable(grade_fn):
        raise ValueError(f"{path} must define grade(submission, answers)")
    return grade_fn


def call_grade(
    grade_fn: Callable[[pd.DataFrame, pd.DataFrame], float],
    submission: pd.DataFrame,
    answers: pd.DataFrame,
) -> tuple[float | None, str | None]:
    try:
        score = float(grade_fn(submission, answers))
    except Exception as exc:  # The audit requires a returned floor, not an exception.
        return None, f"{type(exc).__name__}: {exc}"
    if not math.isfinite(score):
        return score, "grader returned a non-finite score"
    return score, None


def unique_extra_id(values: pd.Series) -> str:
    observed = set(values.astype(str))
    candidate = "__GRADER_AUDIT_EXTRA_ID__"
    while candidate in observed:
        candidate += "X"
    return candidate


def malformed_cases(
    oracle: pd.DataFrame,
    id_col: str,
    prediction_cols: list[str],
    probability_cols: list[str],
) -> dict[str, pd.DataFrame]:
    cases: dict[str, pd.DataFrame] = {}

    extra_column = oracle.copy()
    extra_column["__unexpected_column__"] = 0
    cases["extra_column"] = extra_column

    if len(oracle.columns) > 1:
        cases["reordered_columns"] = oracle[list(reversed(oracle.columns))].copy()
    if prediction_cols:
        cases["missing_column"] = oracle.drop(columns=[prediction_cols[-1]]).copy()
    if len(oracle):
        cases["missing_row"] = oracle.iloc[:-1].copy()

        duplicate_id = oracle.copy()
        if len(duplicate_id) == 1:
            duplicate_id = pd.concat([duplicate_id, duplicate_id], ignore_index=True)
        else:
            duplicate_id.loc[duplicate_id.index[1], id_col] = duplicate_id.iloc[0][id_col]
        cases["duplicate_id"] = duplicate_id

        extra_row = oracle.copy()
        row = extra_row.iloc[[0]].copy()
        row[id_col] = unique_extra_id(extra_row[id_col])
        cases["extra_id"] = pd.concat([extra_row, row], ignore_index=True)

        for name, value in (
            ("blank", ""),
            ("whitespace", " "),
            ("nonnumeric_or_unknown", "not-a-number"),
            ("nan", np.nan),
            ("infinity", np.inf),
        ):
            broken = oracle.copy()
            broken.loc[broken.index[0], prediction_cols[0]] = value
            cases[name] = broken

    if probability_cols and len(oracle):
        negative = oracle.copy()
        negative.loc[negative.index[0], probability_cols[0]] = -0.1
        cases["negative_probability"] = negative

        zero_sum = oracle.copy()
        zero_sum.loc[zero_sum.index[0], probability_cols] = 0.0
        cases["zero_probability_sum"] = zero_sum

        nonfinite_probability = oracle.copy()
        nonfinite_probability.loc[nonfinite_probability.index[0], probability_cols[0]] = np.inf
        cases["nonfinite_probability"] = nonfinite_probability

    return cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answers", type=Path, required=True)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--grade", type=Path, required=True)
    parser.add_argument("--id-col", default="id")
    parser.add_argument("--prediction-cols", nargs="*")
    parser.add_argument("--prob-cols", nargs="*", default=[])
    parser.add_argument("--floor", type=float, default=0.0)
    parser.add_argument("--perfect", type=float, default=1.0)
    parser.add_argument("--tolerance", type=float, default=1e-9)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    answers = pd.read_csv(args.answers)
    oracle = pd.read_csv(args.oracle, keep_default_na=False, dtype=object)
    if args.id_col not in oracle.columns:
        raise ValueError(f"oracle is missing ID column {args.id_col!r}")
    prediction_cols = args.prediction_cols or [
        column for column in oracle.columns if column != args.id_col
    ]
    if not prediction_cols:
        raise ValueError("oracle has no prediction columns")
    missing = set(prediction_cols + args.prob_cols) - set(oracle.columns)
    if missing:
        raise ValueError(f"oracle is missing configured columns: {sorted(missing)}")

    grade_fn = load_grade(args.grade)
    results: dict[str, dict[str, object]] = {}
    failures: list[str] = []

    perfect_score, perfect_error = call_grade(grade_fn, oracle.copy(), answers)
    perfect_pass = (
        perfect_error is None
        and perfect_score is not None
        and abs(perfect_score - args.perfect) <= args.tolerance
    )
    results["oracle"] = {
        "score": perfect_score,
        "error": perfect_error,
        "expected": args.perfect,
        "pass": perfect_pass,
    }
    if not perfect_pass:
        failures.append("oracle did not return the documented perfect score")

    for name, submission in malformed_cases(
        oracle, args.id_col, prediction_cols, args.prob_cols
    ).items():
        score, error = call_grade(grade_fn, submission, answers)
        passed = (
            error is None
            and score is not None
            and abs(score - args.floor) <= args.tolerance
        )
        results[name] = {
            "score": score,
            "error": error,
            "expected": args.floor,
            "pass": passed,
        }
        if not passed:
            failures.append(f"{name} did not return the documented floor")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "results": results,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
