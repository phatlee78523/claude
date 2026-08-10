# Dataset record — Industrial Defect Localization package

## Overview

Challenge-ready repackage of VisA (Visual Anomaly), a collection of 10,821 studio photographs of twelve types of manufactured part, of which 1,200 show a defect and carry a human-drawn instance mask marking every defective pixel. This upload is a split, re-annotated package for blind evaluation, not the unsplit parent dataset: bounding boxes derived from the masks are released for the training images, and the test boxes are withheld in a private grading file. Pixel masks themselves are not redistributed here.

## Source and License

- Source: VisA (Visual Anomaly) dataset, published by Amazon. Repository: https://github.com/amazon-research/spot-diff — paper: Zou, Jeong, Pemula, Zhang and Dabeer, *SPot-the-Difference Self-Supervised Pre-training for Anomaly Detection and Segmentation*, arXiv:2207.14315 (ECCV 2022).
- License: **CC BY 4.0** for the data. Verified from two independent primary sources: the project README states "The data is released under the CC BY 4.0 license", and the AWS Open Data Registry entry for the dataset records the same licence. Commercial use, modification and redistribution are permitted with attribution. The accompanying source code in the same repository carries a separate Apache-2.0 licence and is not used here.
- Attribution: please cite Zou et al. (2022) when using this package.
- The images are photographs of inanimate manufactured objects taken in a controlled rig. They contain no people, no personal data, and no third-party artistic works.

## File Structure

- `images/train_defective/` — 958 JPEG images, `<id>.jpg`, 176.3 MB.
- `train_labels.csv` — 958 rows: `id`, `part_type`, `width`, `height`, `x_min`, `y_min`, `x_max`, `y_max`.
- `images/train_normal/` — 9,621 JPEG images, `<id>.jpg`, 1,695.0 MB.
- `train_normal.csv` — 9,621 rows: `id`, `part_type`.
- `images/test/` — 242 JPEG images, `<id>.jpg`, 43.9 MB.
- `test.csv` — 242 rows: `id`, `part_type`, `width`, `height`.
- `sample_submission.csv` — 242 rows: `id`, `x_min`, `y_min`, `x_max`, `y_max`.
- `private/answer.csv` — 242 rows: `id`, `x_min`, `y_min`, `x_max`, `y_max`, `width`, `height`, `visibility`, `unit_id`. Grading only; never distributed.

Total public package 1.92 GB; private package 12.9 KB.

## Metadata Columns

- `id` — deterministic opaque identifier: the first 12 hexadecimal digits of SHA-256 over a fixed salt, the source part name, the normal/defective role, and the original filename. Original part names, filenames and directory structure are not recoverable from the released files.
- `part_type` — anonymous code `T01`–`T12` assigned by alphabetical order of the source part directories. The mapping to the source part names is not released.
- `width`, `height` — image dimensions in pixels, copied from the image.
- `x_min`, `y_min`, `x_max`, `y_max` — inclusive pixel coordinates of the smallest axis-aligned rectangle containing every defective pixel in the image, computed from the source instance mask.
- `visibility` — public/private leaderboard membership, assigned per independent unit.
- `unit_id` — independent-unit identifier; images sharing a unit are duplicates of one physical defect.

## Array or Media Contents

Three-channel JPEG photographs in eight fixed resolutions between 1274×1176 and 1562×960; all images of one part type share a resolution. No arrays, video or audio. Source instance masks are single-channel PNGs whose non-zero values index individual defect instances; they are consumed during preparation and are not part of the released package.

## Preparation and Quality Filters

- Boxes are derived deterministically from the source masks: a pixel is defective when its mask value is non-zero, and the box is the tight bound over all such pixels. Source masks label instances with values 1–8 rather than a binary 0/255 convention; treating them as binary by thresholding at 127 yields empty masks, and the preparation code accounts for this.
- Near-duplicate grouping: within each part type, every pair of defect masks was compared by intersection-over-union, and pairs at or above 0.75 were merged into one independent unit. Five pairs merged, taking 1,200 images to 1,195 units. Split assignment happens at unit level, so no physical defect appears on both sides.
- Splits are stratified by part type at unit level: about 20% of each type's units to test, then 25% of each type's test units to public.
- No images were dropped, resized, recompressed or otherwise altered; files are byte-identical copies of the source images under new names.
- Preparation (`prepare.py`) is deterministic (fixed salt, split seed 20260810), runs in 92 seconds and peaks at 1.8 GB of RAM.

## Intended Uses and Limitations

Intended for supervised defect localisation trained from scratch on the released files. The auxiliary flawless images make it possible to model correct appearance and treat localisation as deviation detection, which is the intended solution path.

Limitations. The parent corpus is public and ships pixel masks, so blind evaluation depends on the challenge's restriction against retrieving the source annotations; the opaque identifiers and withheld part-name mapping raise the cost of doing so but cannot prevent a determined image-matching attack. Defects are small — a median of 0.8% of image area for the box and 0.19% for the mask itself — so intersection-over-union is sensitive to a few pixels of error on the smallest targets. The twelve part types are consumer and electronic goods photographed in one laboratory rig; results do not transfer automatically to other imaging conditions or industries. With 1,195 annotated units the dataset is small for training large detectors from scratch, which is a deliberate part of the difficulty rather than an oversight.
