#!/usr/bin/env python3
"""Audit visibility integrity and leaderboard score stability."""

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
        raise ValueError(f"{path} must define callable grade(submission, answers)")
    return grade_fn


def check_unit_integrity(
    answers: pd.DataFrame, unit_col: str, visibility_col: str
) -> list[str]:
    for column in (unit_col, visibility_col):
        if column not in answers.columns:
            raise ValueError(f"answers is missing required column {column!r}")
        if answers[column].isna().any():
            raise ValueError(f"answers column {column!r} contains null values")
    counts = answers.groupby(unit_col, dropna=False)[visibility_col].nunique()
    return [str(value) for value in counts[counts != 1].index.tolist()]


def subset_submission(
    submission: pd.DataFrame,
    answer_subset: pd.DataFrame,
    id_col: str,
) -> pd.DataFrame:
    if id_col not in submission.columns or id_col not in answer_subset.columns:
        raise ValueError(f"submission and answers must contain ID column {id_col!r}")
    identifiers = set(answer_subset[id_col].tolist())
    return submission[submission[id_col].isin(identifiers)].copy()


def safe_score(
    grade_fn: Callable[[pd.DataFrame, pd.DataFrame], float],
    submission: pd.DataFrame,
    answers: pd.DataFrame,
) -> float:
    score = float(grade_fn(submission, answers))
    if not math.isfinite(score):
        raise ValueError("grader returned a non-finite score")
    return score


def audit(args: argparse.Namespace) -> tuple[dict[str, object], list[str]]:
    answers = pd.read_csv(args.answers)
    oracle = pd.read_csv(args.oracle)
    grade_fn = load_grade(args.grade)

    crossed_units = check_unit_integrity(answers, args.unit_col, args.visibility_col)
    failures: list[str] = []
    if crossed_units:
        failures.append(f"{len(crossed_units)} independent units cross visibility")

    valid_visibility = {args.public_value, args.private_value}
    observed_visibility = set(answers[args.visibility_col].astype(str).unique())
    unexpected = observed_visibility - valid_visibility
    if unexpected:
        failures.append(f"unexpected visibility values: {sorted(unexpected)}")

    visibility_stats: dict[str, dict[str, int]] = {}
    oracle_scores: dict[str, float] = {}
    for value in (args.public_value, args.private_value):
        answer_subset = answers[answers[args.visibility_col].astype(str) == value]
        if answer_subset.empty:
            failures.append(f"visibility {value!r} has no answer rows")
            continue
        submission_subset = subset_submission(
            oracle, answer_subset, args.id_col
        )
        visibility_stats[value] = {
            "rows": int(len(answer_subset)),
            "units": int(answer_subset[args.unit_col].nunique()),
        }
        oracle_scores[value] = safe_score(grade_fn, submission_subset, answer_subset)

    oracle_gap = None
    if len(oracle_scores) == 2:
        oracle_gap = abs(
            oracle_scores[args.public_value] - oracle_scores[args.private_value]
        )
        if oracle_gap > args.oracle_gap_tolerance:
            failures.append(
                "oracle public/private gap "
                f"{oracle_gap:.6g} exceeds tolerance {args.oracle_gap_tolerance:.6g}"
            )
        for value, score in oracle_scores.items():
            if abs(score - args.perfect_score) > args.perfect_score_tolerance:
                failures.append(
                    f"oracle {value} score {score:.6g} differs from perfect "
                    f"score {args.perfect_score:.6g}"
                )

    private_answers = answers[
        answers[args.visibility_col].astype(str) == args.private_value
    ]
    peer_scores: list[float] = []
    for path in args.peer_submissions:
        submission = pd.read_csv(path)
        private_submission = subset_submission(
            submission, private_answers, args.id_col
        )
        peer_scores.append(safe_score(grade_fn, private_submission, private_answers))

    score_sd = None
    score_range = None
    required_gap_2sd = None
    required_gap_3sd = None
    if peer_scores:
        if len(peer_scores) < 10:
            failures.append(
                f"only {len(peer_scores)} peer submissions supplied; require at least 10"
            )
        score_sd = float(np.std(peer_scores, ddof=1)) if len(peer_scores) > 1 else 0.0
        score_range = float(max(peer_scores) - min(peer_scores))
        required_gap_2sd = 2.0 * score_sd
        required_gap_3sd = 3.0 * score_sd
        if args.solver_gap is not None and args.solver_gap < required_gap_2sd:
            failures.append(
                f"solver gap {args.solver_gap:.6g} is below 2×sd "
                f"({required_gap_2sd:.6g})"
            )
    else:
        failures.append("no equal-quality peer submissions supplied")

    total_units = answers[args.unit_col].nunique()
    public_units = visibility_stats.get(args.public_value, {}).get("units", 0)
    public_fraction = public_units / total_units if total_units else None
    if public_fraction is not None and not (
        args.min_public_fraction <= public_fraction <= args.max_public_fraction
    ):
        failures.append(
            f"public unit fraction {public_fraction:.3f} is outside "
            f"[{args.min_public_fraction:.3f}, {args.max_public_fraction:.3f}]"
        )

    report: dict[str, object] = {
        "status": "PASS" if not failures else "FAIL",
        "crossed_unit_count": len(crossed_units),
        "crossed_unit_examples": crossed_units[:20],
        "visibility": visibility_stats,
        "public_unit_fraction": public_fraction,
        "oracle_scores": oracle_scores,
        "oracle_absolute_gap": oracle_gap,
        "peer_private_scores": peer_scores,
        "peer_score_sd": score_sd,
        "peer_score_range": score_range,
        "required_solver_gap_2sd": required_gap_2sd,
        "preferred_solver_gap_3sd": required_gap_3sd,
        "supplied_solver_gap": args.solver_gap,
        "failures": failures,
    }
    return report, failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answers", type=Path, required=True)
    parser.add_argument("--oracle", type=Path, required=True)
    parser.add_argument("--grade", type=Path, required=True)
    parser.add_argument("--unit-col", required=True)
    parser.add_argument("--id-col", default="id")
    parser.add_argument("--visibility-col", default="visibility")
    parser.add_argument("--public-value", default="public")
    parser.add_argument("--private-value", default="private")
    parser.add_argument("--peer-submissions", type=Path, nargs="*", default=[])
    parser.add_argument("--oracle-gap-tolerance", type=float, default=0.01)
    parser.add_argument("--perfect-score", type=float, default=1.0)
    parser.add_argument("--perfect-score-tolerance", type=float, default=1e-9)
    parser.add_argument("--min-public-fraction", type=float, default=0.20)
    parser.add_argument("--max-public-fraction", type=float, default=0.30)
    parser.add_argument("--solver-gap", type=float)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report, failures = audit(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
