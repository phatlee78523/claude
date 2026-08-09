# Anti-cheat and shortcut audit

## Threat model

Assume a solver will inspect every public byte and exploit any deterministic relationship permitted by the files. A prohibition in `What Not to Use` is not a substitute for removing an avoidable leak.

## Source and identity leakage

- Replace original IDs, filenames, paths, timestamps, coordinates, catalog keys, URLs, hashes, and sequential indices with deterministic opaque identifiers.
- Remove or coarsen metadata that permits direct catalog lookup or target reconstruction.
- Group exact and near duplicates before splitting.
- Search public data for labels embedded in filenames, directory names, schemas, image pixels, EXIF, archive comments, Parquet metadata, or row order.
- Test reverse matching and nearest-neighbor retrieval when multiple views or variants derive from one source.

## Target leakage

- Fit preprocessing only on training data when it uses labels or distribution statistics.
- Generate the split before augmentations, windows, crops, variants, or per-target rows.
- Ensure masks, padding, crop bounds, array lengths, missingness, file sizes, and rendering artifacts do not encode the answer.
- Never expose a clean companion view that directly reveals a held-out target unless cross-view reasoning is the intended task and is evaluated on unseen groups.
- Do not use answer-dependent random seeds or stable token mappings that can be inverted from IDs.

## Rule and template shortcuts

Evaluate constants, majority values, priors, simple geometry, regexes, deterministic parsers, nearest neighbors, memorized templates, per-group means, row-position rules, filename rules, and low-capacity tree models. Compare them with an honest learned baseline.

If a rule baseline reaches the target model band, redesign the target, remove the feature, increase conditional diversity, or hold out the governing groups. Do not make the grader obscure correct answers merely to suppress the shortcut.

## External lookup

Keep required attribution in the dataset record, but do not reveal searchable source-specific keys in the blind challenge statement. Where licensing permits, transform and anonymize data enough that direct answer lookup is impractical. Add challenge-specific restrictions against external copies, APIs, reverse search, and manual test annotation, but assume technical prevention is stronger than policy text.

## Grader attacks

Require exact columns and identifiers. Reject duplicates, missing/extra rows, blanks, nonnumeric values, NaN, infinity, out-of-range values, negative probabilities, nonpositive probability sums, unknown tokens, invalid geometry, and noncanonical strings with the floor score. Do not substitute priors, means, clipped values, or normalized fallbacks.

Test malformed near-perfect submissions because one bad row can otherwise retain a misleading score near 1.0.

## Solvability

After removing shortcuts, confirm that the training input still contains genuine predictive signal. Keep enough independent training units for the selected model family and enough private support for each important class or group. Difficulty caused by disjoint semantics with no bridge between train and test is not useful difficulty.
