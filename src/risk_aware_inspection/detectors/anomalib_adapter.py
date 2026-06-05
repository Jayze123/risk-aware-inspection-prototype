from __future__ import annotations

from pathlib import Path

import numpy as np

from risk_aware_inspection.detectors.base import AnomalyDetector
from risk_aware_inspection.models import DetectionResult


class AnomalibDetectorAdapter(AnomalyDetector):
    """Adapter placeholder for PaDiM/PatchCore experiments through anomalib.

    The dissertation proposal specifies PaDiM and PatchCore as the main experimental baselines.
    Their exact training and inference calls depend on the installed anomalib version and the
    experiment configuration. This adapter deliberately keeps the pipeline contract stable while the
    concrete anomalib integration is added later.

    Expected integration behaviour:
    - load an exported anomalib model or checkpoint;
    - run inference on a preprocessed image;
    - return image-level score, pixel-level anomaly map, calibrated threshold and confidence;
    - keep all downstream localisation, semantic labelling, RPM and human-review logic unchanged.
    """

    def __init__(self, model_name: str, checkpoint_path: str | Path, threshold: float):
        self.model_name = model_name
        self.checkpoint_path = Path(checkpoint_path)
        self.threshold = float(threshold)
        raise NotImplementedError(
            "AnomalibDetectorAdapter is an interface stub. Use StatisticalReferenceDetector for the "
            "runnable MVP, then implement this adapter after selecting the anomalib version and "
            "exported PaDiM/PatchCore checkpoint format."
        )

    def predict(self, image_bgr: np.ndarray) -> tuple[DetectionResult, np.ndarray]:
        raise NotImplementedError
