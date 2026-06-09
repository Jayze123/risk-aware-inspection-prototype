# FastAPI Audit Backend

## Purpose

This note documents the FastAPI backend added to the operational application layer of the risk-aware inspection prototype. The backend provides a lightweight service interface for reading inspection records from the PostgreSQL audit database and saving operator review decisions.

## Implementation summary

The backend is implemented in:

`src/risk_aware_inspection/api_app.py`

It connects to the PostgreSQL audit database through the database utility module:

`src/risk_aware_inspection/audit_db.py`

The database is accessed through Docker PostgreSQL on host port `55432`.

## API endpoints

The backend currently provides the following endpoints:

* `GET /health` checks whether the API and database are reachable.
* `GET /summary` returns grouped inspection counts by category and model.
* `GET /records` returns inspection records with optional filters.
* `GET /records/{record_id}` returns a single inspection record.
* `POST /reviews` saves an operator review decision linked to an inspection record.

## Test evidence

The `/health` endpoint confirmed that the backend connected successfully to PostgreSQL and detected 650 inspection records.

The `/summary` endpoint returned grouped results for bottle, hazelnut and capsule across PatchCore and PaDiM. This confirmed that the API can retrieve the loaded audit records from the database.

The `/docs` endpoint loaded the FastAPI Swagger interface, showing that the backend can be inspected and tested through an interactive API page.

## Dissertation relevance

This backend supports the operational application layer of the dissertation prototype. It shows how the risk-aware inspection pipeline can move beyond command-line experimentation into a service-based architecture. The backend also provides the foundation for human-in-the-loop interaction, because operator review decisions can be submitted and stored in the PostgreSQL audit database.

This contributes to the project aims of auditability, traceability, reproducibility and operator-supported inspection decision-making.
