#!/usr/bin/env python3
"""Data preparation pipeline for the Industrial Defect Localization challenge.

The hosting platform mounts the accepted source dataset at ``raw`` and expects
this module to write the solver-visible package to ``public`` and the grading
material to ``private``.  The heavy work — deriving boxes from instance masks,
grouping near-duplicate defects into independent units, assigning opaque
identifiers and the train/test and public/private splits — already happened when
the dataset was built, deterministically and reproducibly, so this stage only
routes the prepared files to the two destinations and re-checks the invariants
that keep the evaluation blind.

Layout expected under ``raw`` (folder names, wherever they sit in the tree)::

    images/train_defective/*.jpg   train_labels.csv
    images/train_normal/*.jpg      train_normal.csv
    images/test/*.jpg              test.csv
                                   sample_submission.csv
                                   answer.csv        <- grading only, never public

The grading entrypoint reads ``/private/answers.csv``, so the answer table is
written under that plural name regardless of how it is named in ``raw``.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pandas as pd

IMAGE_DIRS = ("train_defective", "train_normal", "test")
PUBLIC_CSVS = (
    "train_labels.csv",
    "train_normal.csv",
    "test.csv",
    "sample_submission.csv",
)
RAW_ANSWER_NAMES = ("answers.csv", "answer.csv")
ANSWER_CSV = "answers.csv"   # the grading entrypoint reads /private/answers.csv
ANSWER_COLUMNS = [
    "id", "x_min", "y_min", "x_max", "y_max",
    "width", "height", "visibility", "unit_id",
]
SUBMISSION_COLUMNS = ["id", "x_min", "y_min", "x_max", "y_max"]
LEAK_COLUMNS = {"x_min", "y_min", "x_max", "y_max", "visibility", "unit_id"}


def _find_file(root: Path, name: str) -> Path:
    """Locate ``name`` under ``root``, preferring the shallowest match."""
    direct = root / name
    if direct.is_file():
        return direct
    matches = sorted(
        (p for p in root.rglob(name) if p.is_file()),
        key=lambda p: (len(p.relative_to(root).parts), str(p)),
    )
    if not matches:
        raise FileNotFoundError(f"{name} not found under {root}")
    return matches[0]


def _find_dir(root: Path, name: str) -> Path:
    direct = root / name
    if direct.is_dir():
        return direct
    nested = root / "images" / name
    if nested.is_dir():
        return nested
    matches = sorted(
        (p for p in root.rglob(name) if p.is_dir()),
        key=lambda p: (len(p.relative_to(root).parts), str(p)),
    )
    if not matches:
        raise FileNotFoundError(f"directory {name} not found under {root}")
    return matches[0]


def _find_answers(root: Path) -> Path:
    """The grading answer table, under either the singular or plural name."""
    for name in RAW_ANSWER_NAMES:
        try:
            return _find_file(root, name)
        except FileNotFoundError:
            continue
    raise FileNotFoundError(
        f"none of {RAW_ANSWER_NAMES} found under {root}"
    )


def _link_tree(source: Path, destination: Path) -> int:
    """Copy an image folder, hard-linking where the filesystem allows it."""
    destination.mkdir(parents=True, exist_ok=True)
    count = 0
    for image in sorted(source.iterdir()):
        if not image.is_file():
            continue
        target = destination / image.name
        try:
            os.link(image, target)
        except OSError:
            shutil.copyfile(image, target)
        count += 1
    return count


def prepare(raw: Path, public: Path, private: Path) -> None:
    raw, public, private = Path(raw), Path(public), Path(private)
    public.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)

    # --- solver-visible images -------------------------------------------------
    counts = {}
    for name in IMAGE_DIRS:
        counts[name] = _link_tree(_find_dir(raw, name), public / name)

    # --- solver-visible tables -------------------------------------------------
    for name in PUBLIC_CSVS:
        shutil.copyfile(_find_file(raw, name), public / name)

    train = pd.read_csv(public / "train_labels.csv", dtype=str)
    normal = pd.read_csv(public / "train_normal.csv", dtype=str)
    test = pd.read_csv(public / "test.csv", dtype=str)
    sample = pd.read_csv(public / "sample_submission.csv", dtype=str)

    # --- grading material ------------------------------------------------------
    answers = pd.read_csv(_find_answers(raw), dtype=str)
    missing = [c for c in ANSWER_COLUMNS if c not in answers.columns]
    if missing:
        raise ValueError(f"the answer file is missing columns: {missing}")
    answers = answers[ANSWER_COLUMNS]
    answers.to_csv(private / ANSWER_CSV, index=False)

    # --- invariants ------------------------------------------------------------
    test_ids = list(test["id"])
    if len(set(test_ids)) != len(test_ids):
        raise ValueError("duplicate id in test.csv")
    if set(answers["id"]) != set(test_ids):
        raise ValueError("the answer file does not cover exactly the test ids")
    if len(answers) != len(test_ids):
        raise ValueError("answer row count does not match test.csv")
    if list(sample.columns) != SUBMISSION_COLUMNS:
        raise ValueError("sample_submission.csv has the wrong column order")
    if set(sample["id"]) != set(test_ids):
        raise ValueError("sample_submission.csv does not cover the test ids")

    if set(train["id"]) & set(test_ids):
        raise ValueError("an identifier appears in both train_labels and test")
    if set(normal["id"]) & set(test_ids):
        raise ValueError("an identifier appears in both train_normal and test")

    units = answers.set_index(pd.Index(list(answers["id"])))["unit_id"]
    visibility = answers.set_index(pd.Index(list(answers["id"])))["visibility"]
    per_unit = pd.DataFrame({"unit": list(units), "vis": list(visibility)})
    crossing = per_unit.groupby("unit")["vis"].nunique()
    if (crossing > 1).any():
        raise ValueError("an independent unit spans both leaderboards")
    if not set(visibility) <= {"public", "private"}:
        raise ValueError("visibility must be 'public' or 'private'")

    # Nothing that reveals a test answer may sit in the public package.
    for path in public.rglob("*.csv"):
        columns = set(pd.read_csv(path, nrows=0).columns)
        if path.name == "train_labels.csv":
            continue
        if columns & LEAK_COLUMNS and path.name != "sample_submission.csv":
            raise ValueError(f"{path.name} exposes grading columns")
    for name in RAW_ANSWER_NAMES:
        if (public / name).exists():
            raise ValueError(f"{name} leaked into the public package")

    print(
        f"public images  train_defective={counts['train_defective']} "
        f"train_normal={counts['train_normal']} test={counts['test']}\n"
        f"public tables  train_labels={len(train)} train_normal={len(normal)} "
        f"test={len(test)} sample_submission={len(sample)}\n"
        f"private        answer={len(answers)} rows, "
        f"{(answers['visibility'] == 'public').sum()} public / "
        f"{(answers['visibility'] == 'private').sum()} private, "
        f"{answers['unit_id'].nunique()} independent units"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.raw, args.public, args.private)
