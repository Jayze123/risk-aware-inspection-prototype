# PostgreSQL Audit Schema

## Purpose

This note documents the PostgreSQL audit schema added for the operational application layer of the risk-aware inspection prototype.

The schema supports traceability by storing automated inspection results and operator review decisions. This aligns with the dissertation objective of developing a risk-aware inspection workflow that is auditable, explainable and suitable for human-in-the-loop review.

## Tables

### inspection_records

The `inspection_records` table stores the automated output produced by the inspection pipeline. Each record can store:

- image ID;
- image path;
- dataset category;
- model name;
- anomaly score;
- anomaly threshold;
- anomaly decision;
- semantic label;
- semantic confidence;
- risk class;
- fused confidence;
- review requirement;
- review reasons;
- full JSON result payload.

The `result_payload` field is stored as JSONB so that detailed pipeline outputs can be preserved without requiring every intermediate value to have a separate database column.

### operator_reviews

The `operator_reviews` table stores human-review decisions linked to inspection records. This allows the system to record whether an operator accepted, rejected or escalated an automated result.

## Dissertation relevance

The schema provides the database foundation for the operational prototype. It supports audit logging, traceability and human-in-the-loop governance, which are important parts of the proposed risk-aware inspection framework.