from __future__ import annotations

from pathlib import Path
import numpy as np

from risk_aware_inspection.confidence import fuse_confidences
from risk_aware_inspection.detectors.base import AnomalyDetector
from risk_aware_inspection.gating import decide_review
from risk_aware_inspection.ingestion import load_image_bgr, preprocess_image
from risk_aware_inspection.localisation import localise_anomalies
from risk_aware_inspection.models import (
    PipelineRecord,
    SemanticResult,
    RiskResult,
    LocalisationResult,
)
from risk_aware_inspection.outputs import append_jsonl, save_visual_artefacts
from risk_aware_inspection.risk import RiskPriorityMatrix
from risk_aware_inspection.semantics import SemanticLabeler
from risk_aware_inspection.utils import sha256_file


class RiskAwareInspectionPipeline:
    """End-to-end prototype pipeline matching the dissertation architecture.

    Sequence: image ingestion -> anomaly detection -> localisation -> constrained semantic label ->
    deterministic RPM -> confidence fusion -> human-review gating -> traceable output.
    """

    def __init__(
        self,
        *,
        config: dict,
        detector: AnomalyDetector,
        semantic_labeler: SemanticLabeler,
        output_dir: str | Path,
    ):
        self.config = config
        self.detector = detector
        self.semantic_labeler = semantic_labeler
        self.output_dir = Path(output_dir)
        self.risk_engine = RiskPriorityMatrix(config)

    def process_image(self, image_path: str | Path) -> PipelineRecord:
        image_path = Path(image_path)
        raw_image = load_image_bgr(image_path)
        image = preprocess_image(raw_image, self.config["image"])

        detection, heatmap = self.detector.predict(image)

        if detection.is_anomalous:
            localisation, mask = localise_anomalies(heatmap, self.config["localisation"])
        else:
            localisation = LocalisationResult(
                boxes=[],
                confidence=detection.confidence,
                mask_area_ratio=0.0,
                component_count=0,
            )
            mask = np.zeros_like(heatmap, dtype="uint8")

        # If the calibrated detector classifies the image as normal, the semantic stage is not asked to
        # invent a defect label. This preserves the proposal's constrained-taxonomy principle while still
        # representing non-defective products explicitly in the audit record.
        if detection.is_anomalous:
            semantic = self.semantic_labeler.label(image, localisation.boxes, heatmap)
        else:
            semantic = SemanticResult(
                label=self.config["taxonomy"].get("normal_label", "normal"),
                confidence=detection.confidence,
                method="detector_normal_decision",
                evidence={"reason": "Image-level anomaly score did not exceed the calibrated threshold."},
            )

        component_confidences = {
            "anomaly": detection.confidence,
            "localisation": localisation.confidence if detection.is_anomalous else detection.confidence,
            "semantic": semantic.confidence,
        }
        fusion = fuse_confidences(component_confidences, self.config["confidence_fusion"])
        fused_preferred = float(fusion["preferred"])

        if detection.is_anomalous:
            risk = self.risk_engine.evaluate(
                label=semantic.label,
                boxes=localisation.boxes,
                fused_confidence=fused_preferred,
            )
        else:
            risk = RiskResult(
                severity="S1",
                occurrence="O1",
                detection="D1",
                risk_class="Low",
                action=self.config["actions"].get("Low", "Continue monitoring."),
                mapped=True,
                rpm_lookup_key="S1|O1|D1",
            )
        review = decide_review(
            detection=detection,
            localisation=localisation,
            semantic=semantic,
            risk=risk,
            fused_confidence=fused_preferred,
            cfg=self.config["gating"],
        )

        safe_parts = [
            part.replace(" ", "_").replace("-", "_")
            for part in image_path.with_suffix("").parts[-4:]
        ]
        image_id = "__".join(safe_parts)
        artefacts = save_visual_artefacts(
            image_bgr=image,
            heatmap=heatmap,
            mask=mask,
            localisation=localisation,
            image_id=image_id,
            output_dir=self.output_dir,
        )

        record = PipelineRecord.create(
            image_id=image_id,
            image_path=str(image_path),
            image_sha256=sha256_file(image_path),
            detection=detection,
            localisation=localisation,
            semantic=semantic,
            confidence={
                "components": component_confidences,
                "fusion": fusion,
            },
            risk=risk,
            review=review,
            artefacts=artefacts,
            config_summary={
                "detector": self.config["detector"].get("name", "unknown"),
                "localisation_threshold": self.config["localisation"].get("heatmap_threshold"),
                "fusion_preferred_strategy": self.config["confidence_fusion"].get("preferred_strategy"),
            },
        )
        append_jsonl(record, self.output_dir)
        return record
