# Integrated PaDiM Hazelnut Result

## Purpose

This experiment tested PaDiM on the MVTec AD hazelnut category and passed the exported Anomalib predictions through the risk-aware inspection pipeline. The purpose was to compare PaDiM with the statistical baseline and the integrated PatchCore result on the same category.

## Dataset

- Dataset: MVTec AD
- Category: hazelnut
- Test images: 110

## Result

| Metric | Value |
|---|---:|
| TP | 69 |
| TN | 10 |
| FP | 30 |
| FN | 1 |
| Accuracy | 0.7182 |
| Precision | 0.6970 |
| Recall | 0.9857 |
| F1-score | 0.8166 |
| Human review rate | 0.9000 |

## Interpretation

PaDiM achieved high recall on the hazelnut category, detecting 69 out of 70 defective samples. However, it also produced 30 false positives, which reduced precision and increased the human-review rate to 0.9000. This shows that PaDiM was sensitive to normal hazelnut variation in this experiment.

Compared with PatchCore, PaDiM was less suitable for hazelnut under the current configuration. PatchCore achieved the same number of true positives with no false positives and a much lower human-review rate. This result is important for the dissertation because it demonstrates that the detector choice has a major effect not only on anomaly classification performance, but also on downstream review workload and risk-aware decision support.
