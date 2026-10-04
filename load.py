"""Load the raw CSV exports into the warehouse's raw schema, exactly as they are.

Every column lands as text; dbt's staging models do the cleaning. Each run replaces the raw
tables inside one transaction, so running it twice gives the same result, and a failed run
leaves yesterday's data in place. Every load is written to raw.load_log.

    python load.py            # from the repo root, warehouse on localhost:5441
"""
import csv
import os
from pathlib import Path

import psycopg

RAW_DIR = Path(__file__).parent / "data" / "raw"

# raw table name -> source file
FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def main():
    conn = psycopg.connect(
        host=os.environ.get("WAREHOUSE_HOST", "localhost"),
        port=os.environ.get("WAREHOUSE_PORT", "5441"),
        dbname="warehouse",
        user="warehouse",
        password=os.environ["WAREHOUSE_PASSWORD"],
    )
    with conn, conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.load_log (
                table_name text,
                source_file text,
                rows_loaded integer,
                loaded_at timestamptz DEFAULT now()
            )""")
        for table, file_name in FILES.items():
            path = RAW_DIR / file_name
            # utf-8-sig drops the byte-order mark some exports start with (the category file does).
            with open(path, encoding="utf-8-sig", newline="") as f:
                header = next(csv.reader(f))
            columns = ", ".join(f'"{c.strip()}" text' for c in header)
            # DROP CASCADE also drops dbt's staging views; the next dbt run rebuilds them.
            cur.execute(f"DROP TABLE IF EXISTS raw.{table} CASCADE")
            cur.execute(f"CREATE TABLE raw.{table} ({columns})")
            with open(path, "rb") as f, cur.copy(f"COPY raw.{table} FROM STDIN WITH (FORMAT csv, HEADER true)") as copy:
                while data := f.read(1 << 20):
                    copy.write(data)
            cur.execute(f"SELECT count(*) FROM raw.{table}")
            rows = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO raw.load_log (table_name, source_file, rows_loaded) VALUES (%s, %s, %s)",
                (table, file_name, rows),
            )
            print(f"raw.{table}: {rows:,} rows from {file_name}")


if __name__ == "__main__":
    main()
