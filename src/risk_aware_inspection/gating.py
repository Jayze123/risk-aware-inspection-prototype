from __future__ import annotations

from risk_aware_inspection.models import DetectionResult, LocalisationResult, ReviewDecision, RiskResult, SemanticResult


def decide_review(
    *,
    detection: DetectionResult,
    localisation: LocalisationResult,
    semantic: SemanticResult,
    risk: RiskResult,
    fused_confidence: float,
    cfg: dict,
) -> ReviewDecision:
    """Apply human-review escalation rules for uncertainty, contradiction and unmapped risk cases."""
    reasons: list[str] = []

    if fused_confidence < float(cfg.get("minimum_fused_confidence", 0.60)):
        reasons.append(
            f"Fused confidence {fused_confidence:.3f} is below operational threshold "
            f"{float(cfg.get('minimum_fused_confidence', 0.60)):.3f}."
        )

    if cfg.get("force_review_for_unknown_label", True) and semantic.label == "unknown":
        reasons.append("Semantic label is unknown or not confidently mapped to the taxonomy.")

    if cfg.get("force_review_for_unmapped_rpm", True) and not risk.mapped:
        reasons.append(f"RPM lookup tuple {risk.rpm_lookup_key} is not mapped in the explicit table.")

    if (
        cfg.get("force_review_when_no_localisation_for_anomaly", True)
        and detection.is_anomalous
        and localisation.component_count == 0
    ):
        reasons.append("Image-level anomaly was detected but no stable localised region was extracted.")

    near_margin = float(cfg.get("near_boundary_margin", 0.07))
    if detection.score_margin <= near_margin:
        reasons.append(
            f"Anomaly score is close to the decision boundary; margin={detection.score_margin:.3f}."
        )

    if detection.is_anomalous and semantic.label == "normal":
        reasons.append("Contradiction: detector marked anomaly but semantic stage returned normal.")

    if risk.risk_class == "Critical":
        reasons.append("Critical risk class requires operator confirmation before release decision.")

    return ReviewDecision(requires_review=bool(reasons), reasons=reasons)
