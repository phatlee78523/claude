# Initial rubrics — Industrial Defect Localization

Nine criteria for the hosting platform's rubric editor. Each is grounded in a
measured property of this release, is checkable from a solution notebook, and
can genuinely fail. Eight of the nine are REQUIRED or RECOMMENDED.

| # | Type | Importance | Criterion |
| --- | --- | --- | --- |
| 1 | DATA_HANDLING | REQUIRED | Reads `width` and `height` per image from `test.csv` instead of assuming one resolution. The release contains eight distinct resolutions between 1274×1176 and 1562×960, one per part type. A solution that resizes images for inference maps predicted coordinates back onto the original pixel grid of that specific image; coordinates left in a resized frame are scored as-is and collapse the score. |
| 2 | DATA_HANDLING | REQUIRED | Writes exactly 242 rows with the header `id,x_min,y_min,x_max,y_max`, every `id` from `test.csv` present exactly once, and every coordinate a canonical non-negative integer — no decimal point, no sign, no leading zeros, no blanks. Validates its own file before submitting rather than relying on the grader to repair it; any structural violation floors the entire submission to 0.0. |
| 3 | DATA_HANDLING | REQUIRED | Emits boxes that satisfy `0 ≤ x_min ≤ x_max ≤ width − 1` and `0 ≤ y_min ≤ y_max ≤ height − 1` for that image. Clamping or rejecting out-of-range model output is the solution's responsibility; a single row outside the image bounds zeroes the whole submission. |
| 4 | MODELING | RECOMMENDED | Makes use of the 9,621 unannotated flawless images, not only the 958 annotated defective ones. They are 89% of the released images and the only source of information about how each part type looks when undamaged. A solution that trains exclusively on the annotated subset leaves the bulk of the release unused. |
| 5 | MODELING | RECOMMENDED | Preserves enough spatial resolution for the target scale. The reference box covers a median of 0.8% of the image and a 1st percentile of 0.011%. Regressing four numbers from a single heavily downsampled global descriptor cannot localise targets this small; the design should keep localisation information at a fine enough stride, by any means. |
| 6 | TRAINING | REQUIRED | Never trains, fits, or tunes on the contents of `test/`, and does not use test images for any form of statistics, normalisation, or pseudo-labelling. |
| 7 | TRAINING | RECOMMENDED | Builds its validation split so that near-duplicate images do not straddle the boundary. Five pairs of training images photograph the same physical flaw twice; if such a pair is split across train and validation, the validation score is inflated by memorisation rather than generalisation. |
| 8 | TRAINING | RECOMMENDED | Reports validation performance broken down by `part_type`, not only in aggregate. Each of the twelve types contributes just 78–80 training images and differs in shape, material and failure mode, so a strong mean can conceal a type the model fails outright. |
| 9 | AGENT_BEHAVIOR | RECOMMENDED | Compares its model against at least one trivial baseline before accepting it — a constant box, the whole image, or the mean box per part type. Those reach roughly 0.03–0.09 mean IoU on this data; a learned model scoring inside that band has not learned to localise and the solution should say so rather than report it as a result. |

## Why these and not others

- **Specificity.** Every criterion names a measured quantity from this release —
  eight resolutions, 9,621 flawless images, 0.8% median box area, 78–80 images
  per type, five duplicate pairs, the 0.03–0.09 baseline band. None of them
  would transfer unchanged to another challenge.
- **Balance.** Criteria 1, 4, 5, 8 and 9 state what a good solution does;
  criteria 2, 3, 6 and 7 state what it must not do.
- **Approach-neutral.** No architecture, library or training recipe is named.
  Criterion 5 constrains the property (localisation resolution), not the method.
- **Discrimination.** Each one is failable by a plausible solution. Criterion 1
  fails any pipeline that resizes and forgets to invert; criterion 2 fails a
  float-formatted CSV; criterion 7 fails the default random split.
- **Importance mix.** Four REQUIRED, five RECOMMENDED, zero UNIVERSAL, so the
  set is entirely task-specific rather than generic best practice.
