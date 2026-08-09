# Split visibility and rank stability

Treat split integrity and ranking stability as mandatory release gates.

## Independent unit

Keep all predictions from one independent item together:

| Task | Unit |
| --- | --- |
| Object detection or segmentation | Image and all boxes or masks |
| Multi-label document task | Document |
| Token or span labeling | Sentence or document |
| Time series | Entire series or independent segment |
| Grouped records | Patient, session, protein domain, site, or analogous group |

Assign train/test and `visibility` by unit before expanding into rows, crops, windows, targets, or variants. Keep exact and near duplicates together.

## Split targets

- Keep test near 15–25% of train unless justified.
- Assign approximately 20–30% of independent test units to public and the rest to private.
- Stratify at the unit level for class, modality, site, language, and difficulty.
- Report row counts and independent-unit counts.
- For macro or mAP metrics, count private support per class; tiny classes can dominate score noise.

## Visibility-bias gate

Assert that every independent unit has one visibility. Score an exact oracle separately on public and private answer subsets. Both must reach the documented perfect score and their gap must stay within numerical tolerance.

Also compare a controlled non-perfect diagnostic submission across public and private when the two sides might differ in difficulty. A correct nominal ratio does not guarantee that both sides measure the same task.

## Rank-stability gate

Create at least ten submissions of equal intended quality by perturbing an oracle at the independent-unit level with one fixed noise magnitude and different seeds. Score them on the complete private set:

```python
sd = np.std(private_scores, ddof=1)
score_range = max(private_scores) - min(private_scores)
```

Require meaningful adjacent solver gaps to exceed `2 × sd`; prefer `3 × sd`. Do not generate noise by independently dropping rows from a multi-row unit.

If variance is excessive, reduce metric sensitivity before collecting more data: relax overly strict overlap thresholds for small objects, remove redundant extreme thresholds, aggregate within units, avoid unstable macro weighting of tiny classes, or increase private support. Reduce measurement noise without leaking train-like copies into test.

Use `scripts/check_stability.py` to automate the audit and retain its JSON report with the challenge release evidence.
