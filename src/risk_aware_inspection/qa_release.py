from __future__ import annotations

from typing import Any


def _normalise_text(value: Any) -> str:
    """Convert a value into a safe lowercase comparison string."""
    if value is None:
        return ""

    return str(value).strip().lower().replace(" ", "_")


def recommend_qa_action(
    inspection_record: dict[str, Any],
    latest_review: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Compute a practical QA release decision for an inspected product.

    The automated inspection result is used first. If an operator review exists,
    the operator decision can override the automated decision. This supports a
    manufacturing-style workflow where false positives may be released after
    review, while confirmed defects can be rejected or escalated.
    """
    if latest_review is not None:
        operator_decision = _normalise_text(latest_review.get("operator_decision"))

        if operator_decision in {
            "false_positive_release",
            "release_after_review",
            "released_after_review",
            "release",
        }:
            return {
                "qa_action": "RELEASE_AFTER_REVIEW",
                "qa_status": "released",
                "requires_operator_action": False,
                "reason": "The operator reviewed the case and marked it as safe to release.",
            }

        if operator_decision in {
            "defect_confirmed",
            "reject_after_review",
            "rejected",
            "reject",
        }:
            return {
                "qa_action": "REJECT_AFTER_REVIEW",
                "qa_status": "rejected",
                "requires_operator_action": False,
                "reason": "The operator reviewed the case and confirmed that the product should not be released.",
            }

        if operator_decision in {
            "escalated",
            "needs_further_inspection",
            "further_inspection",
        }:
            return {
                "qa_action": "ENGINEERING_REVIEW",
                "qa_status": "escalated",
                "requires_operator_action": True,
                "reason": "The operator escalated the case for further inspection.",
            }

    is_anomalous = bool(inspection_record.get("is_anomalous"))
    requires_review = bool(inspection_record.get("requires_review"))
    risk_class = _normalise_text(inspection_record.get("risk_class"))
    semantic_label = _normalise_text(inspection_record.get("semantic_label"))

    if not is_anomalous:
        return {
            "qa_action": "PASS",
            "qa_status": "released",
            "requires_operator_action": False,
            "reason": "The product was not classified as anomalous.",
        }

    if requires_review or semantic_label == "unknown":
        return {
            "qa_action": "REVIEW_REQUIRED",
            "qa_status": "pending_review",
            "requires_operator_action": True,
            "reason": "The case requires review because the result is uncertain or semantically ambiguous.",
        }

    if risk_class == "critical":
        return {
            "qa_action": "QUARANTINE",
            "qa_status": "blocked",
            "requires_operator_action": True,
            "reason": "A critical-risk anomaly was detected, so the product should not be released automatically.",
        }

    if risk_class == "high":
        return {
            "qa_action": "HOLD",
            "qa_status": "held",
            "requires_operator_action": True,
            "reason": "A high-risk anomaly was detected, so the product should be held for quality review.",
        }

    if risk_class == "medium":
        return {
            "qa_action": "REINSPECT",
            "qa_status": "pending_reinspection",
            "requires_operator_action": True,
            "reason": "A medium-risk anomaly was detected, so reinspection is recommended.",
        }

    if risk_class == "low":
        return {
            "qa_action": "PASS_WITH_MONITORING",
            "qa_status": "released",
            "requires_operator_action": False,
            "reason": "A low-risk anomaly was detected, so the product can pass with monitoring.",
        }

    return {
        "qa_action": "REVIEW_REQUIRED",
        "qa_status": "pending_review",
        "requires_operator_action": True,
        "reason": "No confident QA release decision could be made from the available inspection evidence.",
    }