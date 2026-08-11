# Release report — Industrial Defect Localization

Built with the `build-ml-challenges` skill. Source: VisA (Amazon), CC BY 4.0, credited in full in the dataset record only — the platform's data-secrecy gate failed the statement even for an academic citation without a link, so the statement carries an anonymous licence note.

## Design summary

| Design element | Decision |
| --- | --- |
| Real-world objective | Inspect a part the line has never seen damaged, and point at the flaw |
| Evaluation protocol | **Leave-part-types-out**: 9 types annotated for training, 3 held-out types scored |
| Independent unit | One defect-image group (images of the same physical flaw share a unit) |
| Inference input | One JPEG of a part known to be defective — `test.csv` withholds the part type; family identity must be recovered from the flawless pool |
| Target | Inclusive-pixel bounding box over all defective pixels |
| Metric | **Worst per-held-out-type mean IoU**, range 0–1, perfect 1.0, floor 0.0 for any malformed submission |
| Strongest expected shortcut | Positional/size prior learned from the training types — structurally unable to transfer |
| Why supervised learning wins | Only the flawless pool for the scored types tells a model what "correct" looks like there |
| Pretrained models | General-purpose backbones allowed; anomaly/defect-trained checkpoints and the source corpus barred |
| Compute lane | GPU-relevant: fine-tuning a general-purpose backbone at native resolution |

## What this adds to the parent corpus

VisA is normally used for in-distribution anomaly detection and segmentation, every category present at training time. This release changes the protocol, not the pixels:

- Three whole part types are removed from the annotated training data and are the only types scored.
- Flawless images of those three types are still released — 3,004 of them — so the task is transfer with unlabelled reference material, not blind extrapolation.
- Instance masks are reduced to one box per image and the masks themselves are not redistributed.
- Part names and filenames are replaced by opaque identifiers; near-duplicate defects are grouped so no physical flaw crosses a split.

The measurable consequence: the strongest rule baseline falls from **0.092** under a per-type stratified split to **0.023** under this one, because a per-part-type prior has nothing to attach to.

## Data

| Quantity | Value |
| --- | --- |
| Annotated defective images | 1,200 across 12 types, exactly 100 per type → **1,195 independent units** (4 duplicate groups at mask IoU ≥ 0.75) |
| Training | 900 images, 9 part types, 897 units |
| Test | 300 images, 3 held-out part types, 298 units |
| Public / private test rows | 74 / 226 (24.8% of units public) |
| Auxiliary flawless images | 9,621 across all 12 types, of which **3,004** belong to the scored types |
| Held-out types | drawn by seed 20260810, not hand-picked |
| Package size | public 1.92 GB, private 16 KB |
| Defect scale on scored types | box median 0.34% of image area (p1 0.023%, p99 15.7%) |

## Gate results

| Gate | Result | Evidence |
| --- | --- | --- |
| Grader: oracle perfect | PASS (1.0) | `audit/grader_report.json` |
| Grader: 11 malformed cases → floor | PASS (all 0.0) | extra/reordered/missing columns, missing/extra/duplicate IDs, blank, whitespace, nonnumeric, NaN, infinity |
| Visibility integrity | PASS | 0 units cross visibility; public unit fraction 0.248 |
| Split integrity | PASS | 0 held-out-type rows in `train_labels.csv`; test types ∩ train types = ∅; no unit spans train/test |
| Rank stability (12 noisy peers, σ = 0.22 box side) | PASS | worst-type metric: peer sd = 0.0142, 3×sd = 0.0427, far below the solver gap |
| Shortcut resistance | PASS | every rule baseline ≤ 0.0042 under the worst-type metric, against a 0.502 reference solver |
| Packaging | PASS | no answers in public files, ID sets consistent, all identifiers opaque |
| Preparation determinism/cost | PASS | fixed seed 20260810; 2 s in-platform, no randomness beyond the seeded permutation |
| Hosting-platform domain gate | PASS (after three failures) | earlier framings were classified Object Detection, Anomaly Detection and Regression, all closed; the current framing cleared the gate |
| License/provenance | PASS | CC BY 4.0 verified at two primary sources; credited in the dataset record, withheld from the challenge statement |
| Honest learned baseline / agent evaluation | NOT RUN | requires model training compute; remaining open gate |

## Shortcut baselines (private subset, worst-type metric)

| Baseline | Mean over all images | **Worst type (the score)** |
| --- | --- | --- |
| Mean relative box learned from the training types | 0.0207 | **0.0004** |
| Whole image as the box | 0.0128 | 0.0045 |
| *Jittered-oracle reference solver* | *0.527* | *0.502* |
| *Oracle* | *1.000* | *1.000* |

Scoring on the worst held-out type instead of the average cuts the strongest shortcut a further 50-fold: averaging let one easy family carry a rule that had not generalised, and the minimum does not. The strongest shortcut now reaches 0.08% of the reference solver's score. Identifier, row-order and metadata attacks were all tested and all failed.

## Known limitations

- **The parent corpus is public and ships pixel masks.** Matching a released test image back to its source annotation is the one attack this design cannot detect automatically. It is prohibited in `What Not to Use`, and the statement names neither the corpus nor its authors.
- **The platform's novelty and data-secrecy gates are mutually exclusive on attribution.** The novelty review demanded the source be named in the statement; the data-secrecy check then failed the statement for naming it even without a link, ruling the name alone 'trivially findable via a web search'. Both cannot be satisfied by any text. The statement therefore satisfies the hard gate (secrecy: no name anywhere) and bets the novelty threshold on the protocol depth — withheld family labels plus the worst-type metric — which is the substantive half of what the novelty review asked for. If novelty still fails on the missing name, the contradiction is the platform's to resolve.
- Three held-out types is a small sample of the type distribution. The leaderboard measures transfer to *these* three parts, not to industrial inspection in general.
- Boxes are tight bounds over all defects, so on images with more than one flaw the box also covers intervening sound material.
- IoU is sensitive on the smallest targets, and the scored types have smaller defects than the release average (0.34% versus 0.82% median). This is reflected in the measured noise floor.
- Agent evaluation and a trained honest baseline remain to be run on a platform with training compute; every automatable design gate passes.
- **Domain history.** The platform's domain classifier rejected three earlier framings — Object Detection, Anomaly Detection and Regression, all closed to submissions — before the current framing cleared the gate. A scalar-regression variant tried along the way also scored worse on novelty (4 against 6) and was weaker on the merits, since damage extent can be estimated from global texture statistics without finding the damage; it was discarded.

## Artifacts

| File | Rows | Note |
| --- | --- | --- |
| `public/train_labels.csv` | 900 | 9 training part types |
| `public/train_normal.csv` | 9,621 | all 12 types |
| `public/test.csv` | 300 | 3 held-out types, no boxes |
| `public/sample_submission.csv` | 300 | whole-image placeholder |
| `private/answers.csv` | 300 | boxes, visibility, unit ids |
| `public/train_defective/` | 900 files | |
| `public/test/` | 300 files | |
| `public/train_normal/` | 9,621 files | |
