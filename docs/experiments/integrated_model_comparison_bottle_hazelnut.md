# Integrated Model Comparison: Bottle and Hazelnut

## Summary

This document summarises the current integrated results for the risk-aware inspection pipeline using the MVTec AD bottle and hazelnut categories.

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

## Interpretation

The results show that the original statistical detector is useful as a transparent baseline for validating the end-to-end risk-aware pipeline, but it is not robust enough across different MVTec categories. Threshold tuning improved the statistical detector, particularly for bottle, but it also increased the human-review rate.

PatchCore produced the strongest overall performance across both tested categories. It achieved high accuracy, high recall, no false positives, and low human-review rates. This makes it the most promising detector for the current dissertation prototype.

PaDiM performed strongly on bottle, but less effectively on hazelnut. Although it maintained high recall on hazelnut, it produced many false positives and a high human-review rate. This shows that strong anomaly recall alone is not sufficient for a practical risk-aware inspection system; review workload and false-positive behaviour must also be considered.

Overall, the experiments support the proposed architecture: stronger anomaly detectors such as PatchCore and PaDiM can be connected to the same downstream risk-aware governance pipeline, while deterministic risk lookup, confidence fusion and human-review gating remain independent of the detector choice.
