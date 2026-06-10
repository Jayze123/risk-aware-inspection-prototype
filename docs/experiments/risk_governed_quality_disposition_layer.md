# Risk-Governed Quality Disposition Layer

## Purpose

This note documents the Risk-Governed Quality Disposition Layer added to the risk-aware inspection prototype. The layer extends the inspection pipeline by converting model outputs, semantic interpretation, risk class, confidence evidence and operator review decisions into a final quality disposition outcome.

In this context, quality disposition refers to the operational decision assigned to an inspected product after the automated and human-review stages have been considered. Possible outcomes include pass, hold, reinspect, quarantine, review required, release after review and reject after review.

## Rationale

The original inspection pipeline produced anomaly detection outputs, localisation evidence, semantic labels, risk classes and review requirements. However, a manufacturing operator also needs a clear operational decision that explains what should happen to the inspected product.

The Risk-Governed Quality Disposition Layer addresses this by translating inspection evidence into a practical decision-support output. This is especially useful where a product is initially flagged as anomalous but is later confirmed by an operator to be a false positive. In that case, the product can be released after review while preserving the full audit trail.

## Implementation summary

The disposition logic is implemented in:

`src/risk_aware_inspection/qa_release.py`

The FastAPI backend exposes the computed disposition through:

`GET /records/{record_id}/qa-decision`

The NiceGUI dashboard displays the disposition in the selected-record view and allows an operator to submit review decisions that can update the final disposition.

## Disposition policy

The implemented policy uses the inspection record first and then applies the latest operator review where available.

| Condition | Disposition outcome |
|---|---|
| Product is not anomalous | `PASS` |
| Product is anomalous but uncertain, low-confidence or semantically ambiguous | `REVIEW_REQUIRED` |
| Critical-risk anomaly | `QUARANTINE` |
| High-risk anomaly | `HOLD` |
| Medium-risk anomaly | `REINSPECT` |
| Low-risk anomaly | `PASS_WITH_MONITORING` |
| Operator confirms false positive | `RELEASE_AFTER_REVIEW` |
| Operator confirms defect | `REJECT_AFTER_REVIEW` |
| Operator escalates case | `ENGINEERING_REVIEW` |

## Demonstration evidence

The dashboard was tested using inspection record `650`, which initially represented a PaDiM capsule result with high risk, unknown semantic label and review required status. The system initially treated this type of case as requiring review because the semantic label was uncertain and the fused confidence was below the operational threshold.

After the operator selected `false_positive_release`, the disposition changed to:

`RELEASE_AFTER_REVIEW`

The status changed to:

`released`

This demonstrates that the system can support a realistic quality-assurance workflow where a model-detected anomaly can be released after human confirmation, rather than being automatically rejected.

## Dissertation relevance

This layer strengthens the operational application layer of the dissertation prototype. It demonstrates that the system does not stop at anomaly detection or risk classification, but can translate inspection evidence into an auditable quality-control decision.

The layer also supports human-in-the-loop governance because uncertain, high-risk or ambiguous cases can be routed to an operator. Operator decisions are then stored in the PostgreSQL audit database and can influence the final disposition outcome. This provides a practical link between anomaly detection, risk-aware reasoning, operator interaction and traceable quality assurance.

## Scope and limitation

This implementation is a prototype-level decision-support layer rather than a fully deployed production-line controller. It does not physically actuate a conveyor, reject gate or robotic sorting mechanism. Instead, it demonstrates the decision logic that such a system could use. In a real manufacturing facility, the disposition output could be integrated with a programmable logic controller, conveyor diverter or manufacturing execution system after additional safety validation.