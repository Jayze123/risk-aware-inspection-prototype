# Chapter 4: Results and Discussion

## 4.1 Introduction

This chapter presents the experimental results obtained from the risk-aware visual inspection pipeline. The evaluation focuses on three main aspects of the system: image-level anomaly detection, pixel-level localisation, and operational review behaviour. These aspects are considered separately because a model that performs well at classifying an image as normal or anomalous may not necessarily produce the most accurate localisation mask or the most efficient human-review workflow.

The experiments were carried out using the bottle, hazelnut and capsule categories from the MVTec AD dataset. These categories were selected because they contain visually different types of industrial defects, including structural damage, surface contamination, cracks, holes, scratches and deformation. PatchCore and PaDiM were integrated into the proposed pipeline and compared with the earlier statistical baseline where available. The models were evaluated using accuracy, precision, recall and F1-score for image-level classification. Localisation was evaluated using Intersection over Union (IoU) and Dice coefficient, which measure the overlap between predicted anomaly masks and the ground-truth defect masks (Jaccard, 1912; Dice, 1945).

## 4.2 Image-Level Detection and Human-Review Performance

Table 4.1 summarises the image-level performance of the statistical baseline, PatchCore and PaDiM after integration with the risk-aware pipeline. The results show that PatchCore achieved the strongest overall image-level performance across the tested categories. For bottle, PatchCore achieved an F1-score of 0.9920 with a human-review rate of 0.1928. For hazelnut, it achieved an F1-score of 0.9928 with a human-review rate of 0.1727. These results indicate that PatchCore provided both accurate anomaly decisions and a lower review burden compared with the other tested settings.

**Table 4.1: Integrated image-level and review performance**

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

PatchCore was particularly effective because it maintained high precision and recall while producing fewer cases that required human review. This is important in an industrial setting, where a technically accurate system may still be impractical if too many outputs need manual checking. PaDiM achieved high recall in several cases, but its higher review rates suggest that it produced more uncertain outputs or cases that were less confidently mapped through the downstream risk-aware logic.

The capsule results also demonstrate the usefulness of the semantic fallback rule. After the capsule-specific semantic fallback was introduced, PatchCore’s F1-score remained unchanged at 0.9815, while the review rate reduced from 0.6818 to 0.5152. This is a useful outcome because it shows that the governance and semantic interpretation layer can improve operational efficiency without retraining the anomaly detector. In other words, the pipeline is not only dependent on the detector itself; downstream interpretation and decision rules also affect the practical usefulness of the system.

## 4.3 Default Localisation Performance

The default localisation results are shown in Table 4.2. These results compare the predicted anomaly masks with MVTec ground-truth masks using IoU and Dice coefficient. Before threshold tuning, PaDiM produced stronger localisation masks than PatchCore across all three categories. For bottle, PaDiM achieved a mean Dice score of 0.6442 compared with 0.4928 for PatchCore. For hazelnut, PaDiM achieved a mean Dice score of 0.4444 compared with 0.2316 for PatchCore. For capsule, PaDiM achieved a mean Dice score of 0.2673 compared with 0.1671 for PatchCore.

**Table 4.2: Default localisation performance**

| Category | Model     | Mean IoU | Mean Dice | Median IoU | Median Dice |
| -------- | --------- | -------: | --------: | ---------: | ----------: |
| bottle   | PatchCore |   0.3472 |    0.4928 |     0.3480 |      0.5164 |
| bottle   | PaDiM     |   0.4968 |    0.6442 |     0.4930 |      0.6604 |
| hazelnut | PatchCore |   0.1456 |    0.2316 |     0.1070 |      0.1933 |
| hazelnut | PaDiM     |   0.3084 |    0.4444 |     0.3168 |      0.4811 |
| capsule  | PatchCore |   0.1068 |    0.1671 |     0.0450 |      0.0862 |
| capsule  | PaDiM     |   0.1731 |    0.2673 |     0.1365 |      0.2403 |

This result is important because it shows that image-level classification and localisation quality are not the same problem. PatchCore performed better at deciding whether an image was anomalous, but PaDiM initially produced masks that aligned more closely with the ground-truth defect regions. This supports the need for a multi-level evaluation framework rather than relying only on image-level metrics.

## 4.4 Localisation Threshold Tuning

A threshold sweep was carried out to test whether localisation performance could be improved by adjusting the anomaly-map threshold used to generate binary masks. This was done without retraining PatchCore or PaDiM. The tuned results are shown in Table 4.3.

**Table 4.3: Tuned localisation threshold performance**

| Category | Model     | Best threshold | Mean IoU | Mean Dice | Median IoU | Median Dice |
| -------- | --------- | -------------: | -------: | --------: | ---------: | ----------: |
| bottle   | PatchCore |           0.70 |   0.5929 |    0.7322 |     0.5916 |      0.7434 |
| bottle   | PaDiM     |           0.35 |   0.5110 |    0.6612 |     0.4990 |      0.6658 |
| hazelnut | PatchCore |           0.80 |   0.4331 |    0.5854 |     0.4232 |      0.5947 |
| hazelnut | PaDiM     |           0.50 |   0.3340 |    0.4693 |     0.3225 |      0.4877 |
| capsule  | PatchCore |           0.85 |   0.2979 |    0.4311 |     0.2732 |      0.4291 |
| capsule  | PaDiM     |           0.55 |   0.1830 |    0.2749 |     0.1464 |      0.2554 |

The threshold sweep changed the localisation comparison significantly. After tuning, PatchCore achieved the strongest localisation performance across bottle, hazelnut and capsule. For bottle, PatchCore’s mean Dice score increased to 0.7322 using a threshold of 0.70. For hazelnut, it increased to 0.5854 using a threshold of 0.80. For capsule, PatchCore’s mean Dice improved from 0.1671 to 0.4311 using a threshold of 0.85.

PaDiM also improved after threshold tuning, but the increase was smaller. This suggests that PaDiM’s default masks were already closer to its best thresholded performance, while PatchCore’s anomaly maps contained useful localisation information that was not fully captured by the original mask conversion. The finding is useful because it shows that localisation performance can be improved through post-processing rather than retraining the full anomaly detection model.

## 4.5 Qualitative Localisation Examples

The qualitative figures support the numerical IoU and Dice results. Each comparison figure contains the original image, the MVTec ground-truth mask, the anomaly map, the default predicted mask and the tuned threshold mask. This layout makes it easier to understand why the tuned threshold improved the localisation scores.

**Figure 4.1: PatchCore capsule localisation before and after threshold tuning.**
The tuned threshold of 0.85 produced more selective masks than the default output. In several capsule examples, the default mask selected broad or fragmented regions, while the tuned mask aligned more closely with the small defect area. For example, the Dice score for `capsule_test_squeeze_010` improved from 0.205 to 0.861.

**Figure 4.2: PatchCore bottle localisation before and after threshold tuning.**
The tuned threshold of 0.70 reduced over-segmentation and improved the match between the predicted mask and the ground-truth defect area. The examples show that the anomaly maps already highlighted relevant defect regions, but threshold selection had a major effect on the final binary mask.

**Figure 4.3: PaDiM bottle localisation before and after threshold tuning.**
The tuned threshold of 0.35 improved the spatial overlap between predicted and ground-truth masks. However, the tuned PatchCore bottle results still produced the highest overall mean Dice score.

**Figure 4.4: PatchCore hazelnut localisation before and after threshold tuning.**
The tuned threshold of 0.80 produced more focused masks for damaged hazelnut regions. The examples show a clear improvement over the default masks, particularly where the default output selected larger regions than the ground truth.

**Figure 4.5: PaDiM hazelnut localisation before and after threshold tuning.**
The tuned threshold of 0.50 improved localisation compared with the default mask, although its overall tuned IoU and Dice remained lower than PatchCore.

These visual examples are important because they show that the numerical improvements are not only caused by small metric changes. The tuned masks are visibly more useful for interpretation, especially when the default masks include excessive false regions.

## 4.6 Overall Discussion

The results show that the proposed inspection pipeline should not be judged only by anomaly classification accuracy. Image-level detection, localisation performance, semantic interpretation and human-review behaviour each provide different evidence about system performance.

PatchCore was the strongest model for image-level anomaly detection and operational review efficiency. PaDiM initially produced stronger default localisation masks, but PatchCore became the stronger localisation model after threshold tuning. This means that model selection depends on the intended use of the system. If the priority is accurate anomaly classification and reduced review workload, PatchCore is the stronger option. If the system is used without additional localisation threshold tuning, PaDiM may initially provide better mask alignment. However, when threshold optimisation is included, PatchCore provides the strongest overall balance across the tested categories.

The capsule semantic fallback experiment also supports the value of the risk-aware design. The fallback rule reduced the review rate without reducing the image-level F1-score. This shows that semantic interpretation and governance rules can improve the operational behaviour of the pipeline without modifying the detector. This is useful for industrial inspection, where traceability and review efficiency are important alongside raw model accuracy.

The localisation threshold sweep further shows that post-processing is not a minor implementation detail. It directly affects the usefulness of the visual evidence provided to a human reviewer. A poor threshold can make a good anomaly map appear inaccurate, while a better threshold can produce a mask that is much closer to the ground-truth defect region.

## 4.7 Chapter Summary

This chapter evaluated the implemented risk-aware inspection pipeline using image-level metrics, localisation metrics and human-review behaviour. PatchCore achieved the best image-level performance and lowest review burden across the main integrated experiments. PaDiM produced stronger default localisation masks, but PatchCore achieved the best tuned localisation results after threshold optimisation.

The results demonstrate that a risk-aware inspection system should be evaluated as a complete pipeline rather than as a detector alone. The anomaly detector, semantic label mapping, confidence fusion, review gating and localisation post-processing all influence the final system output. This supports the central aim of the project: to develop an inspection framework that combines anomaly detection with explainable, configurable and review-aware decision support.

## References

Bergmann, P., Fauser, M., Sattlegger, D. and Steger, C. (2019) ‘MVTec AD — A comprehensive real-world dataset for unsupervised anomaly detection’, *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pp. 9592–9600.

Defard, T., Setkov, A., Loesch, A. and Audigier, R. (2021) ‘PaDiM: A patch distribution modeling framework for anomaly detection and localization’, *Pattern Recognition. ICPR International Workshops and Challenges*, Lecture Notes in Computer Science, 12664, pp. 475–489.

Dice, L.R. (1945) ‘Measures of the amount of ecologic association between species’, *Ecology*, 26(3), pp. 297–302.

Jaccard, P. (1912) ‘The distribution of the flora in the alpine zone’, *New Phytologist*, 11(2), pp. 37–50.

Roth, K., Pemula, L., Zepeda, J., Schölkopf, B., Brox, T. and Gehler, P. (2022) ‘Towards total recall in industrial anomaly detection’, *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, pp. 14318–14328.

