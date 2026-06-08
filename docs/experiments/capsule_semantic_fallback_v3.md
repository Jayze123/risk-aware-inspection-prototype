# Capsule Semantic Fallback v3

## Purpose

This experiment refined the semantic interpretation layer for the MVTec AD capsule category. Earlier capsule runs showed strong anomaly detection performance, but high human-review rates because many detected anomalies were labelled as unknown.

The update added:
- crack as an explicit allowed semantic label
- surface_defect as a cautious fallback label for high-confidence, moderate-area anomaly regions
- risk mappings for the new labels

## PatchCore capsule result

| Metric | Before semantic v3 | After semantic v3 |
|---|---:|---:|
| Accuracy | 0.9697 | 0.9697 |
| Precision | 0.9907 | 0.9907 |
| Recall | 0.9725 | 0.9725 |
| F1-score | 0.9815 | 0.9815 |
| Human review rate | 0.6818 | 0.5152 |

The PatchCore detection metrics remained unchanged, while the review rate reduced from 0.6818 to 0.5152.

## PaDiM capsule result

| Metric | Before semantic v3 | After semantic v3 |
|---|---:|---:|
| Accuracy | 0.9015 | 0.9015 |
| Precision | 0.9000 | 0.9000 |
| Recall | 0.9908 | 0.9908 |
| F1-score | 0.9432 | 0.9432 |
| Human review rate | 0.8712 | 0.8409 |

The PaDiM review rate reduced slightly, but many cases still remained unknown.

## Interpretation

The semantic fallback improved the risk-aware pipeline without retraining the anomaly detectors. This supports the dissertation argument that downstream governance logic can affect operational review workload independently of detection accuracy.

The improvement was strongest for PatchCore, where surface_defect reduced unnecessary unknown labels and lowered the human-review rate. PaDiM still produced many unknown labels, suggesting that its anomaly maps may be less suitable for the current rule-based semantic layer on capsule.
