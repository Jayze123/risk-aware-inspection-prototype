from __future__ import annotations

from typing import Any

from risk_aware_inspection.models import BoundingBox, RiskResult


SEVERITY_ORDER = {"S1": 1, "S2": 2, "S3": 3, "S4": 4}
SEVERITY_BY_SCORE = {v: k for k, v in SEVERITY_ORDER.items()}


class RiskPriorityMatrix:
    """Deterministic RPM lookup engine.

    The engine does not infer missing risk values. If a tuple is absent from the configured matrix,
    the output is Review Required so that the table can be audited or extended by a domain expert.
    """

    def __init__(self, cfg: dict[str, Any]):
        self.cfg = cfg
        self.actions = cfg["actions"]
        self.table: dict[tuple[str, str, str], str] = {}
        for row in cfg.get("rpm_table", []):
            key = (str(row["severity"]), str(row["occurrence"]), str(row["detection"]))
            self.table[key] = str(row["risk_class"])

    def _severity_from_label_and_area(self, label: str, boxes: list[BoundingBox]) -> str:
        risk_inputs = self.cfg["risk_inputs"]
        base = risk_inputs.get("severity_by_label", {}).get(label, "S3")
        max_area_ratio = max([b.area_ratio for b in boxes], default=0.0)
        base_score = SEVERITY_ORDER.get(base, 3)
        for rule in risk_inputs.get("area_escalation", []):
            if max_area_ratio >= float(rule.get("min_area_ratio", 1.0)):
                min_level = rule.get("minimum_severity", base)
                base_score = max(base_score, SEVERITY_ORDER.get(min_level, base_score))
        return SEVERITY_BY_SCORE.get(base_score, "S3")

    def _occurrence_from_label(self, label: str) -> str:
        return self.cfg["risk_inputs"].get("occurrence_prior_by_label", {}).get(label, "O3")

    def _detection_from_confidence(self, fused_confidence: float) -> str:
        bins = self.cfg["risk_inputs"].get("detection_level_by_confidence", [])
        for row in sorted(bins, key=lambda r: float(r.get("min_confidence", 0.0)), reverse=True):
            if fused_confidence >= float(row.get("min_confidence", 0.0)):
                return str(row.get("level", "D3"))
        return "D3"

    def evaluate(self, *, label: str, boxes: list[BoundingBox], fused_confidence: float) -> RiskResult:
        severity = self._severity_from_label_and_area(label, boxes)
        occurrence = self._occurrence_from_label(label)
        detection = self._detection_from_confidence(fused_confidence)
        key = (severity, occurrence, detection)
        rpm_lookup_key = "|".join(key)
        risk_class = self.table.get(key)
        mapped = risk_class is not None
        if risk_class is None:
            risk_class = "Review Required"
        action = self.actions.get(risk_class, self.actions.get("Review Required", "Escalate to human review."))
        return RiskResult(
            severity=severity,
            occurrence=occurrence,
            detection=detection,
            risk_class=risk_class,
            action=action,
            mapped=mapped,
            rpm_lookup_key=rpm_lookup_key,
        )
