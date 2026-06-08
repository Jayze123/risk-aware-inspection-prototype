# Integrated PatchCore Hazelnut Result

## Purpose

This experiment tested whether the integrated Anomalib PatchCore and risk-aware pipeline workflow generalises beyond the MVTec AD bottle category. Hazelnut was selected because the earlier simple statistical detector performed poorly on this category, especially in terms of recall.

## Dataset

- Dataset: MVTec AD
- Category: hazelnut
- Test images: 110

## Result

PatchCore was trained using Anomalib and the Folder datamodule. Its exported predictions were then passed through the risk-aware inspection pipeline.

| Metric | Value |
|---|---:|
| TP | 69 |
| TN | 40 |
| FP | 0 |
| FN | 1 |
| Accuracy | 0.9909 |
| Precision | 1.0000 |
| Recall | 0.9857 |
| F1-score | 0.9928 |
| Human review rate | 0.1727 |

## Interpretation

The integrated PatchCore result on hazelnut is substantially stronger than the simple statistical detector. The tuned statistical baseline achieved an F1-score of 0.6423, while the integrated PatchCore workflow achieved an F1-score of 0.9928. This suggests that the earlier hazelnut weakness was mainly caused by the limitations of the simple detector rather than the downstream risk-aware governance pipeline.

The result also shows that PatchCore can maintain strong detection performance while reducing the human-review rate. This is important for the dissertation because it supports the use of feature-based anomaly detection models as the main anomaly detection stage before localisation, semantic interpretation, deterministic risk lookup and human-review gating.
