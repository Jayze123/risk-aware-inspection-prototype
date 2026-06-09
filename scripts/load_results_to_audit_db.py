from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from risk_aware_inspection.audit_db import (  # noqa: E402
    connect,
    initialise_schema,
    load_results_csv,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load pipeline results.csv records into the PostgreSQL audit database."
    )
    parser.add_argument("--results", required=True, help="Path to a pipeline results.csv file.")
    parser.add_argument(
        "--database-url",
        default=None,
        help="PostgreSQL connection URL. If omitted, DATABASE_URL or the default local URL is used.",
    )
    parser.add_argument(
        "--schema",
        default="database/schema.sql",
        help="Path to the PostgreSQL schema SQL file.",
    )
    parser.add_argument(
        "--initialise-schema",
        action="store_true",
        help="Create audit tables before loading records.",
    )

    args = parser.parse_args()

    with connect(args.database_url) as connection:
        if args.initialise_schema:
            initialise_schema(connection, args.schema)
            print(f"Schema initialised from: {args.schema}")

        inserted_count = load_results_csv(connection, args.results)

    print("Audit database load complete.")
    print(f"Results file: {args.results}")
    print(f"Inserted records: {inserted_count}")


if __name__ == "__main__":
    main()