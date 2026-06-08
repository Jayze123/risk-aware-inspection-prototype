# Anomalib PatchCore Bottle Experiment

## Purpose

This experiment tested PatchCore on the MVTec AD bottle category using Anomalib and the Folder datamodule. The aim was to move beyond the initial simple statistical detector and confirm that a stronger industrial anomaly detection baseline could be trained and evaluated successfully.

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

PatchCore completed successfully on CPU.

- Image AUROC: 1.0000
- Image F1-score: approximately 0.9920

## Interpretation

The PatchCore result is substantially stronger than the simple statistical detector. The tuned statistical baseline achieved an F1-score of 0.9231 on the bottle category, while PatchCore achieved approximately 0.9920. This supports the dissertation direction of using stronger anomaly detection methods such as PatchCore and PaDiM before integrating the outputs into the risk-aware governance pipeline.
