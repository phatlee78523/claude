# Release report — Multi-Step Arithmetic Word Problems

Built with the `build-ml-challenges` skill on 2026-08-09. Source: GSM8K parquet uploads (`main` + `socratic` configs; socratic sub-question annotations released for train only, validated as consistent with `main` on both splits).

## Design summary

| Design element | Decision |
| --- | --- |
| Real-world objective | Final-answer computation for multi-step arithmetic word problems (tutoring/verification setting) |
| Independent unit | One word problem; 1 row = 1 unit everywhere |
| Inference input | `question` text only |
| Target | Canonical integer string (`^(0|-?[1-9][0-9]*)$`), exact match |
| Metric | Exact-match accuracy, range 0–1, perfect 1.0, floor 0.0 for any malformed submission |
| Strongest expected shortcut | Source lookup (parent corpus is public); mitigated by policy + opaque IDs, measured by retrieval baseline |
| Compute lane | CPU-feasible; GPU optional for seq2seq/transformer training from scratch |

## Data

| Quantity | Value |
| --- | --- |
| Train rows = units | 7,473 |
| Test rows = units | 1,319 (17.7% of train — within 15–25% gate) |
| Public / private test units | 330 (25.02%) / 989 |
| Duplicate questions / train∩test overlap | 0 / 0 |
| Data repair | 98 empty source `solution` fields (comma/negative answers) re-extracted from `####` lines; 5 negative answers retained |
| Socratic supervision | `socratic_solution` train column from the `socratic` config; cross-config check: identical questions and final answers |

## Gate results

| Gate | Result | Evidence |
| --- | --- | --- |
| Grader: oracle perfect | PASS (1.0) | `audit/grader_report.json` |
| Grader: 11 malformed cases → floor | PASS (all 0.0) | extra/reordered/missing columns, missing/extra/duplicate IDs, blank, whitespace, nonnumeric, NaN, infinity |
| Visibility integrity | PASS | 0 units cross visibility; public fraction 0.2502 ∈ [0.20, 0.30] |
| Oracle public/private gap | PASS | 1.0 vs 1.0, gap 0.0 |
| Rank stability (12 noisy peers @ 70% intended accuracy) | PASS | private sd = 0.00851, range = 0.0344; 2×sd = 0.0170, 3×sd = 0.0255; design solver gap 0.03 > 3×sd |
| Shortcut resistance | PASS | constant majority 2.65%, last-number 2.27%, first-number 1.82%, max-number 1.29%, TF-IDF 1-NN train lookup 1.14%; row-order and ID-hash Spearman ≈ 0 (`audit/baseline_report.json`) |
| Packaging | PASS | no answers in public files, ID sets consistent, hashes recorded (`audit/packaging_report.json`) |
| Preparation determinism/cost | PASS | fixed salt + seed 20250809; 0.9 s runtime, 172 MiB peak RSS; `test.csv`, `sample_submission.csv`, `answer.csv` byte-identical across reruns |
| License/provenance | PASS | GSM8K, MIT (verified from source card); attribution in dataset record; challenge statement source-secret |
| Honest learned baseline / agent evaluation | NOT RUN | Requires from-scratch model training and solver harness beyond this session; flagged as the remaining open gate |

## Known limitations

- The parent corpus is public and widely mirrored; blind evaluation relies on the What-Not-to-Use policy (no lookup, no pretrained models). This is inherent to any public-source repackage and is disclosed in the dataset record.
- The `solution` and `socratic_solution` columns keep calculator annotations (`<<expr=result>>`) as an intentional supervision aid.
- Agent-evaluation and trained-baseline gates remain to be run on a platform with training compute; all automatable gates pass.

## Artifacts

| File | SHA-256 (16) | Bytes |
| --- | --- | --- |
| `public/train.csv` | f93c5561e37e4213 | 7,473,764 |
| `public/test.csv` | ab28fe88142b4676 | 337,003 |
| `public/sample_submission.csv` | 2d312cb4f8e7a3d3 | 19,795 |
| `private/answer.csv` | 38c070ec14bddd4b | 48,876 |
