# claude

Toolkit and worked example for building competition-ready ML challenges.

## Contents

### [`build-ml-challenges/`](build-ml-challenges/)

An agent skill for designing, implementing, hardening, and reviewing
machine-learning challenges. Entry point: [SKILL.md](build-ml-challenges/SKILL.md).
Includes reference guides (anti-cheat, description templates, release gates,
split stability) and two audit scripts (`audit_grader.py`, `check_stability.py`,
requiring `numpy` + `pandas`).

### [`arithmetic-word-problems/`](arithmetic-word-problems/)

A complete challenge built with that skill from the GSM8K corpus (MIT license,
Cobbe et al. 2021): predict the final integer answer of a multi-step arithmetic
word problem from its text alone.

- `source-data/` — original GSM8K parquet files (`main` and `socratic` configs)
  plus the upstream dataset card and metadata.
- `prepare.py` — deterministic packaging from the source parquet files,
  opaque IDs, unit-level public/private split.
- `grade.py` — exact-match accuracy with strict validation (floor 0.0 for any
  malformed submission).
- `description.md` / `dataset-description.md` — challenge statement and dataset
  record.
- `public/` — train (7,473 rows), test (1,319 rows), sample submission.
- `private/answer.csv` — held-out answers with visibility split. **Note: this
  repository is public, so test answers are visible here; treat the challenge
  as a reference build, not a live blind competition.**
- `audit/` — grader audit, stability audit, shortcut baselines, and packaging
  reports; see [release-report.md](arithmetic-word-problems/release-report.md)
  for the full gate summary.

To regenerate the challenge package from the source data:

```bash
cd arithmetic-word-problems
python prepare.py \
  --train-parquet source-data/main/train-00000-of-00001.parquet \
  --test-parquet source-data/main/test-00000-of-00001.parquet \
  --socratic-train-parquet source-data/socratic/train-00000-of-00001.parquet \
  --socratic-test-parquet source-data/socratic/test-00000-of-00001.parquet \
  --output-dir .
```
