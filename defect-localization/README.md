# Industrial Defect Localization

A competition-ready ML challenge built with the
[`build-ml-challenges`](../build-ml-challenges/) skill.

**Task.** Given a photograph of a manufactured part known to be defective,
predict the bounding box enclosing the defective region. Metric: mean
intersection-over-union.

**Protocol.** Leave-part-types-out: annotated defects are released for nine part
types, scoring happens on three types for which no annotated defect exists —
only flawless reference photographs.

**Source.** VisA (Visual Anomaly), Amazon — **CC BY 4.0**, verified at the
project repository and the AWS Open Data Registry. Commercial use and
redistribution permitted with attribution. Cite Zou et al., arXiv:2207.14315.

## Contents

- [`description.md`](description.md) — challenge statement (source-secret).
- [`dataset-description.md`](dataset-description.md) — dataset record with
  provenance, licence and preparation details.
- [`release-report.md`](release-report.md) — gate-by-gate results.
- [`rubrics.md`](rubrics.md) — nine initial grading rubrics for the hosting platform.
- `prepare.py` — deterministic packaging from an extracted VisA release.
- `platform_prepare.py` — hosting-platform pipeline, `prepare(raw, public, private)`.
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
and `answer.csv` sit beside it at the top level.

`platform_prepare.py` consumes that layout on the hosting side and flattens it:
the three image folders and the four public CSV files go to `public/`, while
`answer.csv` goes to `private/` and is never copied into the public package.

```bash
python platform_prepare.py --raw raw --public public --private private
```

Requires `numpy`, `pandas`, `pillow`. Deterministic: fixed hash salt and split
seed 20260810, 92 s runtime, 1.8 GB peak RSS.

## Headline numbers

| | |
| --- | --- |
| Annotated defective images | 1,200 → 1,195 independent units |
| Train / test | 900 (9 types) / 300 (3 held-out types) |
| Public / private test rows | 74 / 226 |
| Auxiliary flawless images | 9,621, of which 3,004 are of the scored types |
| Oracle | 1.000 |
| Private noise floor | sd 0.0106 · 3×sd 0.0319 |
| Strongest shortcut baseline | 0.0229 vs 0.527 reference solver |
