# Capsule Localisation Threshold Sweep

## Purpose

This experiment tested whether capsule localisation quality could be improved by tuning the anomaly-map threshold used to convert predicted heatmaps into binary masks. The evaluation used MVTec AD capsule ground-truth masks and measured localisation quality using Intersection-over-Union (IoU) and Dice coefficient.

## PatchCore capsule

| Setting                | Threshold | Mean IoU | Mean Dice | Median IoU | Median Dice |
| ---------------------- | --------: | -------: | --------: | ---------: | ----------: |
| Original pipeline mask |   default |   0.1068 |    0.1671 |     0.0450 |      0.0862 |
| Best tuned threshold   |      0.85 |   0.2979 |    0.4311 |     0.2732 |      0.4291 |

PatchCore showed a large improvement after threshold tuning. This suggests that the anomaly maps contained useful localisation information, but the original mask conversion was not optimal for capsule defects.

## PaDiM capsule

| Setting                  | Threshold | Mean IoU | Mean Dice | Median IoU | Median Dice |
| ------------------------ | --------: | -------: | --------: | ---------: | ----------: |
| Original pipeline mask   |   default |   0.1731 |    0.2673 |     0.1365 |      0.2403 |
| Best mean IoU threshold  |      0.55 |   0.1830 |    0.2749 |     0.1464 |      0.2554 |
| Best mean Dice threshold |      0.50 |   0.1818 |    0.2751 |     0.1430 |      0.2503 |

PaDiM only improved slightly after threshold tuning. This suggests that PaDiM’s default mask conversion was already closer to its best thresholded performance for capsule.

## Interpretation

The threshold sweep shows that localisation performance depends strongly on the post-processing stage. Before threshold tuning, PaDiM produced better capsule localisation than PatchCore. After tuning, PatchCore produced the stronger capsule localisation result, with mean IoU increasing from 0.1068 to 0.2979 and mean Dice increasing from 0.1671 to 0.4311.

This supports the dissertation argument that anomaly detection performance, localisation quality and operational review behaviour should be evaluated separately. It also shows that localisation can be improved through post-processing without retraining the anomaly detector.
