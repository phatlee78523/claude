#!/usr/bin/env python3
"""Data preparation pipeline for the Industrial Defect Localization challenge.

The hosting platform mounts the source dataset at ``raw`` and expects this module
to write the solver-visible package to ``public`` and the grading material to
``private``.

The evaluation protocol is **leave-part-types-out**: three of the twelve part
types are withheld entirely from the annotated training data, and every test
image comes from one of those three.  A solution therefore never sees a single
annotated defect for the part types it is scored on.  What it does get for them
is the unannotated flawless photographs, so the intended path is to model
correct appearance for an unseen part and localise the deviation.

The three held-out types are drawn deterministically from a fixed seed, so the
split is reproducible and was not hand-picked.  Independent units — groups of
images that photograph the same physical flaw — never straddle a split
boundary; duplicates are listed explicitly below because they were computed once
from the source instance masks and cannot be recovered from the released files.

Layout expected under ``raw`` (folder names, wherever they sit in the tree)::

    images/train_defective/*.jpg   train_labels.csv    (958 boxed images)
    images/test/*.jpg              test.csv            (242 unboxed images)
    images/train_normal/*.jpg      train_normal.csv    (9,621 flawless images)
                                   sample_submission.csv
                                   answers.csv    <- boxes for the 242, grading only

``train_labels.csv`` and ``answers.csv`` together carry the boxes for all 1,200
annotated images; this stage pools them and re-splits by part type.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

SPLIT_SEED = 20260810
HELD_OUT_TYPES = 3
PUBLIC_FRACTION = 0.25

RAW_ANSWER_NAMES = ("answers.csv", "answer.csv")
ANSWER_CSV = "answers.csv"   # the grading entrypoint reads /private/answers.csv
BOX_COLUMNS = ["x_min", "y_min", "x_max", "y_max"]
SUBMISSION_COLUMNS = ["id"] + BOX_COLUMNS
ANSWER_COLUMNS = SUBMISSION_COLUMNS + ["width", "height", "visibility", "unit_id"]
LEAK_COLUMNS = set(BOX_COLUMNS) | {"visibility", "unit_id"}

# Images of one physical flaw, grouped at source-mask IoU >= 0.75. Every group
# lies inside a single part type, so leaving a type out keeps a group intact.
DUPLICATE_GROUPS = (
    ("c437cb53d49b", "80bf07e9501c"),
    ("a3b1b704f642", "3fbf72b59e96"),
    ("f12508a2590a", "a10f4690ac89"),
    ("f9172d0cfd97", "7d87009c759d", "61ebcb3ca005"),
)


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
    for name in RAW_ANSWER_NAMES:
        try:
            return _find_file(root, name)
        except FileNotFoundError:
            continue
    raise FileNotFoundError(f"none of {RAW_ANSWER_NAMES} found under {root}")


def _place(source: Path, destination: Path) -> None:
    """Hard-link where the filesystem allows it, otherwise copy."""
    try:
        os.link(source, destination)
    except OSError:
        shutil.copyfile(source, destination)


def _unit_ids(ids: list[str]) -> dict[str, str]:
    """Map every identifier to its independent unit."""
    lookup = {}
    for group in DUPLICATE_GROUPS:
        anchor = min(group)
        for member in group:
            lookup[member] = anchor
    return {i: lookup.get(i, i) for i in ids}


def prepare(raw: Path, public: Path, private: Path) -> None:
    raw, public, private = Path(raw), Path(public), Path(private)
    public.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)

    # --- pool every annotated image, wherever its box currently lives ----------
    boxed = pd.read_csv(_find_file(raw, "train_labels.csv"), dtype=str)
    listed = pd.read_csv(_find_file(raw, "test.csv"), dtype=str)
    answers = pd.read_csv(_find_answers(raw), dtype=str)

    held_boxes = listed[["id", "part_type"]].merge(
        answers[SUBMISSION_COLUMNS + ["width", "height"]], on="id", how="inner"
    )
    if len(held_boxes) != len(listed):
        raise ValueError("the answer file does not cover every row of test.csv")

    columns = ["id", "part_type", "width", "height"] + BOX_COLUMNS
    pool = pd.concat([boxed[columns], held_boxes[columns]], ignore_index=True)
    pool = pool.sort_values("id", kind="stable").reset_index(drop=True)
    if pool["id"].duplicated().any():
        raise ValueError("an identifier appears twice in the annotated pool")
    pool["unit_id"] = pool["id"].map(_unit_ids(list(pool["id"])))

    # --- leave-part-types-out --------------------------------------------------
    rng = np.random.default_rng(SPLIT_SEED)
    codes = sorted(pool["part_type"].unique())
    if len(codes) <= HELD_OUT_TYPES:
        raise ValueError("not enough part types to hold any out")
    held = sorted(codes[i] for i in rng.permutation(len(codes))[:HELD_OUT_TYPES])

    test = pool[pool["part_type"].isin(held)].reset_index(drop=True)
    train = pool[~pool["part_type"].isin(held)].reset_index(drop=True)

    units = sorted(test["unit_id"].unique())
    order = rng.permutation(len(units))
    public_units = {units[i] for i in order[: int(round(PUBLIC_FRACTION * len(units)))]}
    test["visibility"] = np.where(
        test["unit_id"].isin(public_units), "public", "private"
    )

    # --- images ----------------------------------------------------------------
    sources = {}
    for folder in ("train_defective", "test"):
        for image in _find_dir(raw, folder).iterdir():
            if image.is_file():
                sources[image.stem] = image

    counts = {}
    for name, frame in (("train_defective", train), ("test", test)):
        target = public / name
        target.mkdir(parents=True, exist_ok=True)
        for identifier in frame["id"]:
            if identifier not in sources:
                raise FileNotFoundError(f"no image for {identifier}")
            _place(sources[identifier], target / f"{identifier}.jpg")
        counts[name] = len(frame)

    normal_dir = public / "train_normal"
    normal_dir.mkdir(parents=True, exist_ok=True)
    for image in sorted(_find_dir(raw, "train_normal").iterdir()):
        if image.is_file():
            _place(image, normal_dir / image.name)
    counts["train_normal"] = sum(1 for _ in normal_dir.iterdir())

    # --- tables ----------------------------------------------------------------
    shutil.copyfile(
        _find_file(raw, "train_normal.csv"), public / "train_normal.csv"
    )
    normal = pd.read_csv(public / "train_normal.csv", dtype=str)

    train[columns].to_csv(public / "train_labels.csv", index=False)
    test[["id", "part_type", "width", "height"]].to_csv(
        public / "test.csv", index=False
    )
    pd.DataFrame(
        {
            "id": test["id"],
            "x_min": "0",
            "y_min": "0",
            "x_max": (test["width"].astype(int) - 1).astype(str),
            "y_max": (test["height"].astype(int) - 1).astype(str),
        }
    ).to_csv(public / "sample_submission.csv", index=False)
    test[ANSWER_COLUMNS].to_csv(private / ANSWER_CSV, index=False)

    # --- invariants ------------------------------------------------------------
    sample = pd.read_csv(public / "sample_submission.csv", dtype=str)
    test_ids = set(test["id"])
    if len(test_ids) != len(test):
        raise ValueError("duplicate id in the test split")
    if set(train["id"]) & test_ids:
        raise ValueError("an identifier appears in both train and test")
    if set(normal["id"]) & test_ids:
        raise ValueError("a flawless image shares an identifier with a test image")
    if set(train["part_type"]) & set(held):
        raise ValueError("a held-out part type leaked into the training labels")
    if set(test["part_type"]) != set(held):
        raise ValueError("the test split is not exactly the held-out part types")
    if list(sample.columns) != SUBMISSION_COLUMNS:
        raise ValueError("sample_submission.csv has the wrong column order")
    if set(sample["id"]) != test_ids:
        raise ValueError("sample_submission.csv does not cover the test ids")

    crossing = test.groupby("unit_id")["visibility"].nunique()
    if (crossing > 1).any():
        raise ValueError("an independent unit spans both leaderboards")
    if not set(test["visibility"]) <= {"public", "private"}:
        raise ValueError("visibility must be 'public' or 'private'")

    for path in public.rglob("*.csv"):
        present = set(pd.read_csv(path, nrows=0).columns)
        if path.name in ("train_labels.csv", "sample_submission.csv"):
            continue
        if present & LEAK_COLUMNS:
            raise ValueError(f"{path.name} exposes grading columns")
    for name in RAW_ANSWER_NAMES:
        if (public / name).exists():
            raise ValueError(f"{name} leaked into the public package")

    print(
        f"held-out part types : {', '.join(held)}\n"
        f"train  {counts['train_defective']} boxed images, "
        f"{train['part_type'].nunique()} types, {train['unit_id'].nunique()} units\n"
        f"test   {counts['test']} images, {test['part_type'].nunique()} held-out "
        f"types, {test['unit_id'].nunique()} units "
        f"({(test['visibility'] == 'public').sum()} public / "
        f"{(test['visibility'] == 'private').sum()} private rows)\n"
        f"flawless {counts['train_normal']} images across all 12 types\n"
        f"private  {len(test)} answer rows"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--public", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.raw, args.public, args.private)
