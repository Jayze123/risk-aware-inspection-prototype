# Integrated Model Comparison: Bottle, Hazelnut and Capsule

## Bottle results

| Detector | Accuracy | Precision | Recall | F1-score | Human review rate |
|---|---:|---:|---:|---:|---:|
| Statistical original | 0.5904 | 1.0000 | 0.4603 | 0.6304 | 0.5181 |
| Statistical tuned 0.7 | 0.8795 | 0.8955 | 0.9524 | 0.9231 | 0.7711 |
| PatchCore integrated | 0.9880 | 1.0000 | 0.9841 | 0.9920 | 0.1928 |
| PaDiM integrated | 0.9518 | 0.9538 | 0.9841 | 0.9688 | 0.6867 |

## Hazelnut results

| Detector | Accuracy | Precision | Recall | F1-score | Human review rate |
|---|---:|---:|---:|---:|---:|
| Statistical original | 0.4364 | 0.8333 | 0.1429 | 0.2439 | 0.2273 |
| Statistical tuned 0.7 | 0.5545 | 0.6567 | 0.6286 | 0.6423 | 0.7636 |
| PatchCore integrated | 0.9909 | 1.0000 | 0.9857 | 0.9928 | 0.1727 |
| PaDiM integrated | 0.7182 | 0.6970 | 0.9857 | 0.8166 | 0.9000 |

## Capsule results

| Detector | Accuracy | Precision | Recall | F1-score | Human review rate |
|---|---:|---:|---:|---:|---:|
| PatchCore integrated | 0.9697 | 0.9907 | 0.9725 | 0.9815 | 0.6818 |
| PaDiM integrated | 0.9015 | 0.9000 | 0.9908 | 0.9432 | 0.8712 |

## Interpretation

Across the tested categories, PatchCore is currently the strongest detector for the risk-aware inspection pipeline. It achieves high accuracy, strong precision, high recall and consistently strong F1-scores. PaDiM also performs well in some cases, especially in recall, but it produces more false positives on hazelnut and capsule, which increases the human-review rate.

The results show that anomaly detection performance and review workload should be evaluated together. A model with high recall may still be less practical if it causes many normal products to be escalated for review. This supports the dissertation aim of combining anomaly detection with risk-aware governance, confidence fusion and human-review gating rather than reporting detection accuracy alone.
