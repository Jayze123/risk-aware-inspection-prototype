# Risk-Aware Vision Pipeline Prototype

This repository contains a VS Code-compatible research prototype for the MSc dissertation project titled **Risk-Aware Vision Pipeline for Industrial Visual Inspection and Anomaly Detection**.

The project implements a risk-aware industrial inspection workflow that combines anomaly detection, localisation, semantic interpretation, risk classification, human-review gating, audit logging and operator-facing decision support. The purpose of the prototype is to evaluate how anomaly detection outputs can be extended into a more operationally useful inspection framework, rather than treating defect detection as a standalone classification task.

The implemented workflow includes:

1. image ingestion and preprocessing;
2. anomaly detection through a modular detector interface;
3. anomaly detection using statistical reference modelling, PatchCore and PaDiM;
4. localisation through anomaly-map thresholding, morphology and connected components;
5. constrained semantic interpretation using a fixed defect taxonomy;
6. deterministic Risk Priority Matrix lookup;
7. confidence fusion using minimum and weighted-average strategies;
8. human-review gating for uncertain, high-risk or semantically ambiguous cases;
9. quality disposition decisions such as pass, hold, reinspect, quarantine and release after review;
10. PostgreSQL audit logging for inspection records and operator reviews;
11. FastAPI backend endpoints for inspection records, summaries, reviews and QA decisions;
12. NiceGUI operator dashboard for inspection review and decision support;
13. JSONL, CSV, database and visual artefact output for traceability.

The project initially used a simple normal-reference statistical detector so that the full pipeline could be executed immediately in VS Code without GPU access. The pipeline has since been extended with PaDiM and PatchCore experiments, allowing the statistical baseline to be compared with established industrial anomaly detection architectures.

## Project structure

```text
risk_aware_inspection_prototype/
├── config/
│   └── pipeline.yaml
├── database/
│   └── schema.sql
├── docs/
│   ├── experiments/
│   ├── figures/
│   └── writing/
├── scripts/
│   ├── train_patchcore_mvtec.py
│   ├── train_patchcore_folder_mvtec.py
│   ├── train_padim_folder_mvtec.py
│   ├── evaluate_localisation_mvtec.py
│   ├── tune_localisation_thresholds.py
│   └── load_results_to_audit_db.py
├── src/
│   └── risk_aware_inspection/
│       ├── api_app.py
│       ├── audit_db.py
│       ├── cli.py
│       ├── confidence.py
│       ├── config.py
│       ├── dashboard_app.py
│       ├── gating.py
│       ├── ingestion.py
│       ├── localisation.py
│       ├── outputs.py
│       ├── pipeline.py
│       ├── qa_release.py
│       ├── risk.py
│       ├── semantics.py
│       └── detectors/
│           ├── base.py
│           ├── simple_statistical.py
│           └── anomalib_adapter.py
├── tests/
├── docker-compose.yml
├── requirements.txt
├── requirements-anomalib.txt
├── pyproject.toml
└── README.md
```

## Setup in VS Code

Open the project folder in VS Code and create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

For macOS/Linux:

```bash
source .venv/bin/activate
```

Install the project:

```bash
pip install -e .
```

For Anomalib-based experiments, use the dedicated Anomalib environment and the relevant requirements file used for PatchCore and PaDiM runs.

## Quick demo

Create synthetic normal and anomalous inspection images:

```bash
python -m risk_aware_inspection.cli make-demo --output data/demo
```

Calibrate the simple detector on normal images:

```bash
python -m risk_aware_inspection.cli calibrate \
  --normal-dir data/demo/normal \
  --config config/pipeline.yaml \
  --model outputs/simple_reference_model.npz
```

Inspect the demo test images:

```bash
python -m risk_aware_inspection.cli inspect \
  --input data/demo/test \
  --config config/pipeline.yaml \
  --model outputs/simple_reference_model.npz \
  --output outputs/run_demo
```

Outputs are written to:

```text
outputs/run_demo/results.jsonl
outputs/run_demo/results.csv
outputs/run_demo/artefacts/*_heatmap_overlay.png
outputs/run_demo/artefacts/*_mask.png
outputs/run_demo/artefacts/*_annotated.png
```

## Using real images

For real-image experiments, normal training or reference images should be placed in a dedicated folder and used to calibrate or train the selected detector. Test images are then processed through the same inspection pipeline.

For MVTec AD-style experiments, the official `train/good` folder is used as the normal reference set, while the `test/*` folders are used for evaluation.

## Detector interface and Anomalib integration

The downstream pipeline expects each detector to provide a consistent output contract:

* image-level anomaly score;
* calibrated anomaly threshold;
* binary anomaly decision;
* anomaly confidence;
* pixel-level heatmap in `[0, 1]`.

The project integrates Anomalib-based PatchCore and PaDiM experiments into the same downstream risk-aware pipeline. This means that anomaly detection, localisation, semantic interpretation, risk classification, human-review gating and audit logging can be applied consistently across detector types.

This modular structure allows detector architectures to be changed without rewriting the localisation, semantic interpretation, Risk Priority Matrix, confidence fusion, gating or output logging stages.

## Model architecture parameterisation for comparison experiments

The anomaly detection training scripts have been updated to support controlled architecture comparison. This allows the project to evaluate how different feature-extraction backbones and detector hyperparameters affect detection performance, localisation quality and downstream review workload.

The implemented PatchCore detector uses a pre-trained `wide_resnet50_2` convolutional backbone with `layer2` and `layer3` feature extraction. PatchCore applies memory-bank modelling, coreset sampling and nearest-neighbour anomaly scoring to produce image-level anomaly decisions and anomaly maps. The PatchCore scripts support configurable architecture and hyperparameter settings through the following command-line arguments:

* `--backbone`
* `--coreset-sampling-ratio`
* `--num-neighbors`

The implemented PaDiM detector uses a pre-trained `resnet18` convolutional backbone with multi-layer patch feature extraction and statistical modelling of normal patch embeddings. The PaDiM script supports configurable architecture settings through:

* `--backbone`
* `--n-features`

This allows the project to compare feature-extraction backbones such as `resnet18`, `resnet50` and `wide_resnet50_2` while keeping the downstream inspection pipeline consistent. The comparison is intended to support the dissertation results and discussion chapter by showing how architecture choice affects image-level detection performance, localisation behaviour, review workload and operational suitability.

The preferred architecture will be selected based on the overall balance between detection performance, localisation quality, review efficiency and suitability for the proposed industrial inspection workflow, rather than on a single metric alone.

## Operational application layer

The project includes an operational application layer for inspection review, traceability and decision support.

PostgreSQL is used as the audit database for inspection records and operator review decisions. Docker Compose is used to run the PostgreSQL service in a reproducible local environment. FastAPI exposes health checks, inspection records, summaries, review submission and QA decision endpoints. NiceGUI provides an operator-facing dashboard for viewing inspection records, filtering cases, loading selected records and saving review decisions.

This operational layer extends the prototype beyond anomaly detection alone. It demonstrates how model outputs can be connected to traceable quality-control decision support in a way that is closer to an industrial inspection workflow.

### Evidence-linked operator review panel

The NiceGUI operator dashboard includes an evidence-linked review panel. When an inspection record is loaded, the dashboard searches the local `outputs/` directory for visual artefacts linked to the selected `image_id`. The panel displays available annotated inspection images, heatmap overlays, predicted masks and anomaly-map evidence.

This links the database inspection record to the visual evidence used during operator review. It supports traceable quality-control decision making because an operator can review the anomaly evidence before saving a decision such as accept, reject, reinspect or false-positive release.

The feature strengthens the operational layer of the prototype by connecting anomaly detection outputs, localisation artefacts, PostgreSQL audit records, operator review decisions and risk-governed quality disposition.

## Risk-governed quality disposition layer

A risk-governed quality disposition layer has been added to convert inspection evidence into practical quality-control actions.

The layer considers anomaly status, risk class, confidence, semantic ambiguity and the latest operator review decision. It can return outcomes such as:

* `PASS`
* `PASS_WITH_MONITORING`
* `REINSPECT`
* `HOLD`
* `QUARANTINE`
* `REVIEW_REQUIRED`
* `RELEASE_AFTER_REVIEW`
* `REJECT_AFTER_REVIEW`
* `ENGINEERING_REVIEW`

This supports scenarios where a product is initially flagged as anomalous but is later released after an operator confirms that the result was a false positive. The decision is stored through the audit workflow, preserving traceability between the model output, the operator review and the final quality disposition.

## Research notes

The current prototype is designed for dissertation research rather than direct production deployment. The main research-facing features are modularity, traceable outputs, deterministic risk mapping, operator review and auditable decision support.

The semantic component is deliberately constrained to a fixed taxonomy. Missing or uncertain semantic mappings cause Review Required rather than unsupported automatic risk decisions. This design choice reduces uncontrolled interpretation and keeps the system suitable for risk-aware inspection workflows.

The current implementation does not physically control a conveyor, reject gate or robotic sorting mechanism. Instead, it demonstrates the decision logic and audit structure that could later be connected to production-line control systems after further validation.

## Current experiment results

The current prototype has been tested on three MVTec AD categories: bottle, hazelnut and capsule. The experiments compare the initial statistical detector, threshold-tuned statistical detection, PatchCore and PaDiM after integration with the risk-aware inspection pipeline.

### Architecture comparison across evaluated categories

A controlled architecture comparison was carried out across the bottle, capsule and hazelnut categories to evaluate how different PatchCore and PaDiM configurations affected image-level anomaly detection performance. PatchCore was evaluated using `resnet18`, `resnet50` and `wide_resnet50_2` backbones, while PaDiM was evaluated using `resnet18` and `resnet50`. For the PaDiM `resnet50` runs, `n_features` was set to 100 because the installed Anomalib implementation requires an explicit retained feature dimension for that backbone.

The comparison showed that PatchCore produced stronger and more consistent image-level detection performance across the evaluated categories. PatchCore with a `resnet50` backbone provided the strongest overall balance, matching or exceeding the other tested configurations across bottle, capsule and hazelnut. On bottle, all PatchCore backbones achieved an image AUROC of 1.0000 and an image F1-score of 0.9920. On capsule, PatchCore with `resnet50` achieved the strongest result, with an image AUROC of 0.9936 and an image F1-score of 0.9818. On hazelnut, PatchCore with `resnet50` and `wide_resnet50_2` both achieved an image AUROC of 1.0000 and an image F1-score of 0.9928.

Based on these results, PatchCore with `resnet50` was selected as the preferred image-level anomaly detection architecture for the dissertation pipeline. PaDiM remained an important comparative baseline and localisation reference, but it produced weaker image-level performance in the tested architecture comparison, particularly on hazelnut.

### Integrated bottle results

| Detector              | Accuracy | Precision | Recall | F1-score | Human review rate |
| --------------------- | -------: | --------: | -----: | -------: | ----------------: |
| Statistical original  |   0.5904 |    1.0000 | 0.4603 |   0.6304 |            0.5181 |
| Statistical tuned 0.7 |   0.8795 |    0.8955 | 0.9524 |   0.9231 |            0.7711 |
| PatchCore integrated  |   0.9880 |    1.0000 | 0.9841 |   0.9920 |            0.1928 |
| PaDiM integrated      |   0.9518 |    0.9538 | 0.9841 |   0.9688 |            0.6867 |

### Integrated hazelnut results

| Detector              | Accuracy | Precision | Recall | F1-score | Human review rate |
| --------------------- | -------: | --------: | -----: | -------: | ----------------: |
| Statistical original  |   0.4364 |    0.8333 | 0.1429 |   0.2439 |            0.2273 |
| Statistical tuned 0.7 |   0.5545 |    0.6567 | 0.6286 |   0.6423 |            0.7636 |
| PatchCore integrated  |   0.9909 |    1.0000 | 0.9857 |   0.9928 |            0.1727 |
| PaDiM integrated      |   0.7182 |    0.6970 | 0.9857 |   0.8166 |            0.9000 |

### Current interpretation

PatchCore currently gives the strongest overall image-level performance across the tested bottle and hazelnut categories. It achieves high recall, no false positives in the reported runs, and a comparatively low human-review rate. PaDiM performs strongly on bottle, but it produces more false positives on hazelnut, which increases the human-review workload.

These findings indicate that detector choice affects not only classification performance, but also downstream risk-aware decision support and review efficiency.

Detailed experiment notes are stored in `docs/experiments/`.

### Capsule semantic fallback update

A semantic fallback rule was added for the capsule category to reduce unnecessary unknown labels. This did not change the detector-level classification metrics, but it reduced the review workload.

| Detector          | F1-score | Human review rate before | Human review rate after |
| ----------------- | -------: | -----------------------: | ----------------------: |
| PatchCore capsule |   0.9815 |                   0.6818 |                  0.5152 |
| PaDiM capsule     |   0.9432 |                   0.8712 |                  0.8409 |

This shows that the risk-aware pipeline can be improved at the semantic and governance layer without retraining the anomaly detector.

### Localisation evaluation

A localisation evaluation script was added to compare predicted anomaly masks against MVTec AD ground-truth masks using IoU and Dice coefficient.

| Category | Model     | Mean IoU | Mean Dice | Median IoU | Median Dice |
| -------- | --------- | -------: | --------: | ---------: | ----------: |
| bottle   | PatchCore |   0.3472 |    0.4928 |     0.3480 |      0.5164 |
| bottle   | PaDiM     |   0.4968 |    0.6442 |     0.4930 |      0.6604 |
| hazelnut | PatchCore |   0.1456 |    0.2316 |     0.1070 |      0.1933 |
| hazelnut | PaDiM     |   0.3084 |    0.4444 |     0.3168 |      0.4811 |
| capsule  | PatchCore |   0.1068 |    0.1671 |     0.0450 |      0.0862 |
| capsule  | PaDiM     |   0.1731 |    0.2673 |     0.1365 |      0.2403 |

The localisation results show that PaDiM produced stronger default mask alignment across the tested categories, while PatchCore remained stronger for image-level detection and operational review efficiency. This highlights a trade-off between anomaly classification performance and pixel-level localisation quality.

### Capsule localisation threshold sweep

A localisation threshold sweep was added for the capsule category to test whether anomaly-map post-processing could improve IoU and Dice without retraining the detector.

| Model             | Original mean IoU | Tuned mean IoU | Original mean Dice | Tuned mean Dice | Best threshold |
| ----------------- | ----------------: | -------------: | -----------------: | --------------: | -------------: |
| PatchCore capsule |            0.1068 |         0.2979 |             0.1671 |          0.4311 |           0.85 |
| PaDiM capsule     |            0.1731 |         0.1830 |             0.2673 |          0.2751 |           0.55 |

The result shows that PatchCore capsule localisation improved substantially after threshold tuning, while PaDiM improved only slightly. This suggests that PatchCore anomaly maps contained useful localisation information, but the original binary mask conversion was not optimal.

### Bottle and hazelnut localisation threshold sweep

Threshold sweeps were also completed for bottle and hazelnut to compare how different detector outputs respond to localisation post-processing.

| Category | Model     | Best threshold | Mean IoU | Mean Dice | Median IoU | Median Dice |
| -------- | --------- | -------------: | -------: | --------: | ---------: | ----------: |
| bottle   | PatchCore |           0.70 |   0.5929 |    0.7322 |     0.5916 |      0.7434 |
| bottle   | PaDiM     |           0.35 |   0.5110 |    0.6612 |     0.4990 |      0.6658 |
| hazelnut | PatchCore |           0.80 |   0.4331 |    0.5854 |     0.4232 |      0.5947 |
| hazelnut | PaDiM     |           0.50 |   0.3340 |    0.4693 |     0.3225 |      0.4877 |

After threshold tuning, PatchCore achieved stronger localisation performance on both bottle and hazelnut. This supports the interpretation that PatchCore can provide useful localisation evidence when the anomaly-map threshold is selected appropriately.

## API and dashboard demonstration

The FastAPI backend exposes routes for health checking, record listing, record lookup, review creation, summary reporting and QA decision support. The NiceGUI dashboard connects to the same audit database and provides an operator-facing interface.

The dashboard supports:

* database summary by category and detector;
* inspection-record filtering;
* selected-record loading;
* QA release decision display;
* latest operator review display;
* operator decision submission;
* review-based release after false-positive confirmation.

This provides a practical demonstration of the proposed human-in-the-loop inspection workflow.
