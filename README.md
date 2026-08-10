# claude

## build-ml-challenges

An agent skill for designing, implementing, hardening, and reviewing
competition-ready machine-learning challenges. It covers challenge ideation,
dataset sourcing and license verification, `prepare.py`/`grade.py`
construction, anti-cheat audits, public/private split stability, agent
baseline evaluation, and final packaging.

The skill entry point is [build-ml-challenges/SKILL.md](build-ml-challenges/SKILL.md).

### Layout

```
build-ml-challenges/
├── SKILL.md                          # Skill entry point and workflow
├── agents/
│   └── openai.yaml                   # Interface metadata (display name, default prompt)
├── references/
│   ├── anti-cheat.md                 # Anti-cheat and shortcut audit guidance
│   ├── description-template.md       # Challenge/dataset description templates
│   ├── release-gates.md              # Release-gate checklist
│   └── split-stability.md            # Split visibility and rank-stability gates
└── scripts/
    ├── audit_grader.py               # Audits strict submission validation in grade.py
    └── check_stability.py            # Audits visibility integrity and score stability
```

### Scripts

Both scripts require `numpy` and `pandas`, print a JSON report, and exit
non-zero on any audit failure.

```bash
python build-ml-challenges/scripts/audit_grader.py \
  --answers private/answer.csv --oracle audit/oracle_submission.csv \
  --grade grade.py --id-col id --floor 0.0 --perfect 1.0

python build-ml-challenges/scripts/check_stability.py \
  --answers private/answer.csv --oracle audit/oracle.csv \
  --grade grade.py --unit-col source_unit --id-col id \
  --peer-submissions audit/noisy_*.csv --solver-gap 0.03
```

### [`defect-localization/`](defect-localization/)

A complete challenge built with the skill from the VisA corpus (CC BY 4.0,
Amazon): given a photograph of a defective manufactured part, predict the
bounding box enclosing the defect. Mean-IoU metric, 1,195 independent units,
all automatable release gates passing. See
[release-report.md](defect-localization/release-report.md).
