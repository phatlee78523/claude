---
name: build-ml-challenges
description: Design, implement, harden, and review competition-ready machine-learning challenges. Use for challenge ideation, niche-dataset research, commercial-license verification, dataset and challenge descriptions, prepare.py and grade.py creation, anti-cheat audits, CPU/GPU relevance checks, public/private split stability, agent baseline evaluation, reviewer fixes, and final packaging.
---

# Build ML Challenges

Build a challenge whose difficulty comes from learnable generalization, not leakage, tiny test sets, brittle formatting, or grader behavior. Treat novelty, solvability, integrity, compute relevance, and leaderboard stability as separate release gates.

## Load the relevant references

- Read [references/description-template.md](references/description-template.md) whenever drafting or revising dataset or challenge copy.
- Read [references/anti-cheat.md](references/anti-cheat.md) before designing targets, writing `prepare.py`, or accepting an apparently strong baseline.
- Read [references/source-selection.md](references/source-selection.md) before evaluating or downloading a candidate dataset.
- Read [references/split-stability.md](references/split-stability.md) before choosing train/test or public/private membership.
- Read [references/release-gates.md](references/release-gates.md) before packaging, reviewer handoff, or approval.

## Follow the workflow

### 1. Confirm the platform lane

Verify the currently enabled problem domains and whether the lane is CPU, GPU, fine-tuning, or from-scratch. Browse current platform guidance when it may have changed. Do not relabel an unchanged task merely to fit an enabled domain; redesign the learning objective so the chosen domain is accurate.

For a GPU challenge, make GPU relevance intrinsic through a suitable modality, training workload, and model family. Reject a nominal GPU label when a rule system or small CPU model captures the intended signal.

### 2. Select a defensible source

Prefer a niche, real dataset with enough independent examples, useful signal, stable access, and a license permitting the intended commercial use and redistribution. Verify license and attribution at the original source; do not rely solely on a ModelScope, Kaggle, or Hugging Face re-upload label.

Record provenance and license in the dataset description and upload form. Do not reveal searchable source identifiers, original filenames, URLs, or catalog keys inside the challenge problem statement when they create lookup leakage. Attribution and blind-evaluation secrecy are different concerns.

### 3. Design the challenge before generating files

Write down:

1. the real-world decision or failure mode;
2. the independent statistical unit;
3. the input available at inference;
4. the exact target and canonical output;
5. the strongest expected shortcut;
6. why supervised learning should outperform rules;
7. the evaluation metric and its failure behavior; and
8. the expected compute lane.

Establish novelty through a materially different prediction unit, supervision signal, constraint, or evaluation regime. Do not attempt to raise novelty by branding or by merely claiming that a recombination is new. Name the nearest public tasks during internal research, then explain concrete differences naturally in the Overview without adding promotional novelty claims.

### 4. Build `prepare.py`

Make preparation deterministic, bounded in memory, and fast enough for the platform. Use opaque identifiers and remove source-derived lookup keys. Assign train/test and visibility at the independent-unit level before expanding an item into prediction rows or augmentations.

Target test size near 15–25% of train size and public visibility near 20–30% of independent test units unless the task justifies another ratio. Preserve class, site, language, modality, and difficulty balance at the unit level. Keep near duplicates and every derivative of one source unit on the same side.

Emit only documented public files. The private package should contain only data required by the grader, normally `answer.csv`. Do not ship unnecessary source annotations, manifests, mappings, or recoverable random seeds.

### 5. Build `grade.py`

Return one finite scalar with documented direction and theoretical bounds. Define every non-standard metric component and weight with a reproducible formula.

Require exactly the documented columns in the documented order and every expected identifier exactly once. Return the floor for missing, extra, duplicate, or reordered columns; missing, extra, or duplicate IDs; blanks; parse failures; non-finite values; invalid ranges; invalid probability rows; unknown tokens; or noncanonical output. Never repair malformed predictions with priors, means, clipping, renormalization, or silent coercion.

Keep private metadata out of the submission merge surface. Test perfect, baseline, shuffled, constant, malformed, missing-row, extra-row, duplicate-ID, extra-column, NaN, infinity, nonnumeric, negative, and zero-sum submissions as applicable.

### 6. Write the descriptions

Use the standard structure in [references/description-template.md](references/description-template.md). Keep the challenge statement self-contained and source-secret; put license and source attribution in the dataset record instead.

Blend the task's real technical distinction into the Overview. Do not add a separate marketing section solely to influence novelty scoring. Put `What Not to Use` last, tailor every bullet to an actual shortcut in this challenge, and avoid generic boilerplate that does not constrain a plausible exploit.

Do not wrap the entire description in an outer triple-backtick fence. Include one complete submission example with no ellipses.

### 7. Audit shortcuts and measurement integrity

Run cheap baselines before trained models: constants, class priors, row order, identifiers, filenames, dimensions, missingness, metadata, nearest-neighbor lookup, duplicate matching, cross-variant matching, source reconstruction, deterministic formulas, and rule systems. If a shortcut succeeds, remove the signal or redesign the task; do not conceal it with scoring weights.

Run `scripts/audit_grader.py` against the official grader. Run `scripts/check_stability.py` after creating an oracle and at least ten equal-quality noisy submissions. Treat a failed audit as a release blocker.

### 8. Measure model differentiation

Train at least one honest baseline using only allowed data. When agent evaluation is requested, run at least three independent solver attempts under the same data and compute rules. A target band such as 0.2–0.5 is a design requirement only when the user specifies it; achieve it through signal quality and task difficulty, never through leakage or arbitrary grader suppression.

Require meaningful variance. Flat results suggest a saturated shortcut, an impossible task, or deterministic solver behavior. One zero among otherwise similar scores usually indicates a failed run; rerun it instead of using the failure to lower the mean. Compare solver gaps with the private noise floor and require at least `2 × sd`, preferably `3 × sd`.

### 9. Package and report

Regenerate the artifact from a clean temporary output directory. Verify paths, sizes, schemas, counts, deterministic hashes, and that private-only files are absent from public output. Report train/test rows and units, public/private rows and units, class support, leakage checks, malformed-grader checks, oracle scores, stability statistics, baseline scores, runtime, peak memory, and final artifact path.

Do not declare the challenge complete while a release gate remains failed.

## Reusable scripts

### Stability audit

Create challenge-specific oracle and peer submissions, then run:

```bash
python scripts/check_stability.py \
  --answers private/answer.csv \
  --oracle audit/oracle.csv \
  --grade grade.py \
  --unit-col source_unit \
  --id-col id \
  --peer-submissions audit/noisy_*.csv \
  --solver-gap 0.03
```

### Grader audit

Run:

```bash
python scripts/audit_grader.py \
  --answers private/answer.csv \
  --oracle audit/oracle_submission.csv \
  --grade grade.py \
  --id-col id \
  --floor 0.0 \
  --perfect 1.0
```

Fix every case that does not return the documented floor or perfect score.
