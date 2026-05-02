# API Log Lakehouse (Databricks + Delta)

## Architecture

This project implements a simple medallion (Bronze → Silver → Gold) lakehouse pipeline using Databricks and Delta Lake.

* Raw JSON API logs are ingested into a Bronze table as immutable text for replayability and audit.
* Silver transforms the data by parsing JSON, enforcing schema, filtering invalid records into a quarantine table, and deduplicating by `request_id`.
* Gold aggregates the cleaned data into daily service-level KPIs such as error rate, latency, and SLA breaches.

**Flow:**

```
Raw JSON files → Bronze → Silver (clean + quarantine) → Gold (KPIs)
```

---

## Raw Log Schema

```json
{
  "request_id": "req_20260423_000001",
  "event_time": "2026-04-23T09:15:31Z",
  "service": "docs-api",
  "endpoint": "/v1/documents/upload",
  "method": "POST",
  "status_code": 201,
  "latency_ms": 84,
  "bytes_in": 1536,
  "bytes_out": 48210,
  "client_type": "web",
  "region": "ap-south-1",
  "host": "app-03"
}
```

---

## Tables

### Bronze

* `workspace.api_logs_schema.bronze_api_logs_raw`

  * Raw JSON logs stored as text (`value`)
  * Includes ingestion metadata (`ingest_ts`, `source_file`)
  * No parsing or validation applied

### Silver

* `workspace.api_logs_schema.silver_api_logs_clean`

  * Parsed JSON into structured columns
  * Enforced schema and validation rules
  * Removed invalid records
  * Deduplicated by `request_id`

* `workspace.api_logs_schema.silver_api_logs_quarantine`

  * Records that failed validation
  * Examples:

    * missing `request_id`
    * negative `latency_ms`
    * invalid `status_code`
    * malformed JSON

### Gold

* `workspace.api_logs_schema.gold_service_daily_kpis`

  * Aggregated daily metrics per service
  * Includes:

    * total requests
    * client and server errors
    * error rate
    * average and p95 latency
    * SLA breach counts
    * total bytes out

---

## Data Quality Definitions

* **Late data**
  Records where `event_time` belongs to a previous day but arrive in a later ingest batch.

* **Bad data**
  Invalid records such as:

  * missing `request_id`
  * negative `latency_ms`
  * invalid `status_code`
  * malformed JSON

* **Duplicate data**
  Multiple records with the same `request_id`.

---

## Business Questions

1. Which services had the highest error rate each day?
2. Which endpoints had the highest p95 latency?
3. Which services breached SLA most often?

---

## Example KPIs

* Total requests per service per day
* Error rate (4xx + 5xx)
* Average latency and p95 latency
* SLA breach counts per service

---

## Orchestration

The Bronze → Silver → Gold Databricks notebooks are grouped into a Databricks Job and orchestrated from Apache Airflow using `DatabricksRunNowOperator`.

The Airflow DAG runs on a daily schedule and triggers the Databricks job using a workspace API token. Historical data processing is supported using Airflow backfill.

---


## How to Run

1. Generate synthetic logs:

```bash
python scripts/generate_logs.py --date 2026-04-23 --hour 09 --rows 250 --late-rate 0 --dup-rate 0.02 --bad-rate 0.01 --seed 1 --out sample_data/raw/...
```

2. Upload files to Databricks Volume:

```
/Volumes/workspace/api_logs_schema/api_logs_volume/
```

3. Run notebooks in order:

* `00_explore.ipynb`
* `01_bronze_ingest.ipynb`
* `02_silver_clean.ipynb`
* `03_gold_kpis.ipynb`

4. Create Databricks Job:

* bronze_ingest → silver_clean → gold_kpis

5. Run Airflow DAG:

* `api_logs_databricks_run`

---

## Notes

* Bronze stores raw data for audit and replay
* Silver handles data quality logic (validation, deduplication)
* Gold is optimized for analytics and reporting
* Airflow is used only for orchestration, not transformation logic
* Built using Databricks Free Edition, Delta Lake, and Apache Airflow

---

## Repository Structure

```
api-log-lakehouse/
  README.md
  scripts/
    generate_logs.py
  sample_data/
    raw/
    dims/
  databricks_delta/
    01_bronze_ingest.ipynb
    02_silver_clean.ipynb
    03_gold_kpis.ipynb
  airflow_local/
    dags/
      api_logs_databricks_run.py
  docs/
    screenshots/
```

---

## Status

End-to-end pipeline completed:

* Data generation
* Bronze / Silver / Gold layers
* Databricks Job orchestration
* Airflow DAG + backfill

Ready for next step: **dbt modeling and testing**
