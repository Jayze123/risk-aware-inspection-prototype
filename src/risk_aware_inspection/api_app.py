from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from risk_aware_inspection.audit_db import (
    connect,
    fetch_record,
    save_operator_review,
)


app = FastAPI(
    title="Risk-Aware Inspection API",
    description="FastAPI backend for the risk-aware visual inspection prototype.",
    version="0.1.0",
)


class OperatorReviewRequest(BaseModel):
    inspection_record_id: int = Field(..., description="Database ID of the inspection record.")
    operator_decision: str = Field(..., description="Operator decision, such as accepted, rejected or escalated.")
    operator_note: str | None = Field(default=None, description="Optional operator note.")
    reviewed_by: str | None = Field(default=None, description="Optional operator identifier.")


def _make_json_safe(value: Any) -> Any:
    """Convert database rows into JSON-safe objects."""
    return jsonable_encoder(value)


@app.get("/health")
def health_check() -> dict[str, Any]:
    """Check that the API and PostgreSQL database are reachable."""
    try:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS count FROM inspection_records;")
                row = cursor.fetchone()

        return {
            "status": "ok",
            "database": "connected",
            "inspection_records": int(row["count"]),
        }

    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Database connection failed: {exc}") from exc


@app.get("/records")
def list_records(
    limit: int = Query(default=25, ge=1, le=200),
    category: str | None = Query(default=None),
    model_name: str | None = Query(default=None),
    requires_review: bool | None = Query(default=None),
) -> dict[str, Any]:
    """List recent inspection records, with optional filters."""
    query = """
        SELECT
            id,
            image_id,
            image_path,
            category,
            model_name,
            anomaly_score,
            anomaly_threshold,
            is_anomalous,
            semantic_label,
            semantic_confidence,
            risk_class,
            fused_confidence,
            requires_review,
            review_reasons,
            created_at
        FROM inspection_records
        WHERE (%(category)s IS NULL OR category = %(category)s)
          AND (%(model_name)s IS NULL OR model_name = %(model_name)s)
          AND (%(requires_review)s IS NULL OR requires_review = %(requires_review)s)
        ORDER BY created_at DESC, id DESC
        LIMIT %(limit)s;
    """

    params = {
        "limit": limit,
        "category": category,
        "model_name": model_name,
        "requires_review": requires_review,
    }

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

    return {
        "count": len(rows),
        "records": _make_json_safe(rows),
    }


@app.get("/records/{record_id}")
def get_record(record_id: int) -> dict[str, Any]:
    """Return one inspection record by database ID."""
    with connect() as connection:
        record = fetch_record(connection, record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Inspection record not found.")

    return _make_json_safe(record)


@app.post("/reviews")
def create_operator_review(review: OperatorReviewRequest) -> dict[str, Any]:
    """Save an operator review decision for an inspection record."""
    with connect() as connection:
        existing_record = fetch_record(connection, review.inspection_record_id)

        if existing_record is None:
            raise HTTPException(status_code=404, detail="Inspection record not found.")

        review_id = save_operator_review(
            connection=connection,
            inspection_record_id=review.inspection_record_id,
            operator_decision=review.operator_decision,
            operator_note=review.operator_note,
            reviewed_by=review.reviewed_by,
        )

    return {
        "status": "saved",
        "operator_review_id": review_id,
        "inspection_record_id": review.inspection_record_id,
    }


@app.get("/summary")
def get_summary() -> dict[str, Any]:
    """Return grouped record counts by category and model."""
    query = """
        SELECT
            category,
            model_name,
            COUNT(*) AS count,
            SUM(CASE WHEN requires_review THEN 1 ELSE 0 END) AS review_count
        FROM inspection_records
        GROUP BY category, model_name
        ORDER BY category, model_name;
    """

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "summary": _make_json_safe(rows),
    }