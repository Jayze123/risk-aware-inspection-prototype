# Integrated PaDiM Capsule Result

## Purpose

This experiment tested PaDiM on the MVTec AD capsule category and passed the exported Anomalib predictions through the risk-aware inspection pipeline. The purpose was to compare PaDiM with PatchCore on a third category beyond bottle and hazelnut.

## Dataset

- Dataset: MVTec AD
- Category: capsule

## Result

| Metric | Value |
|---|---:|
| TP | 108 |
| TN | 11 |
| FP | 12 |
| FN | 1 |
| Accuracy | 0.9015 |
| Precision | 0.9000 |
| Recall | 0.9908 |
| F1-score | 0.9432 |
| Human review rate | 0.8712 |

## Interpretation

PaDiM achieved very high recall on the capsule category, detecting 108 defective samples with only one false negative. However, it also produced 12 false positives, which reduced precision and increased the human-review rate.

Compared with PatchCore, PaDiM was more sensitive but less selective. PatchCore produced fewer false positives and achieved a higher F1-score, while PaDiM prioritised recall at the cost of review workload. This supports the dissertation argument that model evaluation should consider both detection performance and downstream decision-support burden.
