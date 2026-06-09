# Dissertation Results Chapter Assets

## Purpose

This document consolidates the main quantitative and qualitative results produced during the dissertation implementation. It is intended to support the Results and Discussion chapter by keeping the key tables, findings and figure captions in one place.

## Table 1: Integrated image-level and review performance

| Category | Model / setting                  | Accuracy | Precision | Recall | F1-score | Human review rate |
| -------- | -------------------------------- | -------: | --------: | -----: | -------: | ----------------: |
| bottle   | Statistical original             |   0.5904 |    1.0000 | 0.4603 |   0.6304 |            0.5181 |
| bottle   | Statistical tuned 0.7            |   0.8795 |    0.8955 | 0.9524 |   0.9231 |            0.7711 |
| bottle   | PatchCore integrated             |   0.9880 |    1.0000 | 0.9841 |   0.9920 |            0.1928 |
| bottle   | PaDiM integrated                 |   0.9518 |    0.9538 | 0.9841 |   0.9688 |            0.6867 |
| hazelnut | Statistical original             |   0.4364 |    0.8333 | 0.1429 |   0.2439 |            0.2273 |
| hazelnut | Statistical tuned 0.7            |   0.5545 |    0.6567 | 0.6286 |   0.6423 |            0.7636 |
| hazelnut | PatchCore integrated             |   0.9909 |    1.0000 | 0.9857 |   0.9928 |            0.1727 |
| hazelnut | PaDiM integrated                 |   0.7182 |    0.6970 | 0.9857 |   0.8166 |            0.9000 |
| capsule  | PatchCore integrated             |   0.9697 |    0.9907 | 0.9725 |   0.9815 |            0.6818 |
| capsule  | PatchCore + semantic fallback v3 |   0.9697 |    0.9907 | 0.9725 |   0.9815 |            0.5152 |
| capsule  | PaDiM integrated                 |   0.9015 |    0.9000 | 0.9908 |   0.9432 |            0.8712 |
| capsule  | PaDiM + semantic fallback v3     |   0.9015 |    0.9000 | 0.9908 |   0.9432 |            0.8409 |

## Table 2: Default localisation performance

| Category | Model     | Mean IoU | Mean Dice | Median IoU | Median Dice |
| -------- | --------- | -------: | --------: | ---------: | ----------: |
| bottle   | PatchCore |   0.3472 |    0.4928 |     0.3480 |      0.5164 |
| bottle   | PaDiM     |   0.4968 |    0.6442 |     0.4930 |      0.6604 |
| hazelnut | PatchCore |   0.1456 |    0.2316 |     0.1070 |      0.1933 |
| hazelnut | PaDiM     |   0.3084 |    0.4444 |     0.3168 |      0.4811 |
| capsule  | PatchCore |   0.1068 |    0.1671 |     0.0450 |      0.0862 |
| capsule  | PaDiM     |   0.1731 |    0.2673 |     0.1365 |      0.2403 |

## Table 3: Tuned localisation threshold performance

| Category | Model     | Best threshold | Mean IoU | Mean Dice | Median IoU | Median Dice |
| -------- | --------- | -------------: | -------: | --------: | ---------: | ----------: |
| bottle   | PatchCore |           0.70 |   0.5929 |    0.7322 |     0.5916 |      0.7434 |
| bottle   | PaDiM     |           0.35 |   0.5110 |    0.6612 |     0.4990 |      0.6658 |
| hazelnut | PatchCore |           0.80 |   0.4331 |    0.5854 |     0.4232 |      0.5947 |
| hazelnut | PaDiM     |           0.50 |   0.3340 |    0.4693 |     0.3225 |      0.4877 |
| capsule  | PatchCore |           0.85 |   0.2979 |    0.4311 |     0.2732 |      0.4291 |
| capsule  | PaDiM     |           0.55 |   0.1830 |    0.2749 |     0.1464 |      0.2554 |

## Key findings

PatchCore produced the strongest image-level performance across the tested categories. It achieved high F1-scores and lower human-review rates than PaDiM in the integrated risk-aware pipeline.

PaDiM produced stronger default localisation masks before threshold tuning. However, after threshold optimisation, PatchCore achieved the strongest localisation results across bottle, hazelnut and capsule.

The capsule semantic fallback experiment reduced the PatchCore human-review rate from 0.6818 to 0.5152 without changing the image-level F1-score. This shows that the risk-aware governance layer can improve operational review efficiency without retraining the anomaly detector.

The localisation threshold sweep showed that post-processing has a major effect on IoU and Dice. PatchCore benefited most from threshold tuning, especially on capsule, where mean Dice increased from 0.1671 to 0.4311.

Bottle achieved the strongest localisation scores, followed by hazelnut and capsule. Capsule remained the most difficult category because many capsule defects are small, narrow or visually subtle.

## Suggested figure captions

Figure X. Example PatchCore capsule localisation results before and after threshold tuning. The figure compares the original image, MVTec ground-truth mask, PatchCore anomaly map, default predicted mask and tuned mask. The tuned threshold of 0.85 produced a more selective mask and improved alignment with the ground-truth defect region.

Figure X. Example PatchCore bottle localisation results before and after threshold tuning. The tuned threshold of 0.70 reduced over-segmentation and produced a binary mask that aligned more closely with the MVTec ground-truth defect mask.

Figure X. Example PaDiM bottle localisation results before and after threshold tuning. The tuned threshold of 0.35 improved the spatial overlap between predicted and ground-truth masks, although PatchCore achieved stronger tuned localisation scores overall.

Figure X. Example PatchCore hazelnut localisation results before and after threshold tuning. The tuned threshold of 0.80 improved mask selectivity and produced clearer localisation of damaged regions.

Figure X. Example PaDiM hazelnut localisation results before and after threshold tuning. The tuned threshold of 0.50 improved localisation compared with the default mask, but its overall tuned IoU and Dice remained lower than PatchCore.

## Results chapter argument

The results show that the proposed risk-aware inspection pipeline should not be judged only by anomaly classification accuracy. Image-level detection, localisation quality, semantic interpretation, confidence fusion and human-review behaviour each provide different evidence about system performance.

PatchCore was the strongest model for image-level anomaly detection and operational review efficiency. PaDiM initially produced better default localisation masks, but PatchCore became the stronger localisation model after threshold tuning. This demonstrates that post-processing is an important part of the overall inspection pipeline.

The semantic fallback and localisation threshold experiments also show that the downstream stages of the risk-aware pipeline can improve system usefulness without retraining the anomaly detector. This supports the dissertation aim of building an explainable and configurable inspection framework rather than only comparing anomaly detection models.
