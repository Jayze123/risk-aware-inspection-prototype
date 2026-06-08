# Anomalib PaDiM Bottle Experiment

## Purpose

This experiment tested PaDiM on the MVTec AD bottle category using Anomalib and the Folder datamodule. The purpose was to compare PaDiM with the earlier statistical baseline and the PatchCore experiment.

## Environment

- Anomalib version: 2.5.0
- Torch version: 2.8.0+cpu
- CUDA available: False
- Datamodule: Anomalib Folder
- Dataset category: MVTec AD bottle

## Dataset structure used

- Normal training images: bottle/train/good
- Normal test images: bottle/test/good
- Abnormal test images:
  - bottle/test/broken_large
  - bottle/test/broken_small
  - bottle/test/contamination

## Result

PaDiM completed successfully on CPU.

- Image AUROC: 0.9937
- Image F1-score: 0.9688

## Interpretation

PaDiM achieved strong image-level anomaly detection performance on the bottle category. Its performance was lower than PatchCore in this experiment, but it still substantially outperformed the initial statistical detector. This supports the dissertation methodology of comparing multiple anomaly detection methods before integrating their outputs into the risk-aware inspection pipeline.
