# Integrated PatchCore Capsule Result

## Purpose

This experiment tested the full Anomalib PatchCore and risk-aware pipeline workflow on the MVTec AD capsule category. The purpose was to check whether the full experiment runner works on a third category beyond bottle and hazelnut.

## Dataset

- Dataset: MVTec AD
- Category: capsule

## Result

| Metric | Value |
|---|---:|
| TP | 106 |
| TN | 22 |
| FP | 1 |
| FN | 3 |
| Accuracy | 0.9697 |
| Precision | 0.9907 |
| Recall | 0.9725 |
| F1-score | 0.9815 |
| Human review rate | 0.6818 |

## Interpretation

PatchCore achieved strong integrated performance on the capsule category, with high accuracy, precision, recall and F1-score. The model produced only one false positive and three false negatives, which indicates strong anomaly detection performance.

However, the human-review rate was 0.6818, which is much higher than the PatchCore review rates observed for bottle and hazelnut. This suggests that although PatchCore detected capsule anomalies well, the downstream confidence and risk-governance logic treated many cases as requiring review. This is useful for the dissertation because it shows that detection accuracy and review workload should be analysed separately.
