from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import cv2
import numpy as np

from risk_aware_inspection.models import BoundingBox, SemanticResult
from risk_aware_inspection.utils import clamp


class SemanticLabeler(ABC):
    """Interface for constrained semantic interpretation."""

    @abstractmethod
    def label(
        self,
        image_bgr: np.ndarray,
        boxes: list[BoundingBox],
        heatmap: np.ndarray,
    ) -> SemanticResult:
        """Return one label from the allowed defect taxonomy."""


class RuleBasedSemanticLabeler(SemanticLabeler):
    """Constrained fallback semantic labeller.

    It never invents a free-text defect category. It applies interpretable geometric and colour rules
    to the most important localisation region and maps the result to the configured taxonomy.
    """

    def __init__(self, taxonomy_cfg: dict[str, Any], rule_cfg: dict[str, Any]):
        self.allowed_labels = set(taxonomy_cfg.get("allowed_labels", []))
        self.unknown_label = taxonomy_cfg.get("unknown_label", "unknown")
        self.rule_cfg = rule_cfg

    def _safe_label(self, label: str) -> str:
        return label if label in self.allowed_labels else self.unknown_label

    def label(
        self,
        image_bgr: np.ndarray,
        boxes: list[BoundingBox],
        heatmap: np.ndarray,
    ) -> SemanticResult:
        if not boxes:
            return SemanticResult(
                label=self.unknown_label,
                confidence=0.0,
                method="rules_no_localisation",
                evidence={"reason": "No localised anomalous region was available."},
            )

        box = boxes[0]
        crop = image_bgr[box.y : box.y2, box.x : box.x2]
        if crop.size == 0:
            return SemanticResult(
                label=self.unknown_label,
                confidence=0.0,
                method="rules_empty_crop",
                evidence={"reason": "The selected bounding box produced an empty crop."},
            )

        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        edges = cv2.Canny(gray, 60, 140)
        edge_density = float(np.count_nonzero(edges) / max(1, edges.size))
        mean_saturation = float(hsv[..., 1].mean())
        mean_value = float(hsv[..., 2].mean())

        # Estimate contrast against a small padded neighbourhood in the original image.
        pad = 8
        y1 = max(0, box.y - pad)
        y2 = min(image_bgr.shape[0], box.y2 + pad)
        x1 = max(0, box.x - pad)
        x2 = min(image_bgr.shape[1], box.x2 + pad)
        neighbourhood = image_bgr[y1:y2, x1:x2]
        neighbour_hsv = cv2.cvtColor(neighbourhood, cv2.COLOR_BGR2HSV)
        neighbour_sat = float(neighbour_hsv[..., 1].mean())
        neighbour_value = float(neighbour_hsv[..., 2].mean())
        saturation_contrast = abs(mean_saturation - neighbour_sat)
        dark_contrast = max(0.0, neighbour_value - mean_value)

        elongated = box.aspect_ratio >= float(self.rule_cfg.get("elongated_aspect_ratio", 3.2))
        thin_region = box.area_ratio <= float(self.rule_cfg.get("thin_area_ratio_max", 0.025))
        dark = dark_contrast >= float(self.rule_cfg.get("dark_contrast_threshold", 18.0))
        saturated = saturation_contrast >= float(self.rule_cfg.get("saturation_contrast_threshold", 20.0))
        large = box.area_ratio >= float(self.rule_cfg.get("large_region_ratio", 0.08))
        edge_rich = edge_density >= float(self.rule_cfg.get("edge_density_threshold", 0.06))

        label = self.unknown_label
        rule_strength = 0.0
        evidence_rules: list[str] = []


        if elongated and thin_region and edge_rich and dark:
            label = "crack"
            rule_strength = 0.92
            evidence_rules.append("elongated_thin_dark_edge_rich_crack_like")
        elif elongated and thin_region:
            label = "scratch"
            rule_strength = 0.78 + 0.10 * float(edge_rich)
            evidence_rules.append("elongated_thin_region")
        elif edge_rich and dark:
            label = "crack"
            rule_strength = 0.74 + 0.08 * float(elongated) + 0.08 * float(thin_region)
            evidence_rules.append("dark_edge_rich_crack_like_region")
        elif saturated:
            label = "contamination"
            rule_strength = 0.74 + clamp(saturation_contrast / 80.0) * 0.18
            evidence_rules.append("colour_or_saturation_shift")
        elif large and not edge_rich:
            label = "stain"
            rule_strength = 0.70
            evidence_rules.append("large_low_edge_region")
        elif dark and not elongated:
            label = "dent"
            rule_strength = 0.68 + clamp(dark_contrast / 100.0) * 0.20
            evidence_rules.append("local_dark_depression_like_region")
        elif large and edge_rich:
            label = "deformation"
            rule_strength = 0.66
            evidence_rules.append("large_irregular_edge_region")
        else:
            if box.max_heat >= 0.90 and box.area_ratio >= 0.02:
                label = "surface_defect"
                rule_strength = 0.62
                evidence_rules.append("high_heat_moderate_area_surface_defect_fallback")
            else:
                label = self.unknown_label
                rule_strength = float(self.rule_cfg.get("minimum_semantic_confidence", 0.35))
                evidence_rules.append("no_rule_matched_confidently")

        label = self._safe_label(label)
        confidence = clamp(0.65 * rule_strength + 0.35 * box.max_heat)
        return SemanticResult(
            label=label,
            confidence=confidence,
            method="rules_constrained_taxonomy",
            evidence={
                "selected_box": box.to_dict(),
                "edge_density": edge_density,
                "mean_saturation": mean_saturation,
                "mean_value": mean_value,
                "saturation_contrast": saturation_contrast,
                "dark_contrast": dark_contrast,
                "rules": evidence_rules,
            },
        )


class VisionLanguageSemanticLabeler(SemanticLabeler):
    """Interface stub for a future Hugging Face vision-language implementation.

    A production or dissertation experiment can implement this class to query a VLM, but the output
    must still be forced into the same allowed taxonomy and must expose confidence/evidence.
    """

    def __init__(self, allowed_labels: list[str]):
        self.allowed_labels = allowed_labels
        raise NotImplementedError(
            "VisionLanguageSemanticLabeler is intentionally left as an interface. The current MVP uses "
            "RuleBasedSemanticLabeler so that the pipeline remains deterministic and runnable in VS Code."
        )

    def label(self, image_bgr: np.ndarray, boxes: list[BoundingBox], heatmap: np.ndarray) -> SemanticResult:
        raise NotImplementedError
