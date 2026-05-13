from datetime import datetime

from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="api_logs_databricks_run",
    start_date=datetime(2026, 4, 23),
    schedule="@daily",
    catchup=False,
    tags=["logs", "databricks", "dbt"],
) as dag:

    run_api_logs_job = DatabricksRunNowOperator(
        task_id="run_api_logs_job",
        databricks_conn_id="databricks_default",
        job_id=309286248944804,
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "cd /mnt/c/Users/PavanAray/Desktop/log/api-log-lakehouse/dbt_databricks "
            "&& source ../.venv/bin/activate "
            "&& dbt build"
        ),
    )

    run_api_logs_job >> run_dbt
