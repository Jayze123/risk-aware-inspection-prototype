# Integrated Anomalib Risk-Aware Pipeline Results

## Purpose

This experiment connected exported Anomalib PatchCore and PaDiM predictions to the risk-aware inspection pipeline. The aim was to confirm that deep anomaly detector outputs could be passed through the downstream stages of localisation, constrained semantic labelling, deterministic risk lookup, confidence fusion, human-review gating and audit-ready output logging.

## Dataset

- Dataset: MVTec AD
- Category: bottle
- Test images: 83

## Integrated Results

| Detector | TP | TN | FP | FN | Accuracy | Precision | Recall | F1-score | Human review rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Simple statistical, original | 29 | 20 | 0 | 34 | 0.5904 | 1.0000 | 0.4603 | 0.6304 | 0.5181 |
| Simple statistical, tuned 0.7 | 60 | 13 | 7 | 3 | 0.8795 | 0.8955 | 0.9524 | 0.9231 | 0.7711 |
| PatchCore integrated | 62 | 20 | 0 | 1 | 0.9880 | 1.0000 | 0.9841 | 0.9920 | 0.1928 |
| PaDiM integrated | 62 | 17 | 3 | 1 | 0.9518 | 0.9538 | 0.9841 | 0.9688 | 0.6867 |

## Interpretation

The integrated results show that the risk-aware pipeline can accept anomaly detector outputs from Anomalib models and still produce structured audit records. PatchCore achieved the strongest integrated result, with accuracy of 0.9880, F1-score of 0.9920 and no false positives. PaDiM also performed strongly, with F1-score of 0.9688, although it produced three false positives and a higher human-review rate.

Compared with the simple statistical detector, both PatchCore and PaDiM substantially improved defect detection performance. This confirms that the initial statistical detector is useful as a transparent MVP baseline, but stronger feature-based anomaly detection models are more suitable for the main dissertation experiments.

The results also show that human-review rate is influenced not only by detection accuracy, but also by confidence and downstream risk-governance logic. PatchCore produced the best balance between detection performance and review workload in this bottle experiment.
