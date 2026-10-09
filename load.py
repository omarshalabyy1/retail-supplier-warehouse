"""Load the input files in data/input/ into the warehouse's Bronze layer (schema bronze).

Before the database is touched, every file must exist with its required columns, and every product
category must have a department; otherwise the run stops with one line. Only the required columns are
loaded, as text, exactly as written in the file (the Silver layer does the cleaning; extra columns are
ignored), with their lineage: the file, the row number in it, the run id and the load time.

A row whose required value is empty, or whose value would not convert to the type the Silver layer gives
it, is refused: it goes to bronze.quarantine with the reason, not to its Bronze table. The values are
checked with Postgres's own pg_input_is_valid, so every row in Bronze converts in Silver. An empty file or
a key that appears twice stops the run. Each run replaces the Bronze tables and the quarantine inside one
transaction, so running it twice gives the same result. Every load is written to ops.load_log.

    python load.py
"""
import csv
import io
import uuid
from pathlib import Path

import psycopg

DB_URL = "postgresql://warehouse:warehouse@127.0.0.1:5441/warehouse"
INPUT_DIR = Path(__file__).parent / "data" / "input"

# Input files (data/input/README.md): Bronze table -> file name.
FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "reviews": "olist_order_reviews_dataset.csv",
    "departments": "departments.csv",
}

# Bronze table -> required columns.
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

# Bronze table -> its key: a value that appears twice stops the run (reviews may repeat an order).
KEYS = {
    "orders": ["order_id"],
    "order_items": ["order_id", "order_item_id"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "customers": ["customer_id"],
    "departments": ["category_code"],
}

# Bronze table -> columns that must not be empty. A row with an empty one goes to bronze.quarantine.
NOT_EMPTY = {
    "orders": ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_estimated_delivery_date"],
    "order_items": COLUMNS["order_items"],
    "products": ["product_id"],
    "sellers": ["seller_id"],
    "customers": ["customer_id", "customer_unique_id"],
    "reviews": ["order_id", "review_score", "review_creation_date"],
    "departments": COLUMNS["departments"],
}

# Bronze table -> column -> the type the Silver layer gives it. A row that would not convert goes to bronze.quarantine.
TYPES = {
    "orders": {"order_purchase_timestamp": "timestamp", "order_delivered_customer_date": "timestamp",
               "order_estimated_delivery_date": "date"},
    "order_items": {"order_item_id": "integer", "price": "numeric(12,2)", "freight_value": "numeric(12,2)"},
    "reviews": {"review_score": "integer", "review_creation_date": "timestamp", "review_answer_timestamp": "timestamp"},
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


def refusal(key):
    """SQL for the reasons a row is refused, joined with '; '; an empty string when the row is accepted."""
    checks = [f"case when {c} is null then 'missing {c}' end" for c in NOT_EMPTY[key]]
    checks += [f"case when not pg_input_is_valid({c}, '{t}') then '{c} is not a {t}' end"
               for c, t in TYPES.get(key, {}).items()]
    return f"concat_ws('; ', {', '.join(checks)})"


def main():
    files = check_inputs()
    run_id = str(uuid.uuid4())

    with psycopg.connect(DB_URL) as conn, conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS bronze")
        cur.execute("CREATE SCHEMA IF NOT EXISTS ops")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ops.load_log (
                run_id uuid,
                table_name text,
                source_file text,
                rows_in_file integer,
                rows_loaded integer,
                rows_quarantined integer,
                loaded_at timestamptz DEFAULT now()
            )""")
        cur.execute("DROP TABLE IF EXISTS bronze.quarantine")
        cur.execute("""
            CREATE TABLE bronze.quarantine (
                table_name text NOT NULL,
                source_file text NOT NULL,
                source_row integer NOT NULL,
                row_data jsonb NOT NULL,
                reason text NOT NULL,
                run_id uuid NOT NULL,
                loaded_at timestamptz NOT NULL DEFAULT now(),
                PRIMARY KEY (table_name, source_row)
            )""")
        for key, path in files.items():
            columns = COLUMNS[key]
            # DROP CASCADE also drops dbt's Silver views; the next dbt run rebuilds them.
            cur.execute(f"DROP TABLE IF EXISTS bronze.{key} CASCADE")
            cur.execute(f"""
                CREATE TABLE bronze.{key} (
                    {', '.join(f'{c} text' for c in columns)},
                    source_file text NOT NULL,
                    source_row integer PRIMARY KEY,
                    run_id uuid NOT NULL,
                    loaded_at timestamptz NOT NULL DEFAULT now()
                )""")
            # Only the required columns, written back as CSV: an empty field stays NULL, as in the file.
            # source_row counts the data rows of the file from 1 (the header row is not counted).
            rows_in_file = 0
            f, reader = read_rows(path)
            with f, cur.copy(f"COPY bronze.{key} ({', '.join(columns)}, source_file, source_row, run_id) "
                             "FROM STDIN (FORMAT csv)") as copy:
                buffer = io.StringIO()
                writer = csv.writer(buffer)
                for row in reader:
                    rows_in_file += 1
                    writer.writerow([row[c] for c in columns] + [path.name, rows_in_file, run_id])
                    if buffer.tell() > 1 << 20:
                        copy.write(buffer.getvalue())
                        buffer.seek(0)
                        buffer.truncate()
                copy.write(buffer.getvalue())
            if rows_in_file == 0:
                raise SystemExit(f"data/input/{path.name} has no rows")

            # Refused rows move from the Bronze table to bronze.quarantine, as written in the file.
            cur.execute(f"""
                WITH refused AS (
                    DELETE FROM bronze.{key}
                    WHERE {refusal(key)} <> ''
                    RETURNING *, {refusal(key)} AS reason
                )
                INSERT INTO bronze.quarantine (table_name, source_file, source_row, row_data, reason, run_id)
                SELECT %s, source_file, source_row,
                       jsonb_build_object({', '.join(f"'{c}', {c}" for c in columns)}), reason, run_id
                FROM refused""", (key,))
            rows_quarantined = cur.rowcount

            if key in KEYS:
                cur.execute(f"SELECT count(*) - count(DISTINCT ({', '.join(KEYS[key])})) FROM bronze.{key}")
                if cur.fetchone()[0]:
                    raise SystemExit(f"data/input/{path.name}: {' + '.join(KEYS[key])} appears more than once")

            cur.execute(f"SELECT count(*) FROM bronze.{key}")
            rows = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO ops.load_log (run_id, table_name, source_file, rows_in_file, rows_loaded, rows_quarantined) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (run_id, key, path.name, rows_in_file, rows, rows_quarantined),
            )
            print(f"bronze.{key}: {rows:,} rows from {path.name}, {rows_quarantined:,} to bronze.quarantine")


if __name__ == "__main__":
    main()
