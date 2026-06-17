# Results and Discussion Placement Note

## Purpose of this note

This note identifies where the main experimental and implementation outputs from the risk-aware inspection prototype should be placed in the final dissertation. The aim is to ensure that the dissertation does not only describe the software implementation, but also presents the results in a clear academic structure.

The results and discussion chapter should show how each part of the system contributes to the dissertation aim: developing a risk-aware visual inspection pipeline for industrial anomaly detection and decision support.

## 1. Detector architecture comparison

The architecture comparison should appear early in the results and discussion chapter because it justifies the choice of anomaly detection model used in the final pipeline.

This section should include the comparison of PatchCore and PaDiM across bottle, capsule and hazelnut. It should refer to the combined architecture comparison table and plot.

Relevant artefacts:

* `docs/experiments/architecture_comparison/all_categories_architecture_comparison_summary.csv`
* `docs/figures/architecture_comparison/all_categories_architecture_comparison.png`
* `docs/experiments/architecture_comparison/all_categories_architecture_comparison_interpretation.md`

The section should explain that both PatchCore and PaDiM were used as anomaly detection architectures. Both methods use feature embeddings extracted from pre-trained convolutional neural network backbones, but they model normality differently. PatchCore stores representative normal patch embeddings in a memory bank and uses nearest-neighbour distance for anomaly scoring, while PaDiM models normal patch embeddings using multivariate Gaussian distributions and uses Mahalanobis distance to identify deviations from normal appearance.

The results showed that PatchCore produced stronger image-level detection performance across the evaluated MVTec AD categories. PatchCore with a ResNet50 backbone provided the strongest overall balance, matching or exceeding the other tested configurations across bottle, capsule and hazelnut. For this reason, PatchCore with ResNet50 should be presented as the preferred image-level anomaly detection architecture for the dissertation pipeline, while PaDiM should be retained as a comparative baseline and localisation reference.

## 2. Image-level anomaly detection performance

After the architecture comparison, the chapter should present the main image-level detection results for the integrated pipeline. This should include accuracy, precision, recall, F1-score and review rate where applicable.

This section should explain how detector choice affects not only classification performance, but also downstream review workload. PatchCore should be discussed as the stronger image-level detector, while PaDiM should be discussed in relation to its comparative strengths and limitations.

The bottle, capsule and hazelnut results should be discussed separately first, then compared together.

## 3. Localisation evaluation

The localisation evaluation should appear after image-level detection performance. This is because localisation depends on the anomaly maps produced by the detection architecture.

This section should use IoU and Dice coefficient to discuss how well the predicted masks align with available MVTec AD ground-truth masks.

Relevant result area:

* localisation evaluation results for bottle, capsule and hazelnut;
* localisation threshold sweep results;
* capsule localisation threshold sweep.

The discussion should highlight that image-level detection performance and localisation quality are not always identical. PatchCore performed strongly for image-level anomaly detection, while PaDiM showed useful localisation behaviour in some cases. This supports a balanced discussion rather than a simple claim that one model is better in every respect.

## 4. Semantic interpretation and review workload

The semantic interpretation results should be placed after localisation because the semantic layer depends on localised anomaly evidence.

This section should discuss the constrained defect taxonomy, semantic fallback rules and unknown-label handling. It should explain that the semantic layer was deliberately constrained to reduce unsupported defect naming.

The capsule semantic fallback update should be used as an example of how the pipeline can be improved without retraining the anomaly detector. The key point is that semantic/governance improvements can reduce human-review workload even when detector-level metrics remain unchanged.

## 5. Risk-aware decision logic and QA disposition

The risk-aware decision logic should be discussed after detection, localisation and semantic interpretation because it combines evidence from these earlier stages.

This section should explain the Risk Priority Matrix, confidence fusion, human-review gating and risk-governed quality disposition layer.

The QA disposition logic should be presented as a decision-support layer, not as a physical production-line controller. It converts inspection outputs into practical recommendations such as pass, reinspect, hold, quarantine, release after review, reject after review or engineering review.

This section should also discuss the false-positive release scenario. If an item is flagged by the anomaly detector but an operator determines that the detection is not operationally meaningful, the system can record this decision and allow release after review. This supports a realistic manufacturing inspection workflow.

## 6. PostgreSQL audit database and operational traceability

The PostgreSQL audit database should be discussed as part of the operational validation of the system.

This section should explain that inspection records and operator review decisions are stored in a database, making the workflow traceable. The database supports auditability because each record can be reviewed, queried and linked to operator decisions.

This should not be presented as only a software feature. It should be framed as part of the dissertation’s contribution to traceable quality-control decision support.

## 7. FastAPI and NiceGUI operational dashboard

The FastAPI and NiceGUI components should be discussed as the operational application layer.

FastAPI provides the backend interface for health checks, record retrieval, summary data, review submission and QA decision support. NiceGUI provides the operator-facing dashboard for filtering records, selecting inspection cases, viewing QA recommendations and saving operator review decisions.

This section should explain that the dashboard demonstrates how the inspection pipeline could be used by an operator in a practical quality-control setting.

## 8. Evidence-linked operator review panel

The evidence-linked operator review panel should appear in the operational dashboard discussion.

Relevant documentation:

* `docs/experiments/evidence_linked_operator_review_panel.md`

This section should explain that the dashboard links selected inspection records to visual artefacts such as annotated evidence, heatmap overlays, predicted masks and anomaly maps. This strengthens the operator review process because decisions are supported by visual evidence rather than metadata alone.

The evidence-linked panel should be discussed as a bridge between model output and human decision-making. It supports traceability by connecting the inspection record, visual evidence, operator decision and audit database.

## 9. Discussion of scalability and limitations

The final part of the results and discussion chapter should discuss scalability and limitations.

The project is scalable at the software level because the pipeline is modular, the detector interface is swappable, PostgreSQL supports structured audit storage, FastAPI supports service-based access, and the dashboard can be extended for further operator workflows.

However, the implementation should still be described as a prototype rather than a fully deployed production-line system. It does not physically control a conveyor, reject gate or robotic sorter. Instead, it demonstrates the decision-support logic that could be connected to industrial control hardware after further validation.

## 10. Recommended chapter flow

The recommended results and discussion chapter flow is:

1. overview of implemented pipeline;
2. anomaly detection architecture comparison;
3. image-level detection results;
4. localisation results;
5. localisation threshold tuning;
6. semantic interpretation and review workload;
7. risk-aware gating and QA disposition;
8. PostgreSQL audit logging;
9. FastAPI and NiceGUI dashboard;
10. evidence-linked operator review panel;
11. scalability, limitations and operational relevance.

This order moves logically from model-level evaluation to pipeline-level decision support and then to operational implementation.
