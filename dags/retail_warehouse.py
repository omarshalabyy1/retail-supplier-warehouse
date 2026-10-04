"""Refresh the warehouse every morning: load the raw files, then build and test the star schema.

dbt build builds each model and then runs its tests, in order. A failed test turns the run red
and skips every model that depends on the failed one.
"""
import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag

PROJECT = "/opt/project"
VENV = "/opt/venv/bin"


@dag(
    schedule="0 6 * * *",  # 6am Cairo time, before the working day
    start_date=pendulum.datetime(2026, 10, 1, tz="Africa/Cairo"),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": pendulum.duration(minutes=5)},
)
def retail_warehouse():
    load_raw = BashOperator(task_id="load_raw", bash_command=f"cd {PROJECT} && {VENV}/python load.py")
    dbt_build = BashOperator(task_id="dbt_build", bash_command=f"cd {PROJECT}/dbt && {VENV}/dbt build")
    load_raw >> dbt_build


retail_warehouse()
