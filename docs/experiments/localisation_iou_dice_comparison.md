# Localisation IoU and Dice Comparison

## Purpose

This experiment evaluates the localisation quality of PatchCore and PaDiM outputs after integration with the risk-aware inspection pipeline. Localisation quality is measured using Intersection-over-Union (IoU) and Dice coefficient against MVTec AD ground-truth defect masks.

## Summary results

| Category | Model | Mean IoU | Mean Dice | Median IoU | Median Dice |
|---|---|---:|---:|---:|---:|
| bottle | PatchCore | 0.3472 | 0.4928 | 0.3480 | 0.5164 |
| bottle | PaDiM | 0.4968 | 0.6442 | 0.4930 | 0.6604 |
| hazelnut | PatchCore | 0.1456 | 0.2316 | 0.1070 | 0.1933 |
| hazelnut | PaDiM | 0.3084 | 0.4444 | 0.3168 | 0.4811 |
| capsule | PatchCore | 0.1068 | 0.1671 | 0.0450 | 0.0862 |
| capsule | PaDiM | 0.1731 | 0.2673 | 0.1365 | 0.2403 |

## Interpretation

PaDiM achieved higher localisation scores than PatchCore across bottle, hazelnut and capsule. This suggests that PaDiM produces anomaly masks that align more closely with MVTec ground-truth defect regions.

However, PatchCore remains stronger in the overall risk-aware pipeline because it produced stronger image-level detection performance and lower human-review rates in the integrated experiments. Therefore, the results show a trade-off: PatchCore is better suited to operational decision-making, while PaDiM may provide more spatially accurate localisation evidence.

This finding is important for the dissertation because it demonstrates that model performance must be evaluated at multiple levels. A model can be strong at image-level anomaly classification while being weaker at pixel-level localisation, and vice versa.