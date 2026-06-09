# Localisation Threshold Sweep Across Categories

## Purpose

This experiment tested whether localisation performance could be improved by tuning the anomaly-map threshold used to convert PatchCore and PaDiM heatmaps into binary masks. The evaluation used MVTec AD ground-truth masks and measured localisation quality using Intersection-over-Union (IoU) and Dice coefficient.

## Best threshold results

| Category | Model | Best threshold | Mean IoU | Mean Dice | Median IoU | Median Dice |
|---|---|---:|---:|---:|---:|---:|
| bottle | PatchCore | 0.70 | 0.5929 | 0.7322 | 0.5916 | 0.7434 |
| bottle | PaDiM | 0.35 | 0.5110 | 0.6612 | 0.4990 | 0.6658 |
| hazelnut | PatchCore | 0.80 | 0.4331 | 0.5854 | 0.4232 | 0.5947 |
| hazelnut | PaDiM | 0.50 | 0.3340 | 0.4693 | 0.3225 | 0.4877 |
| capsule | PatchCore | 0.85 | 0.2979 | 0.4311 | 0.2732 | 0.4291 |
| capsule | PaDiM | 0.55 | 0.1830 | 0.2749 | 0.1464 | 0.2554 |

## Interpretation

The threshold sweep shows that localisation performance is strongly affected by the post-processing threshold used to convert anomaly maps into binary masks. PatchCore benefited most from threshold tuning and achieved the strongest tuned localisation performance across bottle, hazelnut and capsule.

Before threshold tuning, PaDiM produced stronger default localisation masks in several categories. However, after threshold optimisation, PatchCore became the stronger localisation model across the tested categories. This suggests that PatchCore’s anomaly maps contained useful localisation information, but the original binary mask conversion was not optimal.

The results also show that localisation quality varies by category. Bottle achieved the strongest localisation scores, followed by hazelnut and capsule. Capsule remained the most difficult category, mainly because many capsule defects are small, thin or visually subtle.

Overall, this experiment supports the dissertation argument that anomaly detection, localisation and operational review behaviour should be evaluated separately. It also shows that localisation can be improved through post-processing without retraining the anomaly detector.