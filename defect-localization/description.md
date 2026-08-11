# Industrial Defect Localization

## Overview

On a manufacturing inspection line, a camera photographs every part that passes under it in a fixed rig: same lighting, same viewpoint, same placement. An automatic quality system that only answers "this part is faulty" leaves the hard work to a human, who must then find the flaw before deciding whether to rework the part or discard it. What the line actually needs is a system that points at the flaw.

This challenge asks for exactly that. Each image shows one manufactured part that is known to be defective, and the task is to regress the four coordinates of the rectangle enclosing the damaged region. The difficulty is one of scale: the flaw occupies a median of 0.8% of the image and can be as small as 0.01%, while the surrounding part looks correct and nearly identical from photo to photo. Because the imaging rig is fixed, global appearance carries almost no information about where the flaw is; the answer must come from finding the small local deviation from how the part is supposed to look. Twelve different part types are covered, so a solution has to generalise across shapes, materials and failure modes rather than memorise one production line.

The released data reflects how an inspection line actually accumulates evidence: defective examples are scarce and expensive to annotate, while flawless parts are abundant. Alongside the annotated defective images, every flawless photograph of the same twelve part types is provided, unannotated, so that a solution can learn what "correct" looks like and treat localisation as a search for the deviation.

## Objective

Given a photograph of a defective manufactured part, predict four integers describing the rectangular region that contains every defective pixel: the left, top, right and bottom edges of the smallest axis-aligned rectangle covering the damage. When an image contains more than one flaw, the target is the single smallest rectangle that contains all of them. Every test image contains at least one defect, so there is no "no defect" answer.

This is a coordinate regression task, not a detection task. Each image has exactly one target and produces exactly one output row of four numbers. There is no object class to predict, no confidence score, no variable number of objects to enumerate, no score threshold, and no non-maximum suppression. Scoring compares one predicted region against one reference region per image, with no matching step and no averaging over confidence thresholds.

## Dataset

- Annotated defective images: 1,200 in total, drawn from 12 part types, split into 958 training and 242 test images.
- Independent units: 1,195. Five pairs of images capture the same physical flaw twice; each such pair is one unit and both of its images are kept on the same side of every split.
- Test images are 20.2% of all annotated images. Approximately 25% of the test units form the public leaderboard and the rest the private leaderboard; membership is assigned per unit and never revealed.
- Auxiliary flawless images: 9,621, covering the same 12 part types. These carry no boxes and no defects. They are training material only; no test image comes from this pool.
- Every part type contributes 78–80 training images and 20–22 test images, so no type dominates.
- Images are JPEG, three-channel colour, in eight fixed resolutions between 1274×1176 and 1562×960. Every image of a given part type shares one resolution.
- No missing values occur in any released file.

## Files

- `train_defective/` — 958 JPEG images of defective parts, named `<id>.jpg`.
- `train_labels.csv` — 958 rows, columns `id`, `part_type`, `width`, `height`, `x_min`, `y_min`, `x_max`, `y_max`.
- `train_normal/` — 9,621 JPEG images of flawless parts, named `<id>.jpg`.
- `train_normal.csv` — 9,621 rows, columns `id`, `part_type`.
- `test/` — 242 JPEG images of defective parts, named `<id>.jpg`.
- `test.csv` — 242 rows, columns `id`, `part_type`, `width`, `height`.
- `sample_submission.csv` — 242 rows in the required submission format, filled with a whole-image box as a placeholder.

## Input Fields

- `id` — opaque 12-character lowercase hexadecimal identifier of the image, matching the image filename without its extension.
- `part_type` — anonymous part-type code, one of `T01` through `T12`. The same code always denotes the same kind of part; the codes carry no ordering.
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

Submit a CSV file with header `id,x_min,y_min,x_max,y_max`, in that column order, containing exactly one row for every `id` in `test.csv` (242 rows, each `id` exactly once). Row order does not matter. Example of the header and one complete row:

```
id,x_min,y_min,x_max,y_max
0250fb240c3e,612,431,689,522
```

## What Not to Use

- The images derive from a corpus that is publicly available under a permissive licence and that ships pixel-level defect annotations. Do not attempt to identify the originating corpus, retrieve the source images, or use any external annotation, mirror, or search service to recover the reference boxes for test images. Solutions must localise defects from the released files alone.
- General-purpose pretrained vision backbones are allowed: publicly available weights trained on general photographic corpora, used as initialisation or as frozen feature extractors, are a legitimate and expected part of a strong solution. Fine-tune them on the released images.
- Checkpoints trained on industrial defect, anomaly-detection or visual-inspection data are not allowed, and neither are weights whose training set includes the images in this challenge or the corpus they derive from. If a public checkpoint advertises anomaly detection, defect segmentation or industrial inspection as its task, do not use it.
- No labels or annotations may come from outside this release. Pretrained weights supply visual features, not answers.
- Do not hand-annotate test images, and do not crowdsource their annotation.
- The auxiliary flawless images are training material. Do not attempt to pair a specific test image with a specific flawless image obtained outside this release in order to read off the difference; using the flawless pool as a general model of correct appearance is the intended use and is allowed.
- Do not probe the public leaderboard to recover private answers; submission-count limits apply.
