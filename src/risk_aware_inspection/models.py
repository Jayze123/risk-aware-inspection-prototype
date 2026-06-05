from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class BoundingBox:
    x: int
    y: int
    w: int
    h: int
    area_px: int
    area_ratio: float
    mean_heat: float
    max_heat: float

    @property
    def x2(self) -> int:
        return self.x + self.w

    @property
    def y2(self) -> int:
        return self.y + self.h

    @property
    def aspect_ratio(self) -> float:
        return max(self.w, self.h) / max(1, min(self.w, self.h))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["x2"] = self.x2
        data["y2"] = self.y2
        data["aspect_ratio"] = self.aspect_ratio
        return data


@dataclass
class DetectionResult:
    detector_name: str
    image_score: float
    threshold: float
    is_anomalous: bool
    confidence: float
    score_margin: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LocalisationResult:
    boxes: list[BoundingBox]
    confidence: float
    mask_area_ratio: float
    component_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "confidence": self.confidence,
            "mask_area_ratio": self.mask_area_ratio,
            "component_count": self.component_count,
            "boxes": [box.to_dict() for box in self.boxes],
        }


@dataclass
class SemanticResult:
    label: str
    confidence: float
    method: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RiskResult:
    severity: str
    occurrence: str
    detection: str
    risk_class: str
    action: str
    mapped: bool
    rpm_lookup_key: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReviewDecision:
    requires_review: bool
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineRecord:
    image_id: str
    image_path: str
    image_sha256: str
    created_utc: str
    detection: dict[str, Any]
    localisation: dict[str, Any]
    semantic: dict[str, Any]
    confidence: dict[str, Any]
    risk: dict[str, Any]
    review: dict[str, Any]
    artefacts: dict[str, str]
    config_summary: dict[str, Any]

    @classmethod
    def create(
        cls,
        *,
        image_id: str,
        image_path: str,
        image_sha256: str,
        detection: DetectionResult,
        localisation: LocalisationResult,
        semantic: SemanticResult,
        confidence: dict[str, Any],
        risk: RiskResult,
        review: ReviewDecision,
        artefacts: dict[str, str],
        config_summary: dict[str, Any],
    ) -> "PipelineRecord":
        return cls(
            image_id=image_id,
            image_path=image_path,
            image_sha256=image_sha256,
            created_utc=datetime.now(timezone.utc).isoformat(),
            detection=detection.to_dict(),
            localisation=localisation.to_dict(),
            semantic=semantic.to_dict(),
            confidence=confidence,
            risk=risk.to_dict(),
            review=review.to_dict(),
            artefacts=artefacts,
            config_summary=config_summary,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
