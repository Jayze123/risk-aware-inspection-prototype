from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import yaml

from risk_aware_inspection.models import DetectionResult
from risk_aware_inspection.pipeline import RiskAwareInspectionPipeline
from risk_aware_inspection.outputs import save_batch_csv
from risk_aware_inspection.semantics import RuleBasedSemanticLabeler


def parse_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalise_path(path: str | Path) -> str:
    return str(Path(path).resolve())


def load_heatmap(path: str | Path) -> np.ndarray:
    heatmap = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)

    if heatmap is None:
        raise FileNotFoundError(f"Could not read anomaly map: {path}")

    return heatmap.astype("float32") / 255.0


class ExportedAnomalibDetector:
    """
    Adapter that makes exported Anomalib predictions look like the detector
    interface expected by the risk-aware inspection pipeline.
    """

    def __init__(
        self,
        prediction_rows: list[dict],
        detector_name: str,
        reporting_threshold: float = 0.5,
    ) -> None:
        self.detector_name = detector_name
        self.threshold = reporting_threshold
        self.current_image_path: str | None = None

        self.records_by_path = {
            normalise_path(row["image_path"]): row for row in prediction_rows
        }

        scores = [float(row["pred_score"]) for row in prediction_rows]
        self.min_score = min(scores)
        self.max_score = max(scores)

    def set_current_image(self, image_path: str | Path) -> None:
        self.current_image_path = normalise_path(image_path)

    def _normalised_score(self, score: float) -> float:
        denominator = self.max_score - self.min_score

        if denominator < 1e-8:
            return 0.5

        return float((score - self.min_score) / denominator)

    def predict(self, image: np.ndarray):
        if self.current_image_path is None:
            raise RuntimeError("Current image path has not been set.")

        if self.current_image_path not in self.records_by_path:
            raise KeyError(f"No exported Anomalib prediction found for {self.current_image_path}")

        row = self.records_by_path[self.current_image_path]

        raw_score = float(row["pred_score"])
        is_anomalous = parse_bool(row["pred_label"])
        normalised_score = self._normalised_score(raw_score)

        confidence = normalised_score if is_anomalous else 1.0 - normalised_score
        confidence = max(0.0, min(1.0, confidence))

        heatmap = load_heatmap(row["anomaly_map_path"])

        score_margin = abs(normalised_score - self.threshold)

        detection = DetectionResult(
            detector_name=self.detector_name,
            image_score=normalised_score,
            threshold=self.threshold,
            is_anomalous=is_anomalous,
            confidence=confidence,
            score_margin=score_margin,
        )

        return detection, heatmap


def read_predictions(predictions_csv: Path) -> list[dict]:
    with predictions_csv.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def run_pipeline_from_export(
    predictions_csv: Path,
    config_path: Path,
    output_dir: Path,
    reporting_threshold: float,
) -> None:
    rows = read_predictions(predictions_csv)

    if not rows:
        raise ValueError(f"No prediction rows found in {predictions_csv}")

    config = load_config(config_path)

    model_name = rows[0].get("model", "anomalib")
    detector = ExportedAnomalibDetector(
        prediction_rows=rows,
        detector_name=f"anomalib_{model_name}",
        reporting_threshold=reporting_threshold,
    )

    labeler = RuleBasedSemanticLabeler(
        config["taxonomy"],
        config["semantic_rules"],
    )

    pipeline = RiskAwareInspectionPipeline(
        config=config,
        detector=detector,
        semantic_labeler=labeler,
        output_dir=output_dir,
    )

    records = []

    for row in rows:
        image_path = Path(row["image_path"])
        detector.set_current_image(image_path)
        record = pipeline.process_image(image_path)
        records.append(record)

    csv_path = save_batch_csv(records, output_dir)

    print("Risk-aware pipeline completed from Anomalib export.")
    print(f"Input predictions: {predictions_csv}")
    print(f"Output directory: {output_dir}")
    print(f"Saved {len(records)} records to {csv_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the risk-aware pipeline using exported Anomalib predictions."
    )

    parser.add_argument(
        "--predictions",
        required=True,
        type=Path,
        help="Path to exported Anomalib predictions.csv.",
    )

    parser.add_argument(
        "--config",
        default=Path("config/pipeline.yaml"),
        type=Path,
        help="Path to the risk-aware pipeline YAML configuration.",
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output directory for risk-aware results.",
    )

    parser.add_argument(
        "--reporting-threshold",
        type=float,
        default=0.5,
        help="Threshold value stored in audit outputs. The binary decision comes from Anomalib pred_label.",
    )

    args = parser.parse_args()

    run_pipeline_from_export(
        predictions_csv=args.predictions,
        config_path=args.config,
        output_dir=args.output,
        reporting_threshold=args.reporting_threshold,
    )


if __name__ == "__main__":
    main()