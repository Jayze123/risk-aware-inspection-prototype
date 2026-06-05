from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from risk_aware_inspection.detectors.base import AnomalyDetector
from risk_aware_inspection.ingestion import iter_image_paths, load_image_bgr, preprocess_image, to_grayscale_float
from risk_aware_inspection.models import DetectionResult
from risk_aware_inspection.utils import clamp


class StatisticalReferenceDetector(AnomalyDetector):
    """A lightweight normal-reference detector used as the immediate MVP baseline.

    This is not a replacement for PaDiM or PatchCore. It is an executable abstraction that preserves
    the same output contract: image-level anomaly score, pixel-level heatmap, threshold, and confidence.
    It learns mean and standard deviation images from normal references and scores deviations as a
    clipped z-score residual map.
    """

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.mean_image: np.ndarray | None = None
        self.std_image: np.ndarray | None = None
        self.threshold: float = float(cfg.get("minimum_threshold", 0.18))
        self.detector_name = "simple_statistical_reference"

    def fit_from_directory(self, normal_dir: str | Path, image_cfg: dict) -> None:
        images = []
        for path in iter_image_paths(normal_dir):
            image = preprocess_image(load_image_bgr(path), image_cfg)
            gray = to_grayscale_float(image)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            images.append(gray)

        if len(images) < 3:
            raise ValueError("At least three normal reference images are recommended for calibration.")

        stack = np.stack(images, axis=0)
        self.mean_image = stack.mean(axis=0).astype(np.float32)
        self.std_image = np.maximum(stack.std(axis=0).astype(np.float32), 0.015)

        normal_scores = [self._score_heatmap(self._heatmap_from_gray(img)) for img in images]
        quantile = float(self.cfg.get("calibration_quantile", 0.995))
        calibrated = float(np.quantile(normal_scores, quantile))
        self.threshold = max(float(self.cfg.get("minimum_threshold", 0.18)), calibrated)

    def _heatmap_from_gray(self, gray: np.ndarray) -> np.ndarray:
        if self.mean_image is None or self.std_image is None:
            raise RuntimeError("Detector has not been calibrated or loaded. Run the calibrate command first.")
        residual = np.abs(gray - self.mean_image) / self.std_image
        z_clip = float(self.cfg.get("zscore_clip", 5.0))
        heatmap = np.clip(residual / z_clip, 0.0, 1.0)
        return heatmap.astype(np.float32)

    def _score_heatmap(self, heatmap: np.ndarray) -> float:
        percentile = float(self.cfg.get("top_percentile", 99.0))
        cutoff = np.percentile(heatmap, percentile)
        upper_tail = heatmap[heatmap >= cutoff]
        if upper_tail.size == 0:
            return float(heatmap.max())
        return float(upper_tail.mean())

    def predict(self, image_bgr: np.ndarray) -> tuple[DetectionResult, np.ndarray]:
        gray = to_grayscale_float(image_bgr)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        heatmap = self._heatmap_from_gray(gray)
        score = self._score_heatmap(heatmap)
        margin = abs(score - self.threshold)
        decision_margin = float(self.cfg.get("decision_margin", 0.08))
        is_anomalous = score >= self.threshold
        confidence = clamp(0.5 + margin / max(decision_margin, 1e-6) * 0.5)
        result = DetectionResult(
            detector_name=self.detector_name,
            image_score=score,
            threshold=self.threshold,
            is_anomalous=is_anomalous,
            confidence=confidence,
            score_margin=margin,
        )
        return result, heatmap

    def save(self, path: str | Path) -> None:
        if self.mean_image is None or self.std_image is None:
            raise RuntimeError("Cannot save an uncalibrated detector.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            path,
            mean_image=self.mean_image,
            std_image=self.std_image,
            threshold=np.array([self.threshold], dtype=np.float32),
        )

    @classmethod
    def load(cls, path: str | Path, cfg: dict) -> "StatisticalReferenceDetector":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Detector model file not found: {path}")
        data = np.load(path)
        detector = cls(cfg)
        detector.mean_image = data["mean_image"].astype(np.float32)
        detector.std_image = data["std_image"].astype(np.float32)
        detector.threshold = float(data["threshold"][0])
        return detector
