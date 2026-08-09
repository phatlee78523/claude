# Release gates

Do not submit to approval until every applicable gate passes.

## Product and rationale

- The title is simple and descriptive rather than branded.
- The domain classification matches the actual task and is currently enabled.
- The Overview explains a concrete real-world motivation and the exact prediction objective.
- Novelty comes from the task design, not wording or a renamed standard benchmark.

## License and provenance

- The original source and license were verified from a primary page.
- Commercial use and redistribution are allowed for the intended package.
- Required attribution and acknowledgements are present in the dataset record.
- The challenge statement does not reveal lookup keys that compromise blind evaluation.

## Dataset quality

- Count independent units as well as derived rows.
- Standard ML tasks have at least roughly 1,000 training examples; recognize that 2,000–5,000 rows can still be small for from-scratch or complex multimodal work.
- Test is normally 15–25% of train and large enough for stable evaluation.
- Public/private membership is assigned by independent unit.
- Important private classes and groups have adequate support.
- Preparation is deterministic, memory-bounded, and within runtime limits.

## Grader

- Oracle reaches the documented perfect score.
- Constant, shuffled, prior, and malformed submissions behave as expected.
- Extra/reordered columns and missing/extra/duplicate IDs return the floor.
- Blank, nonnumeric, nonfinite, invalid-range, negative, and zero-sum predictions return the floor where applicable.
- Every custom metric term and weight is fully documented.

## Shortcut resistance

- Identifier, filename, row-order, metadata, duplicate, paired-view, and source-lookup baselines were tested.
- No simple rule or deterministic parser reaches the intended model score band.
- Private data contains only what grading requires.
- `What Not to Use` addresses actual task-specific threats.

## Compute relevance and agent evaluation

- GPU relevance is intrinsic when submitted as a GPU challenge.
- Run at least three comparable solver attempts when agent evaluation is required.
- Avoid flat results; rerun isolated failures instead of counting an unlucky zero.
- Meet the requested difficulty band through task design rather than scorer suppression.

## Leaderboard integrity

- Zero independent units cross visibility.
- Oracle public and private scores both reach perfect with negligible gap.
- At least ten equal-quality noisy private submissions were scored.
- Record private `sd` and range.
- Meaningful solver gaps exceed `2 × sd`; prefer `3 × sd`.

## Artifact

- Public output contains no answers or private manifests.
- File names, schemas, counts, encodings, and sizes match the documentation.
- The challenge description has no outer triple-backtick fence and includes a complete submission example.
- Record artifact hash, runtime, peak memory, test results, and final path.
