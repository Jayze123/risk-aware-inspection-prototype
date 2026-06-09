# Results and Discussion Draft

## 4.1 Introduction

This chapter presents the results obtained from the implementation and evaluation of the risk-aware visual inspection pipeline. The evaluation considers image-level anomaly detection, localisation performance, semantic interpretation, confidence-based human-review gating and the effect of post-processing on predicted anomaly masks.

The experiments were carried out using selected MVTec AD categories, including bottle, hazelnut and capsule. PatchCore and PaDiM were integrated into the risk-aware pipeline and compared against the earlier statistical baseline. The results are discussed in terms of detection accuracy, precision, recall, F1-score, review workload, IoU and Dice coefficient.

## 4.2 Image-Level Detection and Review Performance

The integrated results show that PatchCore produced the strongest image-level anomaly detection performance across the tested categories. For bottle, PatchCore achieved an F1-score of 0.9920 and a human-review rate of 0.1928. For hazelnut, PatchCore achieved an F1-score of 0.9928 and a human-review rate of 0.1727. These results were stronger than the earlier statistical detector and also more operationally efficient than PaDiM.

PaDiM also produced strong recall in some experiments, but its review rate was higher, especially for hazelnut and capsule. This suggests that PaDiM was more sensitive to anomalous regions but also produced more uncertain or false-positive cases requiring review. In a practical inspection setting, this would increase the workload for a human operator.

The capsule experiment also showed the value of the semantic fallback rule. PatchCore’s capsule F1-score remained unchanged at 0.9815, while the human-review rate reduced from 0.6818 to 0.5152. This shows that the downstream semantic and governance layer can improve review efficiency without retraining the anomaly detector.

## 4.3 Default Localisation Performance

The default localisation results showed a different trend from the image-level classification results. Before threshold tuning, PaDiM produced better localisation masks than PatchCore across the tested categories. For example, PaDiM achieved a mean Dice score of 0.6442 on bottle, compared with 0.4928 for PatchCore. On hazelnut, PaDiM achieved a mean Dice score of 0.4444 compared with 0.2316 for PatchCore. On capsule, PaDiM achieved a mean Dice score of 0.2673 compared with 0.1671 for PatchCore.

This indicates that strong image-level detection does not automatically mean strong pixel-level localisation. PatchCore was better at classifying images as anomalous or normal, but its default masks were less closely aligned with the ground-truth defect masks. This is an important finding because an industrial inspection system may need both reliable detection and meaningful visual explanation.

## 4.4 Localisation Threshold Tuning

A threshold sweep was then carried out to test whether localisation performance could be improved by changing the anomaly-map threshold used to convert heatmaps into binary masks. This experiment showed that PatchCore benefited strongly from threshold tuning.

For bottle, PatchCore’s mean Dice improved to 0.7322 using a threshold of 0.70. For hazelnut, PatchCore’s mean Dice improved to 0.5854 using a threshold of 0.80. For capsule, PatchCore’s mean Dice improved from 0.1671 to 0.4311 using a threshold of 0.85.

PaDiM also improved after threshold tuning, but the improvement was smaller. After tuning, PatchCore achieved the strongest localisation results across bottle, hazelnut and capsule. This suggests that PatchCore’s anomaly maps contained useful localisation information, but the original binary mask conversion was not optimal.

## 4.5 Qualitative Localisation Evidence

The generated visual examples support the quantitative IoU and Dice results. The figures compare the original image, ground-truth mask, anomaly map, default predicted mask and tuned threshold mask. In several examples, the default predicted mask selected broad or fragmented regions, while the tuned mask became more selective and better aligned with the true defect location.

The capsule examples were particularly useful because the default masks often over-segmented the image. After applying the tuned threshold of 0.85, the predicted masks became more focused on the actual defect area. For example, the Dice score for capsule_test_squeeze_010 improved from 0.205 to 0.861. Similar improvements were observed in bottle and hazelnut examples.

These results show that post-processing is not a minor technical detail. It directly affects the usefulness of localisation outputs and the quality of visual evidence available to a human reviewer.

## 4.6 Overall Discussion

Overall, the results show that the proposed pipeline should not be evaluated only by anomaly classification accuracy. Image-level detection, localisation, semantic interpretation and review workload each provide different information about system performance.

PatchCore was the strongest model for image-level detection and operational review efficiency. PaDiM initially produced better default localisation masks, but PatchCore became stronger after threshold tuning. This shows that model selection depends on the intended use of the system. If the priority is classification and review efficiency, PatchCore is stronger. If default localisation without tuning is prioritised, PaDiM initially performs better. However, with threshold optimisation, PatchCore provides the strongest overall balance.

The results also support the purpose of a risk-aware inspection framework. The semantic fallback rule and localisation threshold sweep both improved the usefulness of the system without retraining the anomaly detector. This shows that downstream reasoning, configuration and post-processing can play an important role in industrial visual inspection.
