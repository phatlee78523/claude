# Multi-Step Arithmetic Word Problems

## Overview

Automated tutoring and homework-assistance systems must do more than recognize which formula a textbook exercise is asking for: they have to read a short everyday scenario, identify the quantities and relations it describes, plan a sequence of elementary calculations, and commit to one final number. This challenge evaluates exactly that capability. Each prediction unit is a single self-contained word problem written in natural English, and the system receives only the problem text at inference time. The worked reasoning and the final result for every test problem are withheld, so the answer must be computed by carrying out the described multi-step arithmetic, not retrieved or pattern-matched. Unlike equation-extraction or span-selection tasks, no intermediate annotation is given at test time, and unlike retrieval-style QA, no test problem appears in the training material — solving requires jointly inferring the computation plan and executing it correctly to the last step.

## Objective

Given the text of a word problem, predict its final numeric answer. Every answer is a single base-10 integer. The prediction must be exact: a submission earns credit on a problem only when the submitted integer equals the reference integer.

## Dataset

- Training set: 7,473 word problems. Each problem is one independent unit and appears exactly once.
- Test set: 1,319 word problems, disjoint from training. Approximately 25% of test units are assigned to the public leaderboard and 75% to the private leaderboard; membership is assigned per problem and never revealed.
- Each training problem includes its full worked solution in two forms. Both use calculator annotations of the form `<<48/2=24>>` marking each elementary computation and end in a line of the form `#### <final answer>`. The second form additionally prefixes each reasoning step with the sub-question that the step answers, separated by ` ** `.
- Missing values do not occur in any released file.

## Files

- `train.csv` — 7,473 rows, columns `id`, `question`, `solution`, `socratic_solution`, `final_answer`.
- `test.csv` — 1,319 rows, columns `id`, `question`.
- `sample_submission.csv` — 1,319 rows, columns `id`, `answer`, with a placeholder value in `answer`.

## Input Fields

- `id` — opaque 12-character hexadecimal identifier of the problem.
- `question` — the word problem text (English, plain text).
- `solution` (train only) — the worked solution: several lines of natural-language reasoning with calculator annotations, ending in a line `#### <final answer>`.
- `socratic_solution` (train only) — the same worked solution with each reasoning line prefixed by the sub-question it answers, in the form `<sub-question> ** <reasoning line>`; final line identical to `solution`'s.
- `final_answer` (train only) — the canonical final answer of the problem as a string, identical to the value on the solution's `####` line after canonicalization.

## Expected Output

For every `id` in `test.csv`, output one canonical integer string:

- base-10 digits only, with an optional single leading `-` for negative values;
- no thousands separators, decimal points, currency symbols, units, spaces, or leading zeros;
- `0` is written exactly as `0` (never `-0`, `00`, or `0.0`).

## Evaluation

The metric is exact-match accuracy. Let N be the number of test problems and C the number of submitted answers that are string-equal to the reference canonical integer for the same `id`. The score is C / N, ranging from 0.0 to 1.0; higher is better and a perfect submission scores 1.0. The public leaderboard scores the public subset; the final ranking uses the private subset only.

A submission that violates any structural or format rule receives the floor score 0.0 for the whole submission, with no repair or partial credit: wrong column names or order, extra or missing columns, extra, missing, or duplicated `id` values, empty or whitespace values, non-numeric values, non-finite values, non-canonical integer serializations (leading zeros, `+` signs, decimals, separators), or any unparsable content.

## Submission Format

Submit a CSV file with header `id,answer`, in that column order, containing exactly one row for every `id` in `test.csv` (1,319 rows, each `id` exactly once). The `answer` column holds the canonical integer string. Example of the header and one complete row:

```
id,answer
0021dd37ed4e,42
```

## What Not to Use

- The test problems derive from a corpus that is publicly available in several redistributions. Do not look up test questions in any external dataset, benchmark suite, search engine, mirror, or model-training corpus, and do not use any material obtained that way to annotate or verify test answers.
- Do not use pretrained models of any kind, including language-model APIs, published checkpoints, or embeddings trained on external text. Train only on the files released with this challenge. Tokenizers, vocabularies, and features built from the released text, and standard open-source ML libraries, are allowed.
- Do not solve or annotate test problems by hand, and do not crowdsource them.
- Do not probe the public leaderboard to recover test answers; submission-count limits apply.
