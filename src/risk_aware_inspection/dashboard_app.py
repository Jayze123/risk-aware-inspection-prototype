from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from nicegui import ui

PROJECT_SRC = Path(__file__).resolve().parents[1]

if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from risk_aware_inspection.audit_db import connect, fetch_record, save_operator_review  # noqa: E402
from risk_aware_inspection.qa_release import recommend_qa_action


def fetch_summary() -> list[dict[str, Any]]:
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
            return list(cursor.fetchall())

def fetch_latest_operator_review(record_id: int) -> dict[str, Any] | None:
    """Fetch the latest operator review for one inspection record."""
    query = """
        SELECT
            id,
            inspection_record_id,
            operator_decision,
            operator_note,
            reviewed_by,
            created_at
        FROM operator_reviews
        WHERE inspection_record_id = %(record_id)s
        ORDER BY created_at DESC, id DESC
        LIMIT 1;
    """

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, {"record_id": record_id})
            return cursor.fetchone()

def fetch_records(
    category: str | None = None,
    model_name: str | None = None,
    review_filter: str = "all",
    limit: int = 50,
) -> list[dict[str, Any]]:
    filters: list[str] = []
    params: dict[str, Any] = {"limit": int(limit)}

    if category not in (None, "all"):
        filters.append("category = %(category)s")
        params["category"] = category

    if model_name not in (None, "all"):
        filters.append("model_name = %(model_name)s")
        params["model_name"] = model_name

    if review_filter == "requires review":
        filters.append("requires_review = %(requires_review)s")
        params["requires_review"] = True
    elif review_filter == "no review":
        filters.append("requires_review = %(requires_review)s")
        params["requires_review"] = False

    where_clause = ""

    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    query = f"""
        SELECT
            id,
            image_id,
            category,
            model_name,
            semantic_label,
            risk_class,
            fused_confidence,
            is_anomalous,
            requires_review,
            created_at
        FROM inspection_records
        {where_clause}
        ORDER BY created_at DESC, id DESC
        LIMIT %(limit)s;
    """

    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = list(cursor.fetchall())

    for row in rows:
        if row.get("created_at") is not None:
            row["created_at"] = str(row["created_at"])

        if row.get("fused_confidence") is not None:
            row["fused_confidence"] = round(float(row["fused_confidence"]), 4)

        qa_decision = recommend_qa_action(row)
        row["qa_action"] = qa_decision["qa_action"]

    return rows


def get_record_count() -> int:
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM inspection_records;")
            row = cursor.fetchone()

    return int(row["count"])


ui.page_title("Risk-Aware Inspection Dashboard")

with ui.header().classes("items-center justify-between"):
    ui.label("Risk-Aware Inspection Operator Dashboard").classes("text-h5")
    status_label = ui.label("Database: checking...")

with ui.column().classes("w-full p-4 gap-4"):
    ui.label("Operational dashboard").classes("text-h6")
    ui.label(
        "This interface allows an operator to view inspection records, inspect review requirements "
        "and save review decisions to the PostgreSQL audit database."
    )

    with ui.card().classes("w-full"):
        ui.label("Database summary").classes("text-h6")
        summary_container = ui.column().classes("w-full")

    with ui.card().classes("w-full"):
        ui.label("Inspection records").classes("text-h6")

        with ui.row().classes("items-end gap-4"):
            category_select = ui.select(
                ["all", "bottle", "capsule", "hazelnut"],
                value="all",
                label="Category",
            )

            model_select = ui.select(
                ["all", "patchcore", "padim"],
                value="all",
                label="Model",
            )

            review_select = ui.select(
                ["all", "requires review", "no review"],
                value="all",
                label="Review filter",
            )

            limit_input = ui.number(
                label="Limit",
                value=50,
                min=1,
                max=200,
            )

        columns = [
            {"name": "id", "label": "ID", "field": "id", "sortable": True},
            {"name": "image_id", "label": "Image ID", "field": "image_id", "sortable": True},
            {"name": "category", "label": "Category", "field": "category", "sortable": True},
            {"name": "model_name", "label": "Model", "field": "model_name", "sortable": True},
            {"name": "semantic_label", "label": "Semantic label", "field": "semantic_label", "sortable": True},
            {"name": "risk_class", "label": "Risk class", "field": "risk_class", "sortable": True},
            {"name": "qa_action", "label": "QA action", "field": "qa_action", "sortable": True},
            {"name": "fused_confidence", "label": "Confidence", "field": "fused_confidence", "sortable": True},
            {"name": "requires_review", "label": "Review?", "field": "requires_review", "sortable": True},
            {"name": "created_at", "label": "Created", "field": "created_at", "sortable": True},
        ]

        records_table = ui.table(columns=columns, rows=[], row_key="id").classes("w-full")

    with ui.card().classes("w-full"):
        ui.label("Operator review").classes("text-h6")

        with ui.row().classes("items-end gap-4"):
            record_id_input = ui.number(label="Inspection record ID", value=1, min=1)
            decision_select = ui.select(
                [
                    "false_positive_release",
                    "defect_confirmed",
                    "needs_further_inspection",
                    "rejected",
                    "accepted",
                ],
                value="false_positive_release",
                label="Operator decision",
            )
            reviewed_by_input = ui.input(label="Reviewed by", value="operator_demo")

        review_note_input = ui.textarea(label="Review note").classes("w-full")

        selected_record_output = ui.markdown("No record selected yet.")

        with ui.row().classes("gap-4"):
            load_record_button = ui.button("Load selected record")
            save_review_button = ui.button("Save review decision", color="primary")


def refresh_summary() -> None:
    summary_container.clear()

    try:
        total_records = get_record_count()
        status_label.text = f"Database connected | {total_records} records"

        rows = fetch_summary()

        with summary_container:
            ui.label(f"Total inspection records: {total_records}").classes("text-bold")

            summary_columns = [
                {"name": "category", "label": "Category", "field": "category"},
                {"name": "model_name", "label": "Model", "field": "model_name"},
                {"name": "count", "label": "Records", "field": "count"},
                {"name": "review_count", "label": "Requires review", "field": "review_count"},
            ]

            ui.table(columns=summary_columns, rows=rows, row_key="category").classes("w-full")

    except Exception as exc:
        status_label.text = "Database connection failed"
        with summary_container:
            ui.label(f"Error: {exc}").classes("text-negative")


def refresh_records() -> None:
    category = None if category_select.value == "all" else category_select.value
    model_name = None if model_select.value == "all" else model_select.value
    review_filter = str(review_select.value)
    limit = int(limit_input.value or 50)

    try:
        records_table.rows = fetch_records(
            category=category,
            model_name=model_name,
            review_filter=review_filter,
            limit=limit,
        )
        records_table.update()
        ui.notify("Inspection records refreshed.", type="positive")

    except Exception as exc:
        ui.notify(f"Could not load records: {exc}", type="negative")


def load_selected_record() -> None:
    try:
        record_id = int(record_id_input.value)

        with connect() as connection:
            record = fetch_record(connection, record_id)

        if record is None:
            selected_record_output.content = f"Record `{record_id}` was not found."
            return

        latest_review = fetch_latest_operator_review(record_id)
        qa_decision = recommend_qa_action(record, latest_review)

        selected_record_output.content = (
            f"### Selected inspection record\n\n"
            f"- **ID:** `{record.get('id')}`\n"
            f"- **Image ID:** `{record.get('image_id')}`\n"
            f"- **Category:** `{record.get('category')}`\n"
            f"- **Model:** `{record.get('model_name')}`\n"
            f"- **Semantic label:** `{record.get('semantic_label')}`\n"
            f"- **Risk class:** `{record.get('risk_class')}`\n"
            f"- **Fused confidence:** `{record.get('fused_confidence')}`\n"
            f"- **Requires review:** `{record.get('requires_review')}`\n"
            f"- **Review reasons:** `{record.get('review_reasons')}`\n\n"
            f"### QA release decision\n\n"
            f"- **QA action:** `{qa_decision.get('qa_action')}`\n"
            f"- **QA status:** `{qa_decision.get('qa_status')}`\n"
            f"- **Operator action required:** `{qa_decision.get('requires_operator_action')}`\n"
            f"- **Reason:** {qa_decision.get('reason')}\n\n"
            f"### Latest operator review\n\n"
            f"- **Decision:** `{latest_review.get('operator_decision') if latest_review else 'No review saved yet'}`\n"
            f"- **Reviewed by:** `{latest_review.get('reviewed_by') if latest_review else 'N/A'}`\n"
            f"- **Note:** {latest_review.get('operator_note') if latest_review else 'N/A'}\n"
        )

    except Exception as exc:
        selected_record_output.content = f"Could not load record: {exc}"


def save_review() -> None:
    try:
        record_id = int(record_id_input.value)

        with connect() as connection:
            record = fetch_record(connection, record_id)

            if record is None:
                ui.notify("Inspection record not found.", type="negative")
                return

            review_id = save_operator_review(
                connection=connection,
                inspection_record_id=record_id,
                operator_decision=str(decision_select.value),
                operator_note=review_note_input.value,
                reviewed_by=reviewed_by_input.value,
            )

        ui.notify(f"Review saved with ID {review_id}.", type="positive")

        load_selected_record()
        refresh_records()

    except Exception as exc:
        ui.notify(f"Could not save review: {exc}", type="negative")


ui.button("Refresh summary and records", on_click=lambda: (refresh_summary(), refresh_records()))
load_record_button.on_click(load_selected_record)
save_review_button.on_click(save_review)

refresh_summary()
refresh_records()

ui.run(host="127.0.0.1", port=8090, reload=False)