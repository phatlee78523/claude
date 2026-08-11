# Surface Damage Extent Estimation

## Overview

When a manufactured part comes off an inspection line showing damage, the question that decides its fate is not *whether* it is damaged but *how much*. A scuff over a tenth of a percent of the surface is reworked and shipped. A crack over a fifth of it is scrapped. Somewhere between the two sits a threshold that a plant sets by cost, and every part that passes under the camera has to be placed on one side of it. Getting that number wrong in either direction is expensive: scrapping salvageable parts wastes material, passing badly damaged ones costs a return.

This challenge is that measurement problem. Each image is one manufactured part photographed in a fixed rig — same lighting, same viewpoint, same placement — and the task is to estimate a single quantity: how much of the frame the damage occupies, in parts per million. Nothing has to be outlined or marked; one number per image is the entire output.

The measurement is hard because the quantity spans three orders of magnitude, from a couple of hundred parts per million to a fifth of the image, and because the surrounding part looks correct and nearly identical from photo to photo. Since the rig is fixed, overall appearance says almost nothing about severity — two images of the same part type, one barely marked and one badly damaged, differ in a small fraction of their pixels.

It is harder still because of how the data is split. Labelled examples are released for **nine** kinds of part. Scoring happens entirely on **three other kinds**, for which no labelled example exists at all. What is released for those three, in quantity, is flawless photographs: 3,004 images of undamaged units. So a model cannot calibrate severity against labelled examples of the parts it will be measured on. It has to learn from nine other part types what damage costs in area terms, and carry that to a shape, material and failure mode whose damaged appearance it has never had a number attached to.

## Objective

Given a photograph of a manufactured part known to be damaged, predict `extent_ppm`: the area of the damaged region expressed in parts per million of the total image area, as a single positive integer.

A value of 10,000 means the damage covers 1% of the frame. Every test image contains damage, so the answer is always at least 1; the reference values in this release run from 130 to 212,687.

This is a scalar regression task. Each image produces exactly one number. There is nothing to outline, no region to return, no class to assign, no confidence to report, and no threshold to tune.

## Evaluation Protocol

The split is **leave-part-types-out**, not a random partition:

- Twelve part types exist in the release, coded `T01`–`T12`, 100 damaged images each.
- Three of the twelve were drawn by a fixed random seed and held out. Every test image belongs to one of those three, and no reference value for any of their images appears in any released file.
- The nine remaining types supply all 900 labelled training images.
- Flawless, unlabelled photographs are released for **all twelve types**, including the three scored ones.

This protocol is the point of the challenge. A model fitted to the severity distribution of nine part types is asked to measure three it has never seen measured. Predicting a constant learned from the training types — the natural shortcut — scores 0.78, against 0.23 for a model that estimates each image correctly to within a factor of about 1.8.

## Dataset

- Damaged images: 1,200 across 12 part types, exactly 100 per type, split 900 training / 300 test by part type. The 900 training images are released **with** their reference values in `train_labels.csv`. The 300 test images are released as **images only** — their values are the withheld answers and appear in no released file.
- Independent units: 1,195. Four groups of images photograph the same physical damage more than once; every image of a group stays on the same side of every split. The training pool holds 897 units, the test pool 298.
- Approximately 25% of the test units form the public leaderboard and the rest the private leaderboard: 74 public and 226 private rows. Membership is assigned per unit and never revealed.
- Auxiliary flawless images: 9,621 across all twelve types, of which 3,004 belong to the three scored types. These carry no reference value and show no damage; no test image comes from this pool.
- Images are JPEG, three-channel colour, in eight fixed resolutions between 1274×1176 and 1562×960. Every image of a given part type shares one resolution.
- Reference values in the training set run from 20 to 429,828 parts per million, with a median of 10,871. In the test set they run from 130 to 212,687 with a median of 3,602.
- No missing values occur in any released file.

## Files

- `train_defective/` — 900 JPEG images of damaged parts, named `<id>.jpg`, from the nine training part types.
- `train_labels.csv` — 900 rows, columns `id`, `part_type`, `width`, `height`, `extent_ppm`.
- `train_normal/` — 9,621 JPEG images of flawless parts from all twelve part types, named `<id>.jpg`.
- `train_normal.csv` — 9,621 rows, columns `id`, `part_type`.
- `test/` — 300 JPEG images of damaged parts, named `<id>.jpg`, from the three held-out part types.
- `test.csv` — 300 rows, columns `id`, `part_type`, `width`, `height`.
- `sample_submission.csv` — 300 rows in the required format, filled with a constant placeholder.

## Input Fields

- `id` — opaque 12-character lowercase hexadecimal identifier of the image, matching the image filename without its extension.
- `part_type` — anonymous part-type code, one of `T01` through `T12`. The same code always denotes the same kind of part; the codes carry no ordering. The three codes appearing in `test.csv` do not appear in `train_labels.csv`, and are the three that appear in `train_normal.csv` without any labelled example.
- `width`, `height` — image width and height in pixels.
- `extent_ppm` (training only) — the reference value.

## Expected Output

For each test `id`, one integer:

- `extent_ppm` must satisfy `1 ≤ extent_ppm ≤ 1000000`.
- It must be written as a canonical positive integer: digits only, no sign, no decimal point, no thousands separator, no leading zeros, and no value of `0`.

## Evaluation

The metric is the root-mean-square error of the base-10 logarithm of the prediction:

```
score = sqrt( mean( ( log10(predicted) - log10(actual) )^2 ) )
```

**Lower is better. A perfect submission scores 0.0.** The score has no upper bound: an arbitrarily wrong prediction costs arbitrarily much.

Error is measured in log space because the quantity spans three orders of magnitude. Predicting 2,000 where the truth is 1,000 costs exactly as much as predicting 20,000 where the truth is 10,000 — in both cases the estimate is off by a factor of two, and both are equally wrong for the plant. A score of 0.30 means the typical prediction is off by a factor of 2; a score of 0.10 means a factor of 1.26.

The public leaderboard scores the public subset; the final ranking uses the private subset only.

A submission that violates a structural or format rule is **rejected**, not scored: wrong column names or order, extra or missing columns, extra, missing or duplicated `id` values, empty or whitespace values, non-numeric values, zero, negative or fractional values, non-canonical integer serialisations, or a value above 1,000,000. Predictions are never clipped, rounded or otherwise repaired.

## Submission Format

Submit a CSV file with header `id,extent_ppm`, in that column order, containing exactly one row for every `id` in `test.csv` (300 rows, each `id` exactly once). Row order does not matter. Example of the header and one complete row:

```
id,extent_ppm
0250fb240c3e,6424
```

## Licence

The photographs are used under a permissive licence that allows commercial use, modification and redistribution with attribution. The full provenance, citation and licence terms are recorded in the dataset entry this challenge is built on.

What this challenge contributes is the task and the evaluation protocol rather than the pixels: the target is reduced to a single scalar per image, three whole part types are removed from the labelled training data and are the only ones scored, part names and filenames are replaced by opaque identifiers, repeat photographs of one physical defect are grouped so that none crosses a split, and the metric is log-space RMSE on the held-out types alone.

## What Not to Use

- Do not attempt to identify the corpus these photographs were drawn from, and do not use any external mirror, derivative, reverse-image search or annotation service to recover reference values for test images. Solutions must work from the released files alone.
- General-purpose pretrained vision backbones are allowed: publicly available weights trained on general photographic corpora, used as initialisation or as frozen feature extractors, are a legitimate and expected part of a strong solution. Fine-tune them on the released images.
- Checkpoints trained on industrial defect, anomaly-detection or visual-inspection data are not allowed, and neither are weights whose training set includes the images in this challenge. If a public checkpoint advertises anomaly detection, defect segmentation or industrial inspection as its task, or is published as a baseline for an industrial-inspection benchmark, do not use it, whatever its architecture.
- No labels or annotations may come from outside this release. Pretrained weights supply visual features, not answers.
- Do not hand-measure test images, and do not crowdsource their measurement.
- The flawless images are training material, including the 3,004 belonging to the scored part types — using them to model correct appearance is the intended solution path and is explicitly allowed. What is not allowed is obtaining a specific matching flawless image from outside this release in order to difference it against a specific test image.
- Do not probe the public leaderboard to recover private answers; submission-count limits apply.
