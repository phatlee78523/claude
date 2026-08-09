# Description templates

Use normal Markdown without an outer code fence. Keep paragraphs naturally wrapped rather than inserting hard line breaks at a visual column width.

## Challenge description

Use this order:

1. `# <simple descriptive title>`
2. `## Overview`
3. `## Objective`
4. `## Dataset`
5. `## Files`
6. `## Input Fields` or modality-specific contents
7. `## Expected Output`
8. `## Evaluation`
9. `## Submission Format`
10. `## What Not to Use`

### Overview

Explain the real-world setting for a general audience, the inference input, the exact prediction unit, and why the output matters. Blend the material task distinction into the narrative using verifiable facts: what signal is withheld, what must be jointly inferred, what relations or constraints are new, and why nearby task formulations do not solve the same objective. Do not cite the hidden data source or use novelty-score language.

### Objective and expected output

Define every target token, label, coordinate system, relation, order rule, tie-breaker, valid range, sentinel, and case-sensitivity rule. If output is canonical, specify one unique serialization.

### Dataset and files

State row counts and independent-unit counts. Explain train/test size, public/private composition when appropriate, grouping, arrays, encodings, units, missing-value treatment, and every released file. Do not expose source lookup keys.

### Evaluation

For standard metrics, state the exact variant and averaging. For non-standard metrics, define every intermediate quantity and the complete final formula. Include weights, thresholds, tie behavior, invalid-submission behavior, direction, range, and perfect score. Avoid undefined phrases such as “diagnostic factor,” “hard-region skill,” or “progressively weighted.”

### Submission

List exact columns and order, required row/ID coverage, data types, value ranges, quoting rules, and one complete example row. Never use `...` in the example.

### What Not to Use

Put this section last. Write bullets for challenge-specific threats, such as source-record lookup, paired-view matching, external pretrained encoders, test-set pseudo-labeling, hand-written test annotations, private grader access, or forbidden APIs. State what is allowed when a restriction could be ambiguous.

## Dataset description

Use this order:

1. `## Overview`
2. `## Source and License`
3. `## File Structure`
4. `## Metadata Columns`
5. `## Array or Media Contents`
6. `## Preparation and Quality Filters`
7. `## Intended Uses and Limitations`

Dataset records should carry honest source attribution, original license, required acknowledgements, transformations, omitted identifiers, and whether the upload is an unsplit parent dataset or a challenge-ready package. Never claim commercial permission without verifying the original license terms.
