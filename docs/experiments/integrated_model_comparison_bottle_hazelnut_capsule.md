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
| PatchCore + semantic fallback v3 | 0.9697 | 0.9907 | 0.9725 | 0.9815 | 0.5152 |
| PaDiM integrated | 0.9015 | 0.9000 | 0.9908 | 0.9432 | 0.8712 |
| PaDiM + semantic fallback v3 | 0.9015 | 0.9000 | 0.9908 | 0.9432 | 0.8409 |

## Interpretation

Across the tested categories, PatchCore currently provides the strongest overall performance for the risk-aware inspection pipeline. It achieves high accuracy, strong precision, high recall and consistently strong F1-scores across bottle, hazelnut and capsule.

PaDiM also achieves high recall, but it produces more false positives on hazelnut and capsule. This increases the human-review rate, which makes it less operationally efficient under the current configuration.

The capsule semantic fallback v3 experiment shows that review workload can be reduced without retraining the anomaly detector. PatchCore capsule kept the same F1-score of 0.9815, while its review rate reduced from 0.6818 to 0.5152. This supports the dissertation argument that downstream semantic interpretation and governance rules affect operational decision support independently of detection accuracy.
