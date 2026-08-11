# Industrial Defect Localization

## Overview

On a manufacturing inspection line, a camera photographs every part that passes under it in a fixed rig: same lighting, same viewpoint, same placement. An automatic quality system that only answers "this part is faulty" leaves the hard work to a human, who must then find the flaw before deciding whether to rework the part or discard it. What the line actually needs is a system that points at the flaw.

The hard version of that problem is the one a factory faces whenever it starts producing something new. A new part goes into production; thousands of good units come off the line within days; but defective units are rare, and annotating where the damage is takes an expert with a mouse. Waiting to collect and label enough defects for the new part before inspection can begin is exactly the delay the factory cannot afford.

This challenge reproduces that situation. Defect boxes are released for **nine** kinds of part. Scoring happens entirely on **three other kinds of part**: their defective images are released, but the boxes marking the damage are withheld as the grading answers, so no labelled defect for those parts is available to learn from. What is provided for those three, in quantity, is flawless photographs: 3,004 images of undamaged units. A solution therefore cannot learn where damage tends to sit on the parts it will be scored on. It has to learn, from nine other part types, what "damage" looks like as a departure from correct appearance, and then apply that to a shape, material and failure mode it has never seen annotated.

The scale makes it harder. On the scored part types the flaw occupies a median of 0.34% of the image and can be as small as 0.02%, while the surrounding part looks correct and nearly identical from photo to photo. Because the imaging rig is fixed, global appearance carries almost no information about where the flaw is.

## Objective

Given a photograph of a defective manufactured part, predict four integers describing the rectangular region that contains every defective pixel: the left, top, right and bottom edges of the smallest axis-aligned rectangle covering the damage. When an image contains more than one flaw, the target is the single smallest rectangle that contains all of them. Every test image contains at least one defect, so there is no "no defect" answer.

This is a coordinate regression task, not a detection task. Each image has exactly one target and produces exactly one output row of four numbers. There is no object class to predict, no confidence score, no variable number of objects to enumerate, no score threshold, and no non-maximum suppression. Scoring compares one predicted region against one reference region per image, with no matching step and no averaging over confidence thresholds.

## Evaluation Protocol

The split is **leave-part-types-out**, not a random partition:

- Twelve part types exist in the release, coded `T01`–`T12`, 100 annotated defective images each.
- Three of the twelve were drawn by a fixed random seed and held out. Every test image belongs to one of those three, and no box for any of their defects appears in any released file.
- The nine remaining types supply all 900 boxed training images.
- Flawless, unannotated photographs are released for **all twelve types**, including the three scored ones.

This protocol is the point of the challenge. A model fitted to the positions, shapes and textures of defects on the nine training types is being asked to generalise to parts it has never seen damaged. Approaches that implicitly memorise a per-part-type prior score close to zero here: the strongest such rule baseline reaches 0.023 mean IoU, against 0.527 for a reference solver that localises correctly with noise.

## Dataset

- Defective images: 1,200 in total across 12 part types, exactly 100 per type, split 900 training / 300 test by part type. The 900 training images are released **with** their reference boxes in `train_labels.csv`. The 300 test images are released as **images only** — their boxes are the withheld answers and appear in no released file. Annotated training material therefore covers nine part types; the three scored types contribute test images and flawless references, and nothing else.
- Independent units: 1,195. Four groups of images are repeat photographs of damage already counted — three pairs and one triple, nine images standing for four units — so the 1,200 images correspond to 1,195 distinct units. Every image of a group stays on the same side of every split, and unit counts, not image counts, are what the split balances: the training pool holds 897 units and the test pool 298.
- Approximately 25% of the test units form the public leaderboard and the rest the private leaderboard: 74 public and 226 private rows. Membership is assigned per unit and never revealed.
- Auxiliary flawless images: 9,621 across all twelve types, of which 3,004 belong to the three scored types. These carry no boxes and no defects, and no test image comes from this pool.
- Images are JPEG, three-channel colour, in eight fixed resolutions between 1274×1176 and 1562×960. Every image of a given part type shares one resolution.
- On the scored part types the reference box covers a median of 0.34% of the image, a 1st percentile of 0.023% and a 99th percentile of 15.7%.
- No missing values occur in any released file.

## Files

- `train_defective/` — 900 JPEG images of defective parts, named `<id>.jpg`, from the nine training part types.
- `train_labels.csv` — 900 rows, columns `id`, `part_type`, `width`, `height`, `x_min`, `y_min`, `x_max`, `y_max`.
- `train_normal/` — 9,621 JPEG images of flawless parts from all twelve part types, named `<id>.jpg`.
- `train_normal.csv` — 9,621 rows, columns `id`, `part_type`.
- `test/` — 300 JPEG images of defective parts, named `<id>.jpg`, from the three held-out part types.
- `test.csv` — 300 rows, columns `id`, `part_type`, `width`, `height`.
- `sample_submission.csv` — 300 rows in the required submission format, filled with a whole-image box as a placeholder.

## Input Fields

- `id` — opaque 12-character lowercase hexadecimal identifier of the image, matching the image filename without its extension.
- `part_type` — anonymous part-type code, one of `T01` through `T12`. The same code always denotes the same kind of part; the codes carry no ordering. The three codes appearing in `test.csv` do not appear in `train_labels.csv`, and are the three that do appear in `train_normal.csv` without any annotated defect.
- `width`, `height` — image width and height in pixels.
- `x_min`, `y_min`, `x_max`, `y_max` (training only) — the reference box, in pixel coordinates.

## Expected Output

For each test `id`, four integers describing the predicted box:

- `x_min`, `x_max` are column indices and `y_min`, `y_max` are row indices, with the origin at the top-left pixel of the image.
- Both endpoints are inclusive: a box with `x_min = x_max` is one pixel wide.
- The constraints `0 ≤ x_min ≤ x_max ≤ width − 1` and `0 ≤ y_min ≤ y_max ≤ height − 1` must hold, using the `width` and `height` given for that image in `test.csv`.
- Each value must be written as a canonical non-negative integer: digits only, no sign, no decimal point, no thousands separator, no leading zeros, and `0` written exactly as `0`.

## Evaluation

The metric is mean intersection-over-union. For one image, let P be the predicted box and T the reference box, each treated as an inclusive set of pixels, so that the area of a box is `(x_max − x_min + 1) × (y_max − y_min + 1)`. Their intersection is the overlapping rectangle, whose width is `max(0, min(P.x_max, T.x_max) − max(P.x_min, T.x_min) + 1)` and whose height is defined analogously; the intersection area is the product of the two. The union area is `area(P) + area(T) − area(intersection)`, and the image's score is the intersection area divided by the union area.

The submission score is the arithmetic mean of the per-image scores over all scored images, weighting every image equally. The score ranges from 0.0 to 1.0, higher is better, and a submission that reproduces every reference box exactly scores 1.0. The public leaderboard scores the public subset; the final ranking uses the private subset only.

A submission that violates any structural or format rule receives the floor score 0.0 for the whole submission, with no repair and no partial credit: wrong column names or order, extra or missing columns, extra, missing or duplicated `id` values, empty or whitespace values, non-numeric or non-finite values, non-canonical integer serialisations, a box with `x_min > x_max` or `y_min > y_max`, or any coordinate outside the image bounds. Predictions are never clipped, rounded or otherwise corrected.

## Submission Format

Submit a CSV file with header `id,x_min,y_min,x_max,y_max`, in that column order, containing exactly one row for every `id` in `test.csv` (300 rows, each `id` exactly once). Row order does not matter. Example of the header and one complete row:

```
id,x_min,y_min,x_max,y_max
0250fb240c3e,612,431,689,522
```

## Licence

The photographs are used under a permissive licence that allows commercial use, modification and redistribution with attribution. The full provenance, citation and licence terms are recorded in the dataset entry this challenge is built on.

What this challenge contributes is the evaluation protocol rather than the pixels: the annotations are reduced to a single box per image, three whole part types are removed from the annotated training data and are the only ones scored, part names and filenames are replaced by opaque identifiers, near-duplicate defects are grouped so that no physical flaw crosses a split, and the metric is mean IoU on the held-out types alone.

## What Not to Use

- Do not attempt to identify the corpus these photographs were drawn from, and do not use any external mirror, derivative, reverse-image search or annotation service to recover reference boxes or masks for test images. Solutions must localise defects from the released files alone.
- General-purpose pretrained vision backbones are allowed: publicly available weights trained on general photographic corpora, used as initialisation or as frozen feature extractors, are a legitimate and expected part of a strong solution. Fine-tune them on the released images.
- Checkpoints trained on industrial defect, anomaly-detection or visual-inspection data are not allowed, and neither are weights whose training set includes the images in this challenge. If a public checkpoint advertises anomaly detection, defect segmentation or industrial inspection as its task, or is published as a baseline for an industrial-inspection benchmark, do not use it, whatever its architecture.
- No labels or annotations may come from outside this release. Pretrained weights supply visual features, not answers.
- Do not hand-annotate test images, and do not crowdsource their annotation.
- The flawless images are training material, including the 3,004 belonging to the scored part types — using them to model correct appearance is the intended solution path and is explicitly allowed. What is not allowed is obtaining a specific matching flawless image from outside this release in order to difference it against a specific test image.
- Do not probe the public leaderboard to recover private answers; submission-count limits apply.
