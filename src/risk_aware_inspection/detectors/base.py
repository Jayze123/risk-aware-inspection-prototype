from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np

from risk_aware_inspection.models import DetectionResult


class AnomalyDetector(ABC):
    """Interface for anomaly detectors that return an image score and a pixel-level heatmap."""

    @abstractmethod
    def predict(self, image_bgr: np.ndarray) -> tuple[DetectionResult, np.ndarray]:
        """Return a detection result and a normalised heatmap in [0, 1]."""

    def fit_from_directory(self, normal_dir: str | Path, image_cfg: dict) -> None:
        """Optional calibration method for detectors that learn from normal images."""
        raise NotImplementedError(f"{self.__class__.__name__} does not implement calibration.")

    def save(self, path: str | Path) -> None:
        raise NotImplementedError(f"{self.__class__.__name__} does not implement save().")

    @classmethod
    def load(cls, path: str | Path, cfg: dict) -> "AnomalyDetector":
        raise NotImplementedError(f"{cls.__name__} does not implement load().")
