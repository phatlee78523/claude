# Initial rubrics — Industrial Defect Localization

Ten criteria for the hosting platform's rubric editor. Each is grounded in a
measured property of this release, is checkable from a solution notebook, and can
genuinely fail. All ten are REQUIRED or RECOMMENDED; none is UNIVERSAL.

The design centre of this challenge is the leave-part-types-out protocol, so the
rubrics that separate a serious attempt from a careless one are the ones about
validation design (#1), family recovery (#3) and the worst-type metric (#7, #10).

| # | Type | Importance | Criterion |
| --- | --- | --- | --- |
| 1 | TRAINING | REQUIRED | Validates by holding out whole part types from the nine training types, not by a random split of the 900 training images. The test set contains only part types absent from `train_labels.csv`, so a random-split validation score measures in-distribution fit and systematically overstates leaderboard performance. |
| 2 | TRAINING | REQUIRED | Never trains, fits, or tunes on the contents of `test/`, and does not use test images for any form of statistics, normalisation, or pseudo-labelling. Using the flawless images of the scored part types from `train_normal/` is allowed and intended; using the test images themselves is not. |
| 3 | DATA_HANDLING | REQUIRED | Recovers the part family of each test image, since `test.csv` withholds `part_type`. Grouping test images by appearance against the flawless pool is the intended route; treating all 300 as one undifferentiated set forfeits the reference material the protocol supplies. Also reads `width` and `height` per image from `test.csv` instead of assuming one resolution. The release contains eight distinct resolutions between 1274×1176 and 1562×960, one per part type. A solution that resizes images for inference maps predicted coordinates back onto the original pixel grid of that specific image; coordinates left in a resized frame are scored as-is and collapse the score. |
| 4 | DATA_HANDLING | REQUIRED | Writes exactly 300 rows with the header `id,x_min,y_min,x_max,y_max`, every `id` from `test.csv` present exactly once, and every coordinate a canonical non-negative integer — no decimal point, no sign, no leading zeros, no blanks. Validates its own file before submitting rather than relying on the grader to repair it; any structural violation floors the entire submission to 0.0. |
| 5 | DATA_HANDLING | REQUIRED | Emits boxes that satisfy `0 ≤ x_min ≤ x_max ≤ width − 1` and `0 ≤ y_min ≤ y_max ≤ height − 1` for that image. Clamping or rejecting out-of-range model output is the solution's responsibility; a single row outside the image bounds zeroes the whole submission. |
| 6 | MODELING | RECOMMENDED | Uses the 3,004 flawless images of the three scored part types. They are the only information in the release about how those parts look undamaged, and the protocol supplies them deliberately. A solution that trains solely on the 900 annotated images of the other nine types discards the one signal available for the parts it is actually scored on. |
| 7 | MODELING | RECOMMENDED | Does not encode a per-part-type positional or size prior learned from the training types. Such a prior cannot transfer: the scored types are absent from the annotated training data, and a rule baseline of exactly this kind scores 0.0004 under the worst-type metric used here. |
| 8 | MODELING | RECOMMENDED | Preserves enough spatial resolution for the target scale. On the scored part types the reference box covers a median of 0.34% of the image and a 1st percentile of 0.023%. Regressing four numbers from a single heavily downsampled global descriptor cannot localise targets this small; the design should keep localisation information at a fine enough stride, by any means. |
| 9 | TRAINING | RECOMMENDED | Builds its validation split so that near-duplicate images do not straddle the boundary. Four groups of training images photograph the same physical flaw more than once; if such a group is split across train and validation, the validation score is inflated by memorisation rather than generalisation. |
| 10 | AGENT_BEHAVIOR | RECOMMENDED | Compares its model against at least one trivial baseline before accepting it — a constant box, the whole image, or a mean box learned from the training types. Under the worst-type metric those score 0.0004–0.0042 here; a learned model scoring inside that band has not learned to localise, and the solution should say so rather than report it as a result. |

## Why these and not others

- **Specificity.** Every criterion names a measured quantity from this release —
  nine training types against three scored ones, 900 and 300 images, 3,004
  flawless images of the scored types, eight resolutions, 0.34% median box area,
  four duplicate groups, the 0.0004–0.0042 worst-type baseline band. None would
  transfer unchanged to another challenge.
- **Balance.** Criteria 1, 3, 6, 8, 9 and 10 state what a good solution does;
  criteria 2, 4, 5 and 7 state what it must not do.
- **Approach-neutral.** No architecture, library or training recipe is named.
  Criterion 8 constrains the property — localisation resolution — not the method.
- **Discrimination.** Each is failable by a plausible attempt. Criterion 1 fails
  the default `train_test_split`; criterion 3 fails any pipeline that resizes and
  forgets to invert; criterion 4 fails a float-formatted CSV; criterion 7 fails
  the most natural shortcut on this data.
- **Importance mix.** Five REQUIRED, five RECOMMENDED, zero UNIVERSAL, so the set
  is entirely task-specific rather than generic best practice.
