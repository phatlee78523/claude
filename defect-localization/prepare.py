#!/usr/bin/env python3
"""Prepare the Industrial Defect Localization challenge package.

Reads an extracted VisA release, derives one axis-aligned bounding box per
defective image from its instance mask, groups near-duplicate defects into
single independent units, assigns opaque identifiers and anonymous part-type
codes, splits units into train/test and public/private, and writes the public
package plus the private grading answer file.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

SALT = "idl-v1"
SPLIT_SEED = 20260810
DUP_IOU = 0.75


def opaque_id(part: str, kind: str, filename: str) -> str:
    key = f"{SALT}:{part}:{kind}:{filename}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def union_box(mask_path: Path) -> tuple[int, int, int, int, int, int]:
    mask = np.array(Image.open(mask_path).convert("L")) > 0
    if not mask.any():
        raise ValueError(f"{mask_path} has no positive pixels")
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    height, width = mask.shape
    return (
        int(cols[0]), int(rows[0]), int(cols[-1]), int(rows[-1]), width, height
    )


def duplicate_units(masks: list[Path], parts: list[str]) -> list[int]:
    """Union-find over within-part mask pairs whose IoU exceeds DUP_IOU."""
    parent = list(range(len(masks)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[max(ri, rj)] = min(ri, rj)

    by_part: dict[str, list[int]] = {}
    for index, part in enumerate(parts):
        by_part.setdefault(part, []).append(index)

    for indices in by_part.values():
        flat = []
        for index in indices:
            arr = np.array(Image.open(masks[index]).convert("L")) > 0
            flat.append(arr.reshape(-1).astype(np.float32))
        stack = np.stack(flat)
        inter = stack @ stack.T
        sizes = stack.sum(axis=1)
        denom = np.maximum(sizes[:, None] + sizes[None, :] - inter, 1.0)
        iou = inter / denom
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                if iou[a, b] >= DUP_IOU:
                    union(indices[a], indices[b])
    return [find(i) for i in range(len(masks))]


def collect(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    parts = sorted(
        d.name for d in root.iterdir() if d.is_dir() and (d / "Data").is_dir()
    )
    if not parts:
        raise ValueError(f"no VisA part directories found under {root}")
    type_code = {part: f"T{index + 1:02d}" for index, part in enumerate(parts)}

    defect_rows, normal_rows = [], []
    for part in parts:
        mask_dir = root / part / "Data" / "Masks" / "Anomaly"
        image_dir = root / part / "Data" / "Images" / "Anomaly"
        for mask_path in sorted(mask_dir.iterdir()):
            image_path = next(
                (p for p in sorted(image_dir.iterdir())
                 if p.stem == mask_path.stem), None
            )
            if image_path is None:
                raise ValueError(f"no image matching mask {mask_path}")
            x0, y0, x1, y1, width, height = union_box(mask_path)
            defect_rows.append(
                {
                    "id": opaque_id(part, "defect", image_path.name),
                    "part_type": type_code[part],
                    "source_image": image_path,
                    "source_mask": mask_path,
                    "x_min": x0, "y_min": y0, "x_max": x1, "y_max": y1,
                    "width": width, "height": height,
                }
            )
        for image_path in sorted((root / part / "Data" / "Images" / "Normal").iterdir()):
            normal_rows.append(
                {
                    "id": opaque_id(part, "normal", image_path.name),
                    "part_type": type_code[part],
                    "source_image": image_path,
                }
            )

    defects = pd.DataFrame(defect_rows)
    normals = pd.DataFrame(normal_rows)
    for frame in (defects, normals):
        if frame["id"].duplicated().any():
            raise ValueError("identifier collision")
    return defects, normals


def assign_split(defects: pd.DataFrame, test_fraction: float,
                 public_fraction: float) -> pd.DataFrame:
    groups = duplicate_units(
        defects["source_mask"].tolist(), defects["part_type"].tolist()
    )
    defects = defects.copy()
    defects["unit_id"] = [f"U{g:04d}" for g in groups]

    units = (
        defects.groupby("unit_id")
        .agg(part_type=("part_type", "first"))
        .reset_index()
        .sort_values("unit_id", kind="stable")
    )
    rng = np.random.default_rng(SPLIT_SEED)
    split, visibility = {}, {}
    for part, block in units.groupby("part_type", sort=True):
        ids = block["unit_id"].tolist()
        order = rng.permutation(len(ids))
        n_test = int(round(test_fraction * len(ids)))
        test_ids = [ids[i] for i in order[:n_test]]
        n_public = int(round(public_fraction * len(test_ids)))
        public_ids = set(test_ids[:n_public])
        for unit in ids:
            split[unit] = "test" if unit in set(test_ids) else "train"
            if split[unit] == "test":
                visibility[unit] = "public" if unit in public_ids else "private"
    defects["split"] = defects["unit_id"].map(split)
    defects["visibility"] = defects["unit_id"].map(visibility).fillna("")
    return defects


def copy_images(frame: pd.DataFrame, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for row in frame.itertuples():
        shutil.copyfile(row.source_image, destination / f"{row.id}.jpg")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--visa-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--test-fraction", type=float, default=0.20)
    parser.add_argument("--public-fraction", type=float, default=0.25)
    args = parser.parse_args()

    defects, normals = collect(args.visa_root)
    defects = assign_split(defects, args.test_fraction, args.public_fraction)

    public = args.output_dir / "public"
    private = args.output_dir / "private"
    public.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)

    train = defects[defects["split"] == "train"].sort_values("id", kind="stable")
    test = defects[defects["split"] == "test"].sort_values("id", kind="stable")
    normals = normals.sort_values("id", kind="stable")

    copy_images(train, public / "train_defective")
    copy_images(test, public / "test")
    copy_images(normals, public / "train_normal")

    train[["id", "part_type", "width", "height",
           "x_min", "y_min", "x_max", "y_max"]].to_csv(
        public / "train_labels.csv", index=False
    )
    normals[["id", "part_type"]].to_csv(
        public / "train_normal.csv", index=False
    )
    test[["id", "part_type", "width", "height"]].to_csv(
        public / "test.csv", index=False
    )
    pd.DataFrame(
        {
            "id": test["id"],
            "x_min": 0, "y_min": 0,
            "x_max": test["width"] - 1, "y_max": test["height"] - 1,
        }
    ).to_csv(public / "sample_submission.csv", index=False)

    test[["id", "x_min", "y_min", "x_max", "y_max",
          "width", "height", "visibility", "unit_id"]].to_csv(
        private / "answer.csv", index=False
    )

    print(
        f"parts: {defects['part_type'].nunique()}\n"
        f"defect images: {len(defects)}  independent units: {defects['unit_id'].nunique()}\n"
        f"train defective: {len(train)}  test: {len(test)}"
        f" ({len(test) / len(defects):.3f} of defect images)\n"
        f"public test units: {(test['visibility'] == 'public').sum()}"
        f"  private test units: {(test['visibility'] == 'private').sum()}\n"
        f"auxiliary normal images: {len(normals)}"
    )


if __name__ == "__main__":
    main()
