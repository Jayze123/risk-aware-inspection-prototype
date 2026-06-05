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
