# Risk-Aware Inspection Prototype Progress Log

## Current milestone

This repository now contains a working prototype of a risk-aware visual inspection pipeline for MSc dissertation development.

The implemented pipeline includes:

- image ingestion and preprocessing
- anomaly scoring using a simple statistical baseline detector
- heatmap generation
- localisation using masks and connected components
- constrained semantic labelling
- deterministic risk-priority lookup
- confidence fusion
- human-review gating
- JSON/CSV audit outputs
- threshold override support
- Anomalib PatchCore experiment support through the Folder datamodule

## MVTec AD categories tested

### Bottle baseline

Original threshold:

- TP: 29
- TN: 20
- FP: 0
- FN: 34
- Accuracy: 0.5904
- Precision: 1.0000
- Recall: 0.4603
- F1-score: 0.6304
- Human review rate: 0.5181

Tuned threshold multiplier 0.7:

- TP: 60
- TN: 13
- FP: 7
- FN: 3
- Accuracy: 0.8795
- Precision: 0.8955
- Recall: 0.9524
- F1-score: 0.9231
- Human review rate: 0.7711

### Hazelnut baseline

Original threshold:

- TP: 10
- TN: 38
- FP: 2
- FN: 60
- Accuracy: 0.4364
- Precision: 0.8333
- Recall: 0.1429
- F1-score: 0.2439
- Human review rate: 0.2273

Tuned threshold multiplier 0.7:

- TP: 44
- TN: 17
- FP: 23
- FN: 26
- Accuracy: 0.5545
- Precision: 0.6567
- Recall: 0.6286
- F1-score: 0.6423
- Human review rate: 0.7636

## PatchCore result

PatchCore was successfully run on the MVTec bottle category using Anomalib 2.5.0 with the Folder datamodule.

- Image AUROC: 1.0000
- Image F1-score: approximately 0.9920
- Torch version: 2.8.0+cpu
- CUDA available: False

## Interpretation

The simple statistical detector validates the end-to-end risk-aware pipeline but shows category-dependent limitations. Threshold tuning improves recall and F1-score, especially for bottle, but also increases false positives and human-review workload. PatchCore provides much stronger image-level anomaly detection performance and supports the planned move toward PaDiM/PatchCore-based dissertation experiments.
