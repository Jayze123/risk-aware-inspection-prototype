from __future__ import annotations

from risk_aware_inspection.utils import clamp


def minimum_rule(confidences: dict[str, float]) -> float:
    """Conservative fusion: the weakest component controls the system confidence."""
    if not confidences:
        return 0.0
    return clamp(min(confidences.values()))


def weighted_average(confidences: dict[str, float], weights: dict[str, float]) -> float:
    """Weighted confidence fusion for less conservative operating points."""
    if not confidences:
        return 0.0
    total_weight = 0.0
    weighted_sum = 0.0
    for key, confidence in confidences.items():
        weight = float(weights.get(key, 0.0))
        weighted_sum += weight * float(confidence)
        total_weight += weight
    if total_weight <= 0:
        return minimum_rule(confidences)
    return clamp(weighted_sum / total_weight)


def fuse_confidences(confidences: dict[str, float], cfg: dict) -> dict[str, float]:
    """Record all configured fusion strategies for later comparison."""
    strategies = cfg.get("strategies_to_record", ["minimum", "weighted_average"])
    out: dict[str, float] = {}
    if "minimum" in strategies:
        out["minimum"] = minimum_rule(confidences)
    if "weighted_average" in strategies:
        out["weighted_average"] = weighted_average(confidences, cfg.get("weights", {}))
    preferred = cfg.get("preferred_strategy", "minimum")
    out["preferred_strategy"] = preferred  # type: ignore[assignment]
    out["preferred"] = float(out.get(preferred, minimum_rule(confidences)))
    return out
