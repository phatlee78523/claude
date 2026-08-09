# Dataset record — Multi-Step Arithmetic Word Problems package

## Overview

Challenge-ready repackage of GSM8K (Grade School Math 8K), a corpus of 8,792 linguistically diverse grade-school math word problems with crowdsourced worked solutions. Both source configurations are merged: `main` provides the plain worked solutions and `socratic` provides the same solutions with Socratic sub-question annotations (train only). This upload is a split, canonicalized package for blind evaluation, not the unsplit parent dataset: training rows carry full supervision, test answers are withheld in a private grading file.

## Source and License

- Source: GSM8K, published by OpenAI. Homepage: https://openai.com/blog/grade-school-math/ — repository: https://github.com/openai/grade-school-math — paper: Cobbe et al., *Training Verifiers to Solve Math Word Problems*, arXiv:2110.14168.
- License: MIT. Commercial use and redistribution are permitted with retention of the license notice.
- Attribution: please cite Cobbe et al. (2021) (`@article{cobbe2021gsm8k}`) when using this package.
- Annotations were produced by crowd workers via Surge AI, per the source paper's Appendix A.

## File Structure

- `public/train.csv` — 7,473 rows: `id`, `question`, `solution`, `socratic_solution`, `final_answer`.
- `public/test.csv` — 1,319 rows: `id`, `question`.
- `public/sample_submission.csv` — 1,319 rows: `id`, `answer` (placeholder `0`).
- `private/answer.csv` — 1,319 rows: `id`, `answer`, `visibility` (`public`/`private`), `unit_id`. Grading only; never distributed.

## Metadata Columns

- `id` / `unit_id` — deterministic opaque identifier: first 12 hex digits of SHA-256 over a fixed salt and the question text. Original corpus order, split names, and indices are not recoverable from the released files; rows are sorted by `id`.
- `visibility` — public/private leaderboard membership, assigned per problem with a fixed-seed permutation (330 public, 989 private).

## Array or Media Contents

Text only; no arrays, images, or media. `solution` strings contain calculator annotations `<<expr=value>>` and a final line `#### <answer>`. `socratic_solution` strings additionally prefix every reasoning line with the sub-question it answers, separated by ` ** `.

## Preparation and Quality Filters

- The source distribution's extracted final-answer field was empty for 98 problems (82 train, 16 test) — exactly those whose `####` value contains a thousands separator or a minus sign. This package re-extracts every final answer directly from the `####` line of the worked solution.
- Final answers are canonicalized to integer strings: thousands separators, currency symbols, and spaces removed; validated against `^(0|-?[1-9][0-9]*)$`. All 8,792 answers pass; 5 are negative.
- No rows were dropped or edited otherwise. Train and test contain no duplicate questions and do not overlap.
- The `socratic` configuration was validated against `main` before merging: identical question sets and identical canonical final answers on both splits. Socratic annotations are released for training rows only; the socratic test file is used solely for this consistency check and nothing from it is published.
- Preparation (`prepare.py`) is deterministic (fixed hash salt and split seed 20250809), runs in under 1 second, and peaks below 200 MiB.

## Intended Uses and Limitations

Intended for closed-book evaluation of multi-step arithmetic reasoning under a no-external-data policy: models are trained from scratch on the released training file. Because the parent corpus is public and widely mirrored, blind evaluation is only meaningful under the challenge's lookup and pretrained-model restrictions; scores obtained with internet access or LLMs pretrained on the parent corpus measure contamination, not reasoning. The corpus is English-only, grade-school arithmetic, with an estimated ~1.7% residual annotation error rate per the source paper.
