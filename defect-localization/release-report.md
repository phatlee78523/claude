# Release report — Industrial Defect Localization

Built with the `build-ml-challenges` skill on 2026-08-10. Source: VisA (Amazon), CC BY 4.0.

## Design summary

| Design element | Decision |
| --- | --- |
| Real-world objective | Point an inspection line at the flaw, not merely flag the part |
| Independent unit | One defect-image group (images of the same physical flaw share a unit) |
| Inference input | One JPEG of a part known to be defective, plus its anonymous part type |
| Target | Inclusive-pixel bounding box over all defective pixels |
| Metric | Mean IoU, range 0–1, perfect 1.0, floor 0.0 for any malformed submission |
| Strongest expected shortcut | Per-part-type positional prior; image retrieval against the training set |
| Why supervised learning wins | Fixed rig removes global cues; only local deviation from the flawless appearance localises the flaw |
| Compute lane | GPU-relevant (image detection/segmentation trained from scratch), CPU-feasible at reduced resolution |

## Data

| Quantity | Value |
| --- | --- |
| Annotated defective images | 1,200 → **1,195 independent units** (5 duplicate pairs merged at mask IoU ≥ 0.75) |
| Train / test defective | 958 / 242 (test = 20.2% of train) |
| Public / private test units | 60 / 180 (25.0% public) |
| Auxiliary flawless images | 9,621 (training only, no boxes) |
| Part types | 12, each 78–80 train and 20–22 test images; private support 15–17 per type |
| Package size | public 1.92 GB, private 12.9 KB |
| Defect scale | box median 0.82% of image area (p1 0.011%, p99 29.4%); mask median 0.19% |

## Gate results

| Gate | Result | Evidence |
| --- | --- | --- |
| Grader: oracle perfect | PASS (1.0) | `audit/grader_report.json` |
| Grader: 11 malformed cases → floor | PASS (all 0.0) | extra/reordered/missing columns, missing/extra/duplicate IDs, blank, whitespace, nonnumeric, NaN, infinity |
| Visibility integrity | PASS | 0 units cross visibility; public unit fraction 0.250 ∈ [0.20, 0.30] |
| Oracle public/private gap | PASS | 1.0 vs 1.0, gap 0.0 |
| Rank stability (12 noisy peers, σ = 0.22 box side) | PASS | private sd = 0.0107, range = 0.0416; 2×sd = 0.0214, 3×sd = 0.0321; design solver gap 0.05 > 3×sd |
| Shortcut resistance | PASS | see table below — every rule baseline ≤ 0.092 against a 0.512 reference solver |
| Packaging | PASS (10/10) | no answers in public files, ID sets consistent, all identifiers opaque, hashes recorded |
| Preparation determinism/cost | PASS | fixed salt + seed 20260810; 92 s runtime, 1.8 GB peak RSS |
| License/provenance | PASS | CC BY 4.0 verified at two primary sources; attribution in dataset record; challenge statement source-secret |
| Honest learned baseline / agent evaluation | NOT RUN | requires model training compute; remaining open gate |

## Shortcut baselines (private subset)

| Baseline | Mean IoU |
| --- | --- |
| Whole image as the box | 0.0422 |
| Constant median-size box at image centre | 0.0283 |
| Mean box per part type (from train) | 0.0804 |
| Union of all train boxes per part type | **0.0918** ← strongest rule |
| Rule derived from the hashed identifier | 0.0180 |
| 1-NN image retrieval from train, copy its box | 0.0650 |
| *Jittered-oracle reference solver* | *0.5120* |
| *Oracle* | *1.0000* |

The strongest shortcut reaches 18% of the reference solver's score. Identifier, row-order, metadata and retrieval attacks were all tested and all failed.

## Bug found and fixed during the audit

The first `grade.py` returned 0.0 for every submission including the oracle. Cause: on pandas 3.0, `Series.values` on a string column yields an `ArrowStringArray`, which `DataFrame.set_index` rejects; the required catch-all exception handler converted the resulting `TypeError` into the floor score. Indexing now goes through plain Python lists. This is exactly the failure mode the oracle-perfect check exists to catch, and it would have shipped a challenge on which nobody could score above zero.

## Known limitations

- The parent corpus is public and distributes pixel masks. Opaque identifiers and the withheld part-name mapping raise the cost of recovering answers, but a determined image-matching attack against the source remains possible; this is disclosed in the dataset record and restricted in `What Not to Use`.
- Boxes are tight bounds over all defects, so on the 23.7% of images with more than one flaw the box also covers intervening sound material.
- IoU is sensitive on the smallest targets, where a few pixels of error move the score materially. This is reflected in the measured noise floor and is why the required solver gap is 3×sd.
- Agent evaluation and a trained honest baseline remain to be run on a platform with training compute; every automatable gate passes.

## Artifacts

| File | SHA-256 (16) / count | Size |
| --- | --- | --- |
| `public/train_labels.csv` | c26b60b16bfe8ede | 48 KB |
| `public/test.csv` | 0629ea4a841031e0 | 8 KB |
| `public/train_normal.csv` | 385045e5b1c35ced | 202 KB |
| `public/sample_submission.csv` | 3c6ca21ec7f678a6 | 8 KB |
| `private/answer.csv` | fa87c5450e8eac48 | 13 KB |
| `public/train_defective/` | 958 files | 176.3 MB |
| `public/test/` | 242 files | 43.9 MB |
| `public/train_normal/` | 9,621 files | 1,695.0 MB |
