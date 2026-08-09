# Source evaluation — GSM8K

Evaluated 2026-08-09 against primary sources, per the `build-ml-challenges`
source-selection and license/provenance gates.

## Identity

- **Dataset:** GSM8K (Grade School Math 8K), 8,792 grade-school math word
  problems (7,473 train / 1,319 test) with crowdsourced worked solutions,
  2–8 reasoning steps each; `main` and `socratic` configurations.
- **Publisher:** OpenAI. **Paper:** Cobbe et al., *Training Verifiers to Solve
  Math Word Problems*, arXiv:2110.14168 (2021).
- **Primary repository:** https://github.com/openai/grade-school-math

## Provenance verification

The four parquet files in `source-data/` were compared row-by-row against the
official JSONL files fetched from the primary GitHub repository
(`grade_school_math/data/{train,test,train_socratic,test_socratic}.jsonl`):

| Config/split | Rows (parquet/official) | `question` identical | `answer` identical |
| --- | --- | --- | --- |
| main/train | 7,473 / 7,473 | yes | yes |
| main/test | 1,319 / 1,319 | yes | yes |
| socratic/train | 7,473 / 7,473 | yes | yes |
| socratic/test | 1,319 / 1,319 | yes | yes |

Verdict: the packaged source data is **byte-identical in content and order**
to the official release. The parquet re-upload adds one derived column
(`solution`, the extracted final answer) that is not part of the official
data; its extraction is broken for 98 rows (comma-formatted and negative
answers), which is why `prepare.py` re-extracts final answers from the
authoritative `####` lines instead.

## License

- **License:** MIT, verified from the primary `LICENSE` file in the OpenAI
  repository — "Copyright (c) 2021 OpenAI"; grants rights to "use, copy,
  modify, merge, publish, distribute, sublicense, and/or sell", conditioned on
  retaining the copyright and permission notice.
- **Commercial use:** permitted. **Redistribution:** permitted (this
  repository redistributes the data with attribution and license reference in
  `dataset-description.md`).
- **Attribution:** cite `@article{cobbe2021gsm8k}` (BibTeX provided in the
  primary repository README) — already included in the dataset record.

## Access stability

Primary GitHub repository has been stable since 2021 and requires no
authentication; widely mirrored (e.g., the `openai/gsm8k` dataset hub entry
from which the parquet files derive). Redistribution inside this repository
removes any remaining availability risk for the challenge package.

## Signal quality

- Collection: freelance writers (Upwork) scaled through Surge AI; every
  problem independently re-solved by a different worker, disagreements
  repaired or discarded; the paper estimates **~1.7% residual error rate**.
- Independent checks on this package: all 23,716 calculator annotations in
  the training solutions evaluate correctly (0 arithmetic errors, 0 parse
  failures); no duplicate questions; no train↔test overlap; no near-duplicate
  pairs (max TF-IDF cosine between any test and train question: 0.803);
  train/test distributions match (question length, answer range).
- Volume: 8,792 independent units — above the ≥1,000-unit gate for standard
  supervised tasks, adequate for from-scratch sequence models of modest size.

## Risks and limitations

1. **Benchmark contamination (highest risk).** GSM8K is one of the most
   widely used LLM benchmarks and is present in the training data of
   essentially all modern pretrained models. Any evaluation that permits
   pretrained models or internet access measures contamination, not
   reasoning. The challenge therefore restricts participants to models
   trained from scratch on the released files — this restriction is
   load-bearing, not cosmetic.
2. **Public answer lookup.** Questions and answers are fully public;
   blind evaluation relies on the challenge's What-Not-to-Use policy.
   Technical mitigations (opaque IDs, shuffled row order) raise effort but
   cannot prevent deliberate lookup.
3. **Derived-column defect in the re-upload.** The `solution` column is
   empty for 98 rows (see Provenance) — handled in `prepare.py`; do not
   consume that column directly from the parquets.
4. **Scope.** English-only, elementary arithmetic; conclusions do not
   transfer to symbolic algebra, multilingual, or open-domain reasoning.

## Verdict

License and provenance gates **pass** (MIT verified at the primary source;
content verified identical to the official release; attribution recorded).
The source is suitable for this challenge as a reference build. The known
public availability of answers and universal LLM contamination make it
unsuitable for a live blind competition against unrestricted solvers, as
already disclosed in the dataset record and release report.
