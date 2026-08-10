# Industrial Defect Localization

A competition-ready ML challenge built with the
[`build-ml-challenges`](../build-ml-challenges/) skill.

**Task.** Given a photograph of a manufactured part known to be defective,
predict the bounding box enclosing the defective region. Metric: mean
intersection-over-union.

**Source.** VisA (Visual Anomaly), Amazon — **CC BY 4.0**, verified at the
project repository and the AWS Open Data Registry. Commercial use and
redistribution permitted with attribution. Cite Zou et al., arXiv:2207.14315.

## Contents

- [`description.md`](description.md) — challenge statement (source-secret).
- [`dataset-description.md`](dataset-description.md) — dataset record with
  provenance, licence and preparation details.
- [`release-report.md`](release-report.md) — gate-by-gate results.
- `prepare.py` — deterministic packaging from an extracted VisA release.
- `grade.py` — mean-IoU grader with strict submission validation.
- `audit/` — grader, stability, shortcut-baseline and packaging reports.

The image package (1.92 GB) is not committed here; regenerate it from the
source release.

## Regenerating the package

```bash
curl -O https://amazon-visual-anomaly.s3.us-west-2.amazonaws.com/VisA_20220922.tar
mkdir visa && tar -xf VisA_20220922.tar -C visa
python prepare.py --visa-root visa --output-dir .
cd public && zip -0 -r ../images.zip train_defective train_normal test
```

The released dataset nests the three image folders under `images/`, which is how
the hosting platform extracts an archive named `images.zip`; the four CSV files
sit beside it at the top level.

Requires `numpy`, `pandas`, `pillow`. Deterministic: fixed hash salt and split
seed 20260810, 92 s runtime, 1.8 GB peak RSS.

## Headline numbers

| | |
| --- | --- |
| Annotated defective images | 1,200 → 1,195 independent units |
| Train / test | 958 / 242 · public 60 / private 180 |
| Auxiliary flawless images | 9,621 |
| Oracle | 1.000 (public and private, gap 0.0) |
| Private noise floor | sd 0.0107 · 3×sd 0.0321 |
| Strongest shortcut baseline | 0.0918 vs 0.512 reference solver |
