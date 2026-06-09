# Docker PostgreSQL Service

This note documents the PostgreSQL service used for the operational application layer of the risk-aware inspection prototype.

The Docker Compose setup provides a PostgreSQL database for storing inspection audit records and operator review decisions.

The service uses:

- database name: risk_inspection
- username: risk_user
- password: risk_password
- port: 5432
- persistent volume: risk_postgres_data

Start the service with:

```powershell
docker compose up -d postgres