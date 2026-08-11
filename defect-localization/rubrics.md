# Initial rubrics — Surface Damage Extent Estimation

Ten criteria for the hosting platform's rubric editor. Each is grounded in a
measured property of this release, is checkable from a solution notebook, and can
genuinely fail. All ten are REQUIRED or RECOMMENDED; none is UNIVERSAL.

The design centre of this challenge is the leave-part-types-out protocol, so the
rubrics that separate a serious attempt from a careless one are the ones about
validation design (#1) and about not falling back on a severity prior (#7).

| # | Type | Importance | Criterion |
| --- | --- | --- | --- |
| 1 | TRAINING | REQUIRED | Validates by holding out whole part types from the nine training types, not by a random split of the 900 training images. The test set contains only part types absent from `train_labels.csv`, so a random-split validation score measures in-distribution fit and systematically overstates leaderboard performance. |
| 2 | TRAINING | REQUIRED | Never trains, fits, or tunes on the contents of `test/`, and does not use test images for any form of statistics, normalisation, or pseudo-labelling. Using the flawless images of the scored part types from `train_normal/` is allowed and intended; using the test images themselves is not. |
| 3 | DATA_HANDLING | REQUIRED | Treats the target as relative, not absolute. `extent_ppm` is a fraction of image area, and the release contains eight distinct resolutions between 1274×1176 and 1562×960, one per part type. A pipeline that measures damage in raw pixels and forgets to divide by that image's `width × height` is systematically wrong by the ratio between resolutions. |
| 4 | DATA_HANDLING | REQUIRED | Writes exactly 300 rows with the header `id,extent_ppm`, every `id` from `test.csv` present exactly once, and every value a canonical positive integer — no decimal point, no sign, no leading zeros, no zero, no blanks. Validates its own file before submitting; any structural violation causes the whole submission to be rejected rather than scored. |
| 5 | MODELING | REQUIRED | Fits and predicts in log space, or otherwise accounts for the target spanning three orders of magnitude. The metric is RMSE of `log10`, so a model trained to minimise squared error on the raw parts-per-million value optimises the wrong loss and is dominated by the few largest examples. |
| 6 | MODELING | RECOMMENDED | Uses the 3,004 flawless images of the three scored part types. They are the only information in the release about how those parts look undamaged, and the protocol supplies them deliberately. A solution that trains solely on the 900 labelled images of the other nine types discards the one signal available for the parts it is actually measured on. |
| 7 | MODELING | RECOMMENDED | Does not fall back on a per-part-type severity prior learned from the training types. Such a prior cannot transfer: the scored types are absent from the labelled training data, and constant baselines of exactly this kind score 0.78–1.19, against 0.23 for a model that measures each image. |
| 8 | MODELING | RECOMMENDED | Preserves enough spatial detail for the scale being measured. The median test value is 3,602 parts per million — 0.36% of the frame — and the smallest is 130. A model that reduces the image to a single heavily downsampled global descriptor discards the evidence the measurement depends on; the design should retain fine detail, by any means. |
| 9 | TRAINING | RECOMMENDED | Builds its validation split so that repeat photographs do not straddle the boundary. Four groups of training images capture the same physical damage more than once; if such a group is split across train and validation, the validation score is flattered by memorisation rather than generalisation. |
| 10 | AGENT_BEHAVIOR | RECOMMENDED | Compares its model against a constant-prediction baseline before accepting it. Predicting the geometric mean of the training values scores 0.78 here; a learned model that does not clearly beat that has not learned to measure anything, and the solution should say so rather than report it as a result. |

## Why these and not others

- **Specificity.** Every criterion names a measured quantity from this release —
  nine training types against three scored ones, 900 and 300 images, 3,004
  flawless images of the scored types, eight resolutions, a 3,602 ppm median and
  a 130 ppm minimum, four repeat groups, the 0.78 constant baseline. None would
  transfer unchanged to another challenge.
- **Balance.** Criteria 1, 3, 6, 8, 9 and 10 state what a good solution does;
  criteria 2, 4, 5 and 7 state what it must not do.
- **Approach-neutral.** No architecture, library or training recipe is named.
  Criterion 8 constrains the property — retained spatial detail — not the method.
- **Discrimination.** Each is failable by a plausible attempt. Criterion 1 fails
  the default `train_test_split`; criterion 3 fails a pixel-count pipeline that
  forgets to normalise; criterion 4 fails a float-formatted CSV; criterion 5
  fails a model trained on raw-scale squared error; criterion 7 fails the most
  natural shortcut on this data.
- **Importance mix.** Five REQUIRED, five RECOMMENDED, zero UNIVERSAL, so the set
  is entirely task-specific rather than generic best practice.
