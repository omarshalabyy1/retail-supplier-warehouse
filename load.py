"""Load the input files in data/input/ into the warehouse's raw schema.

Before the database is touched, every file must exist with its required columns, and every product
category must have a department; otherwise the run stops with one line. Only the required columns are
loaded, as text (dbt's staging models do the cleaning; extra columns are ignored). Each run replaces the
raw tables inside one transaction, so running it twice gives the same result. Every load is written to
raw.load_log.

    python load.py
"""
import csv
import io
from pathlib import Path

import psycopg

DB_URL = "postgresql://warehouse:warehouse@127.0.0.1:5441/warehouse"
INPUT_DIR = Path(__file__).parent / "data" / "input"

# Input files (data/input/README.md): raw table -> file name.
FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "departments": "departments.csv",
}

# Raw table -> required columns.
COLUMNS = {
    "orders": ["order_id", "customer_id", "order_status", "order_purchase_timestamp",
               "order_delivered_customer_date", "order_estimated_delivery_date"],
    "order_items": ["order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"],
    "products": ["product_id", "product_category_name"],
    "sellers": ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"],
    "customers": ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"],
    "reviews": ["order_id", "review_score", "review_creation_date", "review_answer_timestamp"],
    "departments": ["category_code", "department"],
}


def read_rows(path):
    """Rows as dicts. utf-8-sig drops the byte-order mark some exports start with."""
    f = open(path, encoding="utf-8-sig", newline="")
    reader = csv.DictReader(f)
    reader.fieldnames = [name.strip() for name in reader.fieldnames or []]
    return f, reader


def check_inputs():
    files = {key: INPUT_DIR / name for key, name in FILES.items()}
    for key, path in files.items():
        if not path.exists():
            raise SystemExit(f"missing input file data/input/{path.name}")
        f, reader = read_rows(path)
        with f:
            missing = [c for c in COLUMNS[key] if c not in reader.fieldnames]
        if missing:
            raise SystemExit(f"data/input/{path.name} is missing column(s): {', '.join(missing)}")

    f, reader = read_rows(files["departments"])
    with f:
        mapped = {row["category_code"] for row in reader}
    f, reader = read_rows(files["products"])
    with f:
        unmapped = sorted({row["product_category_name"] for row in reader if row["product_category_name"]} - mapped)
    if unmapped:
        raise SystemExit(f"data/input/{files['departments'].name} has no department for category code(s): {', '.join(unmapped)}")
    return files


def main():
    files = check_inputs()

    with psycopg.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS raw.load_log (
                table_name text,
                source_file text,
                rows_loaded integer,
                loaded_at timestamptz DEFAULT now()
            )""")
        for key, path in files.items():
            columns = COLUMNS[key]
            # DROP CASCADE also drops dbt's staging views; the next dbt run rebuilds them.
            cur.execute(f"DROP TABLE IF EXISTS raw.{key} CASCADE")
            cur.execute(f"CREATE TABLE raw.{key} ({', '.join(f'{c} text' for c in columns)})")
            # Only the required columns, written back as CSV: an empty field stays NULL, as in the file.
            f, reader = read_rows(path)
            with f, cur.copy(f"COPY raw.{key} FROM STDIN (FORMAT csv)") as copy:
                buffer = io.StringIO()
                writer = csv.writer(buffer)
                for row in reader:
                    writer.writerow([row[c] for c in columns])
                    if buffer.tell() > 1 << 20:
                        copy.write(buffer.getvalue())
                        buffer.seek(0)
                        buffer.truncate()
                copy.write(buffer.getvalue())
            cur.execute(f"SELECT count(*) FROM raw.{key}")
            rows = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO raw.load_log (table_name, source_file, rows_loaded) VALUES (%s, %s, %s)",
                (key, path.name, rows),
            )
            print(f"raw.{key}: {rows:,} rows from {path.name}")


if __name__ == "__main__":
    main()
