# NiceGUI Operator Dashboard

## Purpose

This note documents the NiceGUI operator dashboard added to the operational application layer of the risk-aware inspection prototype. The dashboard provides a browser-based interface for viewing inspection records, checking review requirements and saving operator review decisions to the PostgreSQL audit database.

## Implementation summary

The dashboard is implemented in:

`src/risk_aware_inspection/dashboard_app.py`

It connects to the PostgreSQL audit database through:

`src/risk_aware_inspection/audit_db.py`

The PostgreSQL service is provided through Docker Compose and is accessed from the host machine using port `55432`.

## Dashboard features

The dashboard currently provides:

* a database connection status indicator;
* a summary table showing the number of inspection records by category and model;
* a review-count summary showing how many cases require operator review;
* an inspection records table with category, model, semantic label, risk class, confidence and review status;
* category, model and review-status filters;
* an operator review form for loading a selected inspection record;
* a review submission function for saving operator decisions to the PostgreSQL audit database.

## Test evidence

The dashboard successfully connected to the PostgreSQL audit database and detected 650 inspection records. The database summary displayed the six loaded experiment groups: bottle, capsule and hazelnut across PatchCore and PaDiM. The inspection records table also loaded records from the database, confirming that the dashboard can retrieve operational inspection outputs.

The dashboard was run locally on:

`http://127.0.0.1:8090`

Port `8090` was used because port `8080` was unavailable on the Windows system.

## Dissertation relevance

The NiceGUI dashboard demonstrates the human-in-the-loop part of the risk-aware inspection system. It moves the prototype beyond command-line experimentation by providing an operator-facing interface for inspection review. This supports the dissertation objectives related to deployment, operator interaction, auditability and practical system integration.

Together with FastAPI, PostgreSQL and Docker, the dashboard forms part of the operational application layer of the proposed inspection framework.
