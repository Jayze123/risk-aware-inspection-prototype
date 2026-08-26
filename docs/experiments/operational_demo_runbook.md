# Operational Demo Runbook

## Purpose

This runbook documents how to run the operational demonstration of the risk-aware inspection prototype. It brings together the Docker PostgreSQL audit database, the loaded experiment results, the FastAPI backend and the NiceGUI operator dashboard.

The purpose of the runbook is to provide a reproducible sequence for demonstrating the system as an integrated application layer rather than only as separate command-line experiments.

## 1. Prepare the operational environment

Open a PowerShell terminal in the repository root.

Create the standard environment if it does not already exist:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the operational application dependencies:

```powershell
python -m pip install -e ".[app]"
```

Confirm the active interpreter:

```powershell
python -c "import sys; print(sys.executable)"
```

The output should end with `.venv\Scripts\python.exe`.

## 2. Start PostgreSQL using Docker

Start the PostgreSQL container:

```powershell
docker compose up -d postgres
```

Check the container status:

```powershell
docker compose ps
```

The PostgreSQL service should show as healthy and should expose the database through host port `55432`.

## 3. Check the database connection

Confirm that PostgreSQL is reachable:

```powershell
docker compose exec -T postgres psql -U risk_user -d risk_inspection -c "SELECT current_user, current_database();"
```

The expected database user is `risk_user`, and the expected database is `risk_inspection`.

## 4. Load the final experiment evidence

A fresh Docker database initialises the schema automatically from `database/schema.sql`. Apply the same idempotent schema explicitly so that this procedure also works with an existing empty database volume:

```powershell
docker compose exec -T postgres psql -v ON_ERROR_STOP=1 -U risk_user -d risk_inspection -f /docker-entrypoint-initdb.d/001-schema.sql
```

Before loading, confirm that the database contains no inspection records:

```powershell
docker compose exec -T postgres psql -U risk_user -d risk_inspection -tAc "SELECT COUNT(*) FROM inspection_records;"
```

The expected result is `0`. Do not run the loading block against a populated database because the loader appends records.

Load the six portable final-result files:

```powershell
$evidenceFiles = Get-ChildItem -LiteralPath "evidence/final_results" -Filter "*.csv" | Sort-Object Name

foreach ($evidenceFile in $evidenceFiles) {
    python scripts/load_results_to_audit_db.py --results $evidenceFile.FullName
}
```

The six files should insert 650 inspection records in total.

## 5. Confirm loaded audit records

Check the number of inspection records:

```powershell
docker compose exec -T postgres psql -U risk_user -d risk_inspection -c "SELECT COUNT(*) FROM inspection_records;"
```

The expected total after loading the six final result sets is 650 records.

Check the grouped summary:

```powershell
docker compose exec -T postgres psql -U risk_user -d risk_inspection -c "SELECT category, model_name, COUNT(*) FROM inspection_records GROUP BY category, model_name ORDER BY category, model_name;"
```

The expected groups are bottle, capsule and hazelnut across PatchCore and PaDiM.

## 6. Run the FastAPI backend

Start the FastAPI backend:

```powershell
python -m uvicorn risk_aware_inspection.api_app:app --app-dir src --reload --port 8000
```

Open the health endpoint:

`http://127.0.0.1:8000/health`

The expected response should show:

* status: ok
* database: connected
* inspection_records: 650

Open the summary endpoint:

`http://127.0.0.1:8000/summary`

Open the interactive API documentation:

`http://127.0.0.1:8000/docs`

Stop the FastAPI backend with `Ctrl + C` after testing.

## 7. Run the NiceGUI operator dashboard

Start the dashboard:

```powershell
python src\risk_aware_inspection\dashboard_app.py
```

Open the dashboard in a browser:

`http://127.0.0.1:8090`

The dashboard should show:

* database connection status;
* 650 inspection records;
* summary table by category and model;
* inspection records table;
* operator review section.

## 8. Test the operator review workflow

First obtain the ID of a record requiring operator review:

```powershell
docker compose exec -T postgres psql -U risk_user -d risk_inspection -tAc "SELECT id FROM inspection_records WHERE requires_review IS TRUE ORDER BY id LIMIT 1;"
```

Enter the returned inspection-record ID in the dashboard and click:

Click:

`LOAD SELECTED RECORD`

The selected record details should appear below the review note box.

Enter a short operator note, choose a decision and click:

`SAVE REVIEW DECISION`

Verify that the review was saved in PostgreSQL:

```powershell
docker compose exec -T postgres psql -U risk_user -d risk_inspection -c "SELECT id, inspection_record_id, operator_decision, reviewed_by, created_at FROM operator_reviews ORDER BY id DESC LIMIT 5;"
```

## 9. Stop services

Stop the dashboard with:

`Ctrl + C`

Stop the Docker PostgreSQL service when the demo is finished:

```powershell
docker compose down
```

## Dissertation relevance

This runbook demonstrates that the prototype can be executed as an integrated operational workflow. The anomaly detection results are stored in PostgreSQL, exposed through FastAPI and reviewed through a NiceGUI dashboard. This supports the dissertation objectives related to reproducible experimentation, audit logging, operator interaction and deployment-oriented system integration.
