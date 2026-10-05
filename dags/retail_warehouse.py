"""Refresh the warehouse on the client's schedule: load the input files, then build and test the star schema.

dbt build builds each model and then runs its tests, in order. A failed test turns the run red
and skips every model that depends on the failed one. Every client value comes from load_config().
"""
import json
import sys

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag

PROJECT = "/opt/project"
VENV = "/opt/venv/bin"

sys.path.insert(0, PROJECT)
from config import load_config  # noqa: E402

cfg = load_config()
warehouse = cfg["warehouse"]
# dbt reads the connection from these (dbt/profiles.yml); DB_PASSWORD is already in the container's environment.
DBT_ENV = {
    "WAREHOUSE_HOST": warehouse["host"],
    "WAREHOUSE_PORT": str(warehouse["port"]),
    "WAREHOUSE_USER": warehouse["user"],
    "WAREHOUSE_DATABASE": warehouse["database"],
}
DBT_VARS = json.dumps({key: cfg["rules"][key] for key in ("late_after_days", "top_sellers")})


@dag(
    schedule=cfg["schedule"]["cron"],
    start_date=pendulum.datetime(2026, 10, 1, tz=cfg["schedule"]["timezone"]),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": pendulum.duration(minutes=5)},
)
def retail_warehouse():
    load_raw = BashOperator(task_id="load_raw", bash_command=f"cd {PROJECT} && {VENV}/python load.py")
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {PROJECT}/dbt && {VENV}/dbt build --vars '{DBT_VARS}'",
        env=DBT_ENV,
        append_env=True,
    )
    load_raw >> dbt_build


retail_warehouse()
