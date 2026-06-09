from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Any

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover
    psycopg = None
    dict_row = None


DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://risk_user:risk_password@127.0.0.1:55432/risk_inspection",
)


def _require_psycopg() -> None:
    if psycopg is None:
        raise RuntimeError(
            "psycopg is not installed. Install it with: pip install 'psycopg[binary]'"
        )


def connect(database_url: str | None = None):
    """Create a PostgreSQL connection."""
    _require_psycopg()
    return psycopg.connect(database_url or DEFAULT_DATABASE_URL, row_factory=dict_row)


def initialise_schema(connection, schema_path: str | Path = "database/schema.sql") -> None:
    """Create the audit tables if they do not already exist."""
    schema_file = Path(schema_path)

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    schema_sql = schema_file.read_text(encoding="utf-8")

    with connection.cursor() as cursor:
        cursor.execute(schema_sql)

    connection.commit()


def _first_available(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_bool(value: Any) -> bool | None:
    if value in (None, ""):
        return None

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()

    if text in {"true", "1", "yes", "y", "anomalous"}:
        return True

    if text in {"false", "0", "no", "n", "normal"}:
        return False

    return None


def _infer_category(image_path: str | None, image_id: str | None) -> str | None:
    combined = f"{image_path or ''} {image_id or ''}".lower()

    for category in ("bottle", "hazelnut", "capsule"):
        if category in combined:
            return category

    return None


def _normalise_model_name(value: Any) -> str:
    if value in (None, ""):
        return "unknown"

    text = str(value).strip().lower()

    if "patchcore" in text:
        return "patchcore"

    if "padim" in text:
        return "padim"

    if "statistical" in text or "simple" in text:
        return "statistical"

    return text


def normalise_result_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert one pipeline CSV row into the database record format."""
    image_id = _first_available(row, "image_id", "id")
    image_path = _first_available(row, "image_path", "path")
    model_name = _normalise_model_name(
        _first_available(row, "model", "model_name", "detector_name", "detection.detector_name")
    )

    anomaly_score = _parse_float(
        _first_available(
            row,
            "detection.image_score",
            "image_score",
            "pred_score",
            "score",
            "anomaly_score",
        )
    )

    anomaly_threshold = _parse_float(
        _first_available(
            row,
            "detection.threshold",
            "threshold",
            "pred_threshold",
            "anomaly_threshold",
        )
    )

    is_anomalous = _parse_bool(
        _first_available(
            row,
            "detection.is_anomalous",
            "is_anomalous",
            "pred_label",
            "prediction",
        )
    )

    semantic_label = _first_available(row, "semantic.label", "semantic_label")
    semantic_confidence = _parse_float(
        _first_available(row, "semantic.confidence", "semantic_confidence")
    )

    risk_class = _first_available(row, "risk.risk_class", "risk_class")
    fused_confidence = _parse_float(
        _first_available(
            row,
            "confidence.fusion.preferred",
            "fused_confidence",
            "confidence",
        )
    )

    requires_review = _parse_bool(
        _first_available(row, "review.requires_review", "requires_review")
    )

    review_reasons = _first_available(row, "review.reasons", "review_reasons")

    return {
        "image_id": str(image_id or "unknown"),
        "image_path": str(image_path) if image_path is not None else None,
        "category": _infer_category(str(image_path) if image_path else None, str(image_id) if image_id else None),
        "model_name": model_name,
        "anomaly_score": anomaly_score,
        "anomaly_threshold": anomaly_threshold,
        "is_anomalous": is_anomalous,
        "semantic_label": str(semantic_label) if semantic_label is not None else None,
        "semantic_confidence": semantic_confidence,
        "risk_class": str(risk_class) if risk_class is not None else None,
        "fused_confidence": fused_confidence,
        "requires_review": requires_review,
        "review_reasons": str(review_reasons) if review_reasons is not None else None,
        "result_payload": row,
    }


def insert_inspection_record(connection, record: dict[str, Any]) -> int:
    """Insert one inspection record and return its database ID."""
    query = """
        INSERT INTO inspection_records (
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
            result_payload
        )
        VALUES (
            %(image_id)s,
            %(image_path)s,
            %(category)s,
            %(model_name)s,
            %(anomaly_score)s,
            %(anomaly_threshold)s,
            %(is_anomalous)s,
            %(semantic_label)s,
            %(semantic_confidence)s,
            %(risk_class)s,
            %(fused_confidence)s,
            %(requires_review)s,
            %(review_reasons)s,
            %(result_payload)s
        )
        RETURNING id;
    """

    prepared_record = dict(record)
    prepared_record["result_payload"] = json.dumps(prepared_record["result_payload"])

    with connection.cursor() as cursor:
        cursor.execute(query, prepared_record)
        inserted = cursor.fetchone()

    connection.commit()
    return int(inserted["id"])


def load_results_csv(connection, results_path: str | Path) -> int:
    """Load inspection records from a pipeline results CSV file."""
    csv_path = Path(results_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"Results file not found: {csv_path}")

    inserted_count = 0

    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            record = normalise_result_row(row)
            insert_inspection_record(connection, record)
            inserted_count += 1

    return inserted_count


def save_operator_review(
    connection,
    inspection_record_id: int,
    operator_decision: str,
    operator_note: str | None = None,
    reviewed_by: str | None = None,
) -> int:
    """Store an operator review decision linked to an inspection record."""
    query = """
        INSERT INTO operator_reviews (
            inspection_record_id,
            operator_decision,
            operator_note,
            reviewed_by
        )
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """

    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (inspection_record_id, operator_decision, operator_note, reviewed_by),
        )
        inserted = cursor.fetchone()

    connection.commit()
    return int(inserted["id"])


def fetch_recent_records(connection, limit: int = 25) -> list[dict[str, Any]]:
    """Fetch recent inspection records for the operator dashboard/API."""
    query = """
        SELECT *
        FROM inspection_records
        ORDER BY created_at DESC
        LIMIT %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()

    return list(rows)


def fetch_record(connection, record_id: int) -> dict[str, Any] | None:
    """Fetch a single inspection record."""
    query = """
        SELECT *
        FROM inspection_records
        WHERE id = %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (record_id,))
        row = cursor.fetchone()

    return dict(row) if row is not None else None