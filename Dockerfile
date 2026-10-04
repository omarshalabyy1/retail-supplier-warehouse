# Airflow plus the project's own tools (dbt, psycopg) in a separate virtual environment,
# so dbt's packages never clash with Airflow's. The repo is mounted at /opt/project.
FROM apache/airflow:3.3.2-python3.10

USER root
RUN mkdir /opt/venv && chown airflow:0 /opt/venv
USER airflow

COPY requirements.txt /tmp/requirements.txt
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt
