from datetime import datetime

from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator

with DAG(
	dag_id = "api_logs_databricks_run",
	start_date = datetime(2026,4,23),
	schedule = "@daily",
	catchup = False,
	tag = ["logs","databricks"],
) as dag:
	run_api_logs_job = DatabricksRunNowOperator(
		task_id = "run_api_logs_job",
		databricks_conn_id = "databricks_default",
		job_id = 309286248944804,
	)