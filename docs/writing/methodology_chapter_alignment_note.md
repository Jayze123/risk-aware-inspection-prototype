# Methodology Chapter Alignment Note

## Purpose of this note

This note aligns the implemented risk-aware inspection prototype with the methodology chapter of the dissertation. It confirms that the practical system developed in the repository remains consistent with the proposed research direction: using anomaly detection, localisation, semantic interpretation, risk-aware reasoning and operator review to support industrial visual inspection.

The implemented system should not be described only as an anomaly detection model. It is better described as a risk-aware inspection pipeline, because the anomaly detector is only one component within a broader decision-support workflow.

## Alignment with the proposed methodology

The methodology is based on a modular inspection pipeline. Each stage produces information that is passed to the next stage, allowing the system to move from visual anomaly detection to traceable quality-control decision support.

The implemented workflow follows this structure:

1. image ingestion and preprocessing;
2. image-level anomaly detection;
3. pixel-level anomaly localisation;
4. semantic interpretation using a constrained defect taxonomy;
5. risk classification using a deterministic Risk Priority Matrix;
6. confidence fusion;
7. human-review gating;
8. risk-governed quality disposition;
9. audit logging and operator review;
10. API and dashboard-based operator interaction.

This structure is consistent with the dissertation aim because it evaluates not only whether an image is anomalous, but also how anomaly outputs can support practical inspection decisions.

## Dataset and experimental setup

The experiments use MVTec AD-style industrial anomaly detection data. The evaluated categories include bottle, capsule and hazelnut. These categories provide a suitable basis for testing the pipeline because they include normal training samples, anomalous test samples and, where available, ground-truth masks for localisation evaluation.

The normal samples are used to model defect-free appearance, while the test samples are used to evaluate anomaly detection and localisation performance. This follows the common industrial anomaly detection setting, where models are trained mainly on normal data and are expected to detect deviations from normal appearance during inspection.

## Anomaly detection architecture

Both PatchCore and PaDiM were used as anomaly detection architectures in the project. Both methods use feature embeddings extracted from pre-trained convolutional neural network backbones, but they model normality differently. PatchCore stores representative normal patch embeddings in a memory bank and uses nearest-neighbour distance for anomaly scoring, while PaDiM models normal patch embeddings using multivariate Gaussian distributions and uses Mahalanobis distance to identify deviations from normal appearance.

A controlled architecture comparison was carried out across bottle, capsule and hazelnut. PatchCore was evaluated using `resnet18`, `resnet50` and `wide_resnet50_2` backbones. PaDiM was evaluated using `resnet18` and `resnet50`, with `n_features` set to 100 for the ResNet50 PaDiM runs because the installed Anomalib implementation requires an explicit retained feature dimension for that backbone.

The experimental comparison showed that PatchCore produced stronger image-level detection performance across the evaluated MVTec AD categories. PatchCore with a ResNet50 backbone provided the strongest overall balance, matching or exceeding the other tested configurations across bottle, capsule and hazelnut. For this reason, PatchCore with ResNet50 was selected as the preferred image-level anomaly detection architecture for the dissertation pipeline, while PaDiM remained an important comparative baseline and localisation reference.

## Localisation and post-processing

The anomaly detection stage produces image-level scores and anomaly maps. The localisation stage converts anomaly maps into binary masks using thresholding, morphology and connected components. This allows the system to identify regions of the image that are likely to contain abnormal visual patterns.

Localisation was evaluated using IoU and Dice coefficient against available MVTec AD ground-truth masks. Localisation threshold sweeps were also implemented to test whether post-processing could improve mask alignment without retraining the anomaly detector. This is methodologically important because it separates model training from downstream post-processing and shows that operational performance can be improved through pipeline-level tuning.

## Semantic interpretation and risk reasoning

The semantic interpretation stage uses a constrained defect taxonomy rather than open-ended defect naming. This design reduces uncontrolled interpretation and supports traceability. If a defect cannot be confidently mapped to the taxonomy, the system treats the case as uncertain rather than inventing an unsupported label.

The risk stage uses a deterministic Risk Priority Matrix. This maps known defect categories to risk levels in a transparent way. Missing or uncertain semantic mappings are routed to review instead of being assigned unsupported automatic risk values.

This approach is suitable for a risk-aware inspection methodology because it makes the decision process explainable and auditable.

## Confidence fusion and human-review gating

The pipeline includes confidence fusion using minimum and weighted-average strategies. This combines model confidence, localisation evidence and semantic confidence into a final decision-support signal.

Human-review gating is used for uncertain, high-risk or ambiguous cases. This means that the system does not attempt to fully automate every decision. Instead, it identifies which inspection cases should be escalated to an operator.

This supports the dissertation argument that anomaly detection systems should be evaluated not only by classification accuracy, but also by their effect on review workload, traceability and decision reliability.

## Risk-governed quality disposition

A risk-governed quality disposition layer was added to convert inspection evidence into practical quality-control actions. The layer considers anomaly status, risk class, confidence, semantic ambiguity and the latest operator review decision.

The possible disposition outcomes include pass, pass with monitoring, reinspect, hold, quarantine, review required, release after review, reject after review and engineering review.

This is important because it demonstrates how an anomaly detection output can be converted into a quality-control decision. It also supports realistic manufacturing scenarios where an item may initially be flagged as anomalous but later released after operator review confirms that the detection was a false positive.

## Operational application layer

The operational application layer was implemented using PostgreSQL, Docker, FastAPI and NiceGUI.

PostgreSQL is used as the audit database for inspection records and operator review decisions. Docker Compose is used to run the PostgreSQL service in a reproducible local environment. FastAPI exposes endpoints for health checking, inspection records, summaries, review submission and QA decision support. NiceGUI provides an operator-facing dashboard for reviewing records, filtering inspection cases, loading selected records and saving operator decisions.

This layer strengthens the methodology because it shows how the research pipeline can be connected to an operator workflow. It also provides evidence that the project is not limited to offline model evaluation, but includes audit logging, review traceability and practical decision-support interaction.

## Evaluation strategy

The methodology evaluates the system at multiple levels:

1. image-level detection performance using AUROC and F1-score;
2. localisation quality using IoU and Dice coefficient;
3. review workload using human-review rate;
4. semantic and governance behaviour using unknown-label handling and fallback rules;
5. operational traceability using PostgreSQL audit records;
6. operator interaction using the FastAPI and NiceGUI application layer;
7. architecture suitability using PatchCore and PaDiM backbone comparison.

This multi-level evaluation is important because a high-performing anomaly detector is not automatically sufficient for industrial decision support. The dissertation therefore evaluates both model performance and downstream operational behaviour.

## Scope and limitation

The current implementation is a prototype-level decision-support system rather than a fully deployed production-line controller. It does not physically actuate a conveyor, reject gate or robotic sorting mechanism. Instead, it demonstrates the decision logic, audit trail and operator workflow that could later be integrated with production-line control hardware after further validation.

The prototype is therefore suitable for dissertation evaluation because it demonstrates the technical feasibility and research value of a risk-aware inspection pipeline, while keeping the scope realistic for an MSc project.

## Methodological contribution

The main methodological contribution is the integration of anomaly detection with risk-aware reasoning, localisation evaluation, operator review and audit logging. The project moves beyond simple image classification by showing how anomaly outputs can be converted into traceable inspection decisions.

The architecture comparison further strengthens the methodology by showing that the selected detection model was not chosen arbitrarily. PatchCore with ResNet50 was selected because it provided the strongest overall image-level detection balance across the evaluated categories, while PaDiM remained a useful comparative baseline and localisation reference.

This methodology supports the dissertation objective of developing and evaluating a risk-aware visual inspection framework for industrial anomaly detection.
