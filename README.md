# Risk-Aware Vision Pipeline Prototype

This repository is a VS Code-compatible research prototype for the MSc dissertation proposal titled
**Risk-Aware Vision Pipeline for Industrial Visual Inspection and Anomaly Detection**.

The project implements the proposal's minimum viable inspection workflow:

1. image ingestion and preprocessing;
2. anomaly detection through a swappable detector interface;
3. localisation through heatmap thresholding, morphology and connected components;
4. constrained semantic interpretation using a fixed defect taxonomy;
5. deterministic Risk Priority Matrix lookup;
6. confidence fusion using minimum and weighted-average strategies;
7. human-review gating;
8. JSONL, CSV and visual artefact output for auditability.

The runnable detector is a simple normal-reference statistical detector. It is included so that the
whole pipeline can be executed immediately in VS Code without GPU access. It is not intended to replace
PaDiM or PatchCore. The detector interface and `AnomalibDetectorAdapter` stub show where PaDiM and
PatchCore outputs should later be connected.

## Project structure

```text
risk_aware_inspection_prototype/
├── config/pipeline.yaml
├── src/risk_aware_inspection/
│   ├── cli.py
│   ├── pipeline.py
│   ├── ingestion.py
│   ├── localisation.py
│   ├── semantics.py
│   ├── risk.py
│   ├── confidence.py
│   ├── gating.py
│   ├── outputs.py
│   └── detectors/
│       ├── base.py
│       ├── simple_statistical.py
│       └── anomalib_adapter.py
├── tests/
├── requirements.txt
└── pyproject.toml
```

## Setup in VS Code

Open the project folder in VS Code and run the following in the terminal:

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate

pip install -e .
```

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

Place normal training/reference images in a folder, calibrate the detector on those images, then run
inspection on your test images. For MVTec AD-style work, use the official `train/good` folder as the
normal reference folder and run inference on `test/*` images.

## Replacing the MVP detector with PaDiM or PatchCore

The downstream pipeline expects any detector to return:

- image-level anomaly score;
- calibrated anomaly threshold;
- binary anomaly decision;
- anomaly confidence;
- pixel-level heatmap in `[0, 1]`.

When an anomalib PaDiM or PatchCore experiment has been trained and exported, implement the
`AnomalibDetectorAdapter.predict()` method so it converts anomalib outputs into this same contract.
No change should be required in localisation, semantic interpretation, RPM, gating or output logging.

## Research notes

The current prototype is designed for dissertation progress rather than production deployment. The
most important research-facing features are modularity, traceable outputs and deterministic risk
mapping. The semantic component is deliberately constrained to a fixed taxonomy, and missing RPM
lookups cause Review Required rather than inferred risk values.

## Current experiment results

The current prototype has been tested on two MVTec AD categories: bottle and hazelnut. The experiments compare the initial statistical detector, threshold-tuned statistical detection, PatchCore, and PaDiM after integration with the risk-aware inspection pipeline.

### Integrated bottle results

| Detector | Accuracy | Precision | Recall | F1-score | Human review rate |
|---|---:|---:|---:|---:|---:|
| Statistical original | 0.5904 | 1.0000 | 0.4603 | 0.6304 | 0.5181 |
| Statistical tuned 0.7 | 0.8795 | 0.8955 | 0.9524 | 0.9231 | 0.7711 |
| PatchCore integrated | 0.9880 | 1.0000 | 0.9841 | 0.9920 | 0.1928 |
| PaDiM integrated | 0.9518 | 0.9538 | 0.9841 | 0.9688 | 0.6867 |

### Integrated hazelnut results

| Detector | Accuracy | Precision | Recall | F1-score | Human review rate |
|---|---:|---:|---:|---:|---:|
| Statistical original | 0.4364 | 0.8333 | 0.1429 | 0.2439 | 0.2273 |
| Statistical tuned 0.7 | 0.5545 | 0.6567 | 0.6286 | 0.6423 | 0.7636 |
| PatchCore integrated | 0.9909 | 1.0000 | 0.9857 | 0.9928 | 0.1727 |
| PaDiM integrated | 0.7182 | 0.6970 | 0.9857 | 0.8166 | 0.9000 |

### Current interpretation

PatchCore currently gives the strongest overall performance across both tested categories. It achieves high recall, no false positives, and a low human-review rate. PaDiM performs strongly on ottle, but it produces many false positives on hazelnut, which increases the human-review workload. These findings support the dissertation argument that anomaly detector choice affects not only classification performance, but also downstream risk-aware decision support and review efficiency.

Detailed experiment notes are stored in docs/experiments/.

### Capsule semantic fallback update

A semantic fallback rule was added for the capsule category to reduce unnecessary unknown labels. This did not change the detector-level classification metrics, but it reduced the review workload.

| Detector | F1-score | Human review rate before | Human review rate after |
|---|---:|---:|---:|
| PatchCore capsule | 0.9815 | 0.6818 | 0.5152 |
| PaDiM capsule | 0.9432 | 0.8712 | 0.8409 |

This shows that the risk-aware pipeline can be improved at the semantic/governance layer without retraining the anomaly detector.

### Capsule semantic fallback update

A semantic fallback rule was added for the capsule category to reduce unnecessary unknown labels. This did not change the detector-level classification metrics, but it reduced the review workload.

| Detector | F1-score | Human review rate before | Human review rate after |
|---|---:|---:|---:|
| PatchCore capsule | 0.9815 | 0.6818 | 0.5152 |
| PaDiM capsule | 0.9432 | 0.8712 | 0.8409 |

This shows that the risk-aware pipeline can be improved at the semantic/governance layer without retraining the anomaly detector.

### Localisation evaluation

A localisation evaluation script was added to compare predicted anomaly masks against MVTec AD ground-truth masks using IoU and Dice coefficient.

| Category | Model | Mean IoU | Mean Dice | Median IoU | Median Dice |
|---|---|---:|---:|---:|---:|
| bottle | PatchCore | 0.3472 | 0.4928 | 0.3480 | 0.5164 |
| bottle | PaDiM | 0.4968 | 0.6442 | 0.4930 | 0.6604 |
| hazelnut | PatchCore | 0.1456 | 0.2316 | 0.1070 | 0.1933 |
| hazelnut | PaDiM | 0.3084 | 0.4444 | 0.3168 | 0.4811 |
| capsule | PatchCore | 0.1068 | 0.1671 | 0.0450 | 0.0862 |
| capsule | PaDiM | 0.1731 | 0.2673 | 0.1365 | 0.2403 |

The localisation results show that PaDiM produced stronger mask alignment across the tested categories, while PatchCore remained stronger for image-level detection and operational review efficiency. This highlights an important trade-off between anomaly classification performance and pixel-level localisation quality.

### Capsule localisation threshold sweep

A localisation threshold sweep was added for the capsule category to test whether anomaly-map post-processing could improve IoU and Dice without retraining the detector.

| Model | Original mean IoU | Tuned mean IoU | Original mean Dice | Tuned mean Dice | Best threshold |
|---|---:|---:|---:|---:|---:|
| PatchCore capsule | 0.1068 | 0.2979 | 0.1671 | 0.4311 | 0.85 |
| PaDiM capsule | 0.1731 | 0.1830 | 0.2673 | 0.2751 | 0.55 |

The result shows that PatchCore capsule localisation improved substantially after threshold tuning, while PaDiM improved only slightly. This suggests that PatchCore anomaly maps contained useful localisation information, but the original binary mask conversion was not optimal.
