#!/usr/bin/env python3
"""Prepare the Multi-Step Arithmetic Word Problems challenge package.

Reads the source train/test parquet files, canonicalizes final answers from
the `#### <value>` line of each worked solution, assigns opaque deterministic
identifiers, splits test units into public/private visibility, and emits the
public package plus the private grading answer file.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd

SALT = "mswp-v1"
SPLIT_SEED = 20250809
FINAL_LINE = re.compile(r"####\s*(.+?)\s*$", re.S)
CANONICAL_INT = re.compile(r"^(0|-?[1-9][0-9]*)$")


def canonical_answer(worked_solution: str) -> str:
    match = FINAL_LINE.search(worked_solution)
    if match is None:
        raise ValueError("worked solution has no '####' final line")
    value = match.group(1).strip().replace(",", "").replace("$", "").replace(" ", "")
    if not CANONICAL_INT.match(value):
        raise ValueError(f"final answer {value!r} is not a canonical integer")
    return value


def opaque_id(question: str) -> str:
    return hashlib.sha256(f"{SALT}:{question}".encode("utf-8")).hexdigest()[:12]


def load_split(path: Path) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    for column in ("question", "answer"):
        if column not in frame.columns:
            raise ValueError(f"{path} is missing required column {column!r}")
        if frame[column].isna().any():
            raise ValueError(f"{path} column {column!r} contains nulls")
    if frame["question"].duplicated().any():
        raise ValueError(f"{path} contains duplicate questions")
    out = pd.DataFrame(
        {
            "id": frame["question"].map(opaque_id),
            "question": frame["question"].astype(str),
            "solution": frame["answer"].astype(str),
            "final_answer": frame["answer"].astype(str).map(canonical_answer),
        }
    )
    if out["id"].duplicated().any():
        raise ValueError(f"{path} produced colliding identifiers")
    return out.sort_values("id", kind="stable").reset_index(drop=True)


def attach_socratic(base: pd.DataFrame, path: Path, emit: bool) -> pd.DataFrame:
    """Validate the socratic config against the main config; optionally attach
    its worked solutions as a `socratic_solution` column (train only)."""
    socratic = load_split(path)
    if list(socratic["id"]) != list(base["id"]):
        raise ValueError(f"{path} question set differs from the main config")
    if list(socratic["final_answer"]) != list(base["final_answer"]):
        raise ValueError(f"{path} final answers differ from the main config")
    if not emit:
        return base
    out = base.copy()
    out.insert(3, "socratic_solution", socratic["solution"].values)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-parquet", type=Path, required=True)
    parser.add_argument("--test-parquet", type=Path, required=True)
    parser.add_argument("--socratic-train-parquet", type=Path)
    parser.add_argument("--socratic-test-parquet", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--public-fraction", type=float, default=0.25)
    args = parser.parse_args()

    train = load_split(args.train_parquet)
    test = load_split(args.test_parquet)
    if args.socratic_train_parquet is not None:
        train = attach_socratic(train, args.socratic_train_parquet, emit=True)
    if args.socratic_test_parquet is not None:
        test = attach_socratic(test, args.socratic_test_parquet, emit=False)

    overlap = set(train["id"]) & set(test["id"])
    if overlap:
        raise ValueError(f"{len(overlap)} identifiers appear in both train and test")

    public_count = int(round(args.public_fraction * len(test)))
    rng = np.random.default_rng(SPLIT_SEED)
    order = rng.permutation(len(test))
    visibility = np.full(len(test), "private", dtype=object)
    visibility[order[:public_count]] = "public"

    public_dir = args.output_dir / "public"
    private_dir = args.output_dir / "private"
    public_dir.mkdir(parents=True, exist_ok=True)
    private_dir.mkdir(parents=True, exist_ok=True)

    train_columns = [c for c in
                     ("id", "question", "solution", "socratic_solution", "final_answer")
                     if c in train.columns]
    train[train_columns].to_csv(public_dir / "train.csv", index=False)
    test[["id", "question"]].to_csv(public_dir / "test.csv", index=False)
    pd.DataFrame({"id": test["id"], "answer": "0"}).to_csv(
        public_dir / "sample_submission.csv", index=False
    )
    pd.DataFrame(
        {
            "id": test["id"],
            "answer": test["final_answer"],
            "visibility": visibility,
            "unit_id": test["id"],
        }
    ).to_csv(private_dir / "answer.csv", index=False)

    print(
        f"train rows/units: {len(train)}\n"
        f"test rows/units: {len(test)}\n"
        f"public units: {public_count} ({public_count / len(test):.3f})\n"
        f"private units: {len(test) - public_count}"
    )


if __name__ == "__main__":
    main()
