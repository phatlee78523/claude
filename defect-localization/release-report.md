# Release report — Surface Damage Extent Estimation

Built with the `build-ml-challenges` skill. Source: VisA (Amazon), CC BY 4.0, credited in the dataset record — deliberately not in the challenge statement.

## Design summary

| Design element | Decision |
| --- | --- |
| Real-world objective | Measure how much of a part is damaged, to decide rework against scrap |
| Evaluation protocol | **Leave-part-types-out**: 9 types annotated for training, 3 held-out types scored |
| Independent unit | One defect-image group (images of the same physical flaw share a unit) |
| Inference input | One JPEG of a part known to be defective, plus its anonymous part type |
| Target | `extent_ppm`, damaged area in parts per million of image area, integer 1..1,000,000 |
| Metric | RMSE of log10, **minimise**, perfect 0.0, unbounded above; malformed submissions rejected |
| Strongest expected shortcut | Constant prediction learned from the training types — 0.784 |
| Why supervised learning wins | Only the flawless pool for the scored types calibrates what undamaged looks like there |
| Pretrained models | General-purpose backbones allowed; anomaly/defect-trained checkpoints and the source corpus barred |
| Compute lane | GPU-relevant: fine-tuning a general-purpose backbone at native resolution |

## What this adds to the parent corpus

VisA is normally used for in-distribution anomaly detection and segmentation, every category present at training time. This release changes the protocol, not the pixels:

- Three whole part types are removed from the annotated training data and are the only types scored.
- Flawless images of those three types are still released — 3,004 of them — so the task is transfer with unlabelled reference material, not blind extrapolation.
- Instance masks are reduced to one scalar per image; neither the masks nor the boxes are redistributed.
- Part names and filenames are replaced by opaque identifiers; near-duplicate defects are grouped so no physical flaw crosses a split.

The measurable consequence: with the scored types absent from the labelled data, the natural per-type prior collapses to a single constant, which scores **0.784** against **0.227** for a solver that measures each image.

## Data

| Quantity | Value |
| --- | --- |
| Damaged images | 1,200 across 12 types, exactly 100 per type → **1,195 independent units** (4 repeat groups at mask IoU ≥ 0.75) |
| Training | 900 images, 9 part types, 897 units |
| Test | 300 images, 3 held-out part types, 298 units |
| Public / private test rows | 74 / 226 (24.8% of units public) |
| Auxiliary flawless images | 9,621 across all 12 types, of which **3,004** belong to the scored types |
| Held-out types | drawn by seed 20260810, not hand-picked |
| Package size | public 1.92 GB, private 16 KB |
| Target on scored types | 130..212,687 ppm, median 3,602; log10 spread 2.11..5.33, sd 0.653 |

## Gate results

| Gate | Result | Evidence |
| --- | --- | --- |
| Grader: oracle perfect | PASS (0.0) | exact reference values reproduce the perfect score |
| Grader: malformed submissions rejected | PASS | wrong/extra/missing/reordered columns, wrong row count, duplicate or unknown ids, blank, whitespace, nonnumeric, zero, negative, fractional, leading zeros, out of range |
| Visibility integrity | PASS | 0 units cross visibility; public unit fraction 0.248 |
| Split integrity | PASS | 0 held-out-type rows in `train_labels.csv`; test types ∩ train types = ∅; no unit spans train/test |
| Rank stability (12 noisy peers, σ = 0.25 dex) | PASS | private sd = 0.0106; 3×sd = 0.0318 |
| Shortcut resistance | PASS | best constant baseline 0.784 against a 0.227 reference solver |
| Packaging | PASS | no answers in public files, ID sets consistent, all identifiers opaque |
| Preparation determinism/cost | PASS | fixed seed 20260810; 2 s in-platform, no randomness beyond the seeded permutation |
| License/provenance | PASS | CC BY 4.0 verified at two primary sources; credited in the dataset record, withheld from the challenge statement |
| Honest learned baseline / agent evaluation | NOT RUN | requires model training compute; remaining open gate |

## Baselines (private subset, lower is better)

| Baseline | Score |
| --- | --- |
| Predict 1 | 3.629 |
| Predict 1,000,000 | 2.517 |
| Constant = arithmetic mean of training values | 1.185 |
| Constant = median of training values | 0.803 |
| Constant = geometric mean of training values | **0.784** ← best constant |
| *Reference solver, each image right to within a factor of ~1.8* | *0.227* |
| *Oracle* | *0.000* |

The best constant baseline is 3.5× worse than a solver that actually measures each image. Because the scored part types never appear in the labelled training data, a per-type prior — the natural shortcut — degenerates to exactly this constant.

## Known limitations

- **The parent corpus is public and ships pixel masks.** Matching a released test image back to its source annotation is the one attack this design cannot detect automatically. It is prohibited in `What Not to Use`, and the challenge statement withholds the corpus name, the citation and the link so that the attack is not handed to solvers.
- **The platform's own gates conflict on this point.** Its novelty review asked for the source to be credited by name in the challenge statement; its data-secrecy check then failed the statement for naming and linking a publicly downloadable source, on the ground that it makes the reference boxes recoverable. The resolution is to separate the two audiences: the challenge statement, which agents read, carries a licence note without a name; the dataset record, published alongside, carries the full citation, repository link and CC BY 4.0 terms. That satisfies the licence, which requires attribution but not attribution inside the problem prompt.
- Three held-out types is a small sample of the type distribution. The leaderboard measures transfer to *these* three parts, not to industrial inspection in general.
- The target is derived from the bounding rectangle of the damage, so on images with more than one damaged spot it also counts the sound material between them. It measures the extent of the affected region, not the damaged pixel count.
- A model can in principle estimate extent from global texture statistics without ever finding the damage. That is a legitimate solution to this task, and it is why this challenge measures severity rather than position.
- Agent evaluation and a trained honest baseline remain to be run on a platform with training compute; every automatable gate passes.

## Artifacts

| File | Rows | Note |
| --- | --- | --- |
| `public/train_labels.csv` | 900 | 9 training part types, with `extent_ppm` |
| `public/train_normal.csv` | 9,621 | all 12 types |
| `public/test.csv` | 300 | 3 held-out types, no target |
| `public/sample_submission.csv` | 300 | constant placeholder 10,078 |
| `private/answers.csv` | 300 | `extent_ppm`, visibility, unit ids |
| `public/train_defective/` | 900 files | |
| `public/test/` | 300 files | |
| `public/train_normal/` | 9,621 files | |
