# Bottle Model Comparison Summary

| Detector | Setting | Accuracy | Precision | Recall | F1-score | Image AUROC | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| Simple statistical | Original threshold | 0.5904 | 1.0000 | 0.4603 | 0.6304 | N/A | Conservative baseline with many missed defects |
| Simple statistical | Threshold multiplier 0.7 | 0.8795 | 0.8955 | 0.9524 | 0.9231 | N/A | Threshold override improved recall and F1-score |
| PatchCore | Anomalib Folder | N/A | N/A | N/A | 0.9920 | 1.0000 | Strongest result in the current bottle experiment |
| PaDiM | Anomalib Folder | N/A | N/A | N/A | 0.9688 | 0.9937 | Strong result, but slightly below PatchCore on bottle |

## Interpretation

The bottle experiments show that the simple statistical detector is useful for validating the risk-aware pipeline, but stronger feature-based anomaly detection models provide substantially better image-level performance. Threshold tuning improved the statistical baseline, but PatchCore and PaDiM achieved higher anomaly detection performance without relying on the simple handcrafted image-difference approach. These results support the dissertation plan to use PatchCore and PaDiM as the main anomaly detection methods before linking detector outputs to localisation, semantic labelling, deterministic risk lookup and human-review gating.
