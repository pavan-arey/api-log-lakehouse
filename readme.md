# API Log Lakehouse

### Databricks + Delta Lake + Airflow + dbt

Production-style medallion lakehouse pipeline for ingesting, validating, and analyzing high-volume API telemetry data using Databricks and Delta Lake.

This project simulates how data engineering teams process operational API logs into reliable analytical datasets for monitoring, SLA tracking, and downstream reporting.

---

# Repository

```text
https://github.com/pavan-arey/api-log-lakehouse
```

---

# Overview

The pipeline ingests raw JSON API logs into Delta Lake, applies validation and deduplication logic, quarantines bad records, and produces analytical KPI marts for service monitoring.

The project includes:

* batch ingestion pipelines
* streaming-style ingestion with Auto Loader
* Delta Lake medallion architecture
* quarantine handling for malformed records
* late-arriving event handling
* dbt analytical marts
* Airflow orchestration
* scale validation on ~1.28M records

---

# Architecture

```text
Raw Files / Stream Landing
            ↓
Bronze Delta Tables
            ↓
Silver Validation + Quarantine
            ↓
Gold KPI Aggregates + dbt Marts
            ↓
Airflow-Orchestrated Pipelines
```

---

# Tech Stack

* Databricks
* Apache Spark
* Delta Lake
* PySpark
* Structured Streaming
* Databricks Auto Loader
* Apache Airflow
* dbt
* Python

---

# Dataset

Synthetic API telemetry logs were generated to emulate production API traffic.

Example event:

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

The generator supports:

* configurable duplicate rates
* malformed JSON generation
* invalid status codes
* negative latency values
* late-arriving events
* deterministic seeded runs

---

# Medallion Layers

## Bronze Layer

### Table

`workspace.api_logs_schema.bronze_api_logs_raw`

### Purpose

Stores immutable raw ingestion data exactly as received.

### Characteristics

* raw JSON stored as text
* append-only Delta table
* ingestion metadata captured
* replayable source of truth
* no validation or transformation

### Metadata Captured

* `ingest_ts`
* `source_file`

---

## Silver Layer

### Tables

* `workspace.api_logs_schema.silver_api_logs_clean`
* `workspace.api_logs_schema.silver_api_logs_quarantine`

### Responsibilities

* JSON parsing
* schema enforcement
* validation
* duplicate handling
* bad-record isolation

### Validation Rules

Records are quarantined if they contain:

* malformed JSON
* missing `request_id`
* invalid `status_code`
* negative `latency_ms`

### Duplicate Handling

During scale testing, an overly broad duplicate-removal issue was discovered.

The initial implementation deduplicated only on `request_id`, but the synthetic generator reused IDs across files, causing unrelated records to collapse.

Deduplication logic was corrected to use a fuller event identity, preventing accidental data loss during large-scale ingestion validation.

This debugging process helped validate correctness under scaled workloads.

---

## Gold Layer

### Table

`workspace.api_logs_schema.gold_service_daily_kpis`

### Purpose

Aggregated KPI layer for operational analytics and reporting.

### Metrics

* total requests
* 4xx errors
* 5xx errors
* error rate
* average latency
* p95 latency
* SLA breach counts
* total bytes transferred

### Example Business Questions

* Which services had the highest daily error rate?
* Which endpoints had the highest p95 latency?
* Which services breached SLA most frequently?

---

# Streaming Ingestion

The project was extended with a streaming-style ingestion path using Databricks Auto Loader and Structured Streaming.

## Streaming Flow

```text
new files land in stream_landing/
        ↓
04_streaming_bronze_ingest
        ↓
05_streaming_silver_clean
        ↓
stream clean + quarantine tables refreshed
```

## Features

* incremental file ingestion
* checkpoint-based progress tracking
* triggered micro-batch execution
* reusable Silver validation logic
* separation of ingestion and downstream transformation

The streaming implementation was validated using triggered execution rather than continuously running clusters.

---

# Scale Testing

The pipeline was validated on a larger synthetic workload to test ingestion behavior, validation logic, and downstream rebuild consistency.

## Scale Validation Results

| Layer                    | Row Count |
| ------------------------ | --------: |
| Bronze                   | 1,280,995 |
| Silver Clean             | 1,230,948 |
| Silver Quarantine        |    19,535 |
| dbt Staging              | 1,230,948 |
| dbt Service Daily KPIs   |       100 |
| dbt Endpoint Hourly KPIs |       350 |

## Scale Testing Validated

* multi-file batch ingestion
* malformed-record quarantine
* duplicate handling behavior
* late-arriving event processing
* streaming checkpoint consistency
* downstream dbt mart rebuilds

---

# Why These Design Decisions?

## Why store raw JSON in Bronze?

* replayability
* auditability
* schema evolution safety
* separation of ingestion from transformation

## Why use a quarantine table?

Bad records are isolated without failing the entire ingestion pipeline.

This allows:

* continued processing of valid data
* investigation of malformed records
* safer operational workflows

## Why separate Airflow from transformations?

Airflow handles orchestration only.

Transformation logic remains inside Databricks notebooks and dbt models, keeping orchestration concerns separate from data processing logic.

---

# Orchestration

## Databricks Workflow

```text
bronze_ingest
    ↓
silver_clean
    ↓
gold_kpis
```

## Airflow DAG

Airflow triggers the Databricks workflow using:

```python
DatabricksRunNowOperator
```

### Features

* scheduled daily execution
* historical backfill support
* external orchestration
* dependency management

---

# Repository Structure

```text
api-log-lakehouse/
│
├── README.md
│
├── scripts/
│   └── generate_logs.py
│
├── sample_data/
│   ├── raw/
│   └── dims/
│
├── databricks_delta/
│   ├── 00_explore.ipynb
│   ├── 01_bronze_ingest.ipynb
│   ├── 02_silver_clean.ipynb
│   ├── 03_gold_kpis.ipynb
│   ├── 04_streaming_bronze_ingest.ipynb
│   └── 05_streaming_silver_clean.ipynb
│
├── airflow_local/
│   └── dags/
│       └── api_logs_databricks_run.py
│
├── dbt/
│   ├── models/
│   └── marts/
│
└── docs/
    └── screenshots/
```

---

# How to Run

## 1. Generate Synthetic Logs

```bash
python scripts/generate_logs.py \
  --date 2026-04-23 \
  --hour 09 \
  --rows 250 \
  --late-rate 0 \
  --dup-rate 0.02 \
  --bad-rate 0.01 \
  --seed 1 \
  --out sample_data/raw/
```

## 2. Upload Files to Databricks Volume

```text
/Volumes/workspace/api_logs_schema/api_logs_volume/
```

## 3. Run Databricks Notebooks

```text
00_explore.ipynb
01_bronze_ingest.ipynb
02_silver_clean.ipynb
03_gold_kpis.ipynb
```

## 4. Create Databricks Workflow

```text
bronze_ingest → silver_clean → gold_kpis
```

## 5. Run Airflow DAG

```text
api_logs_databricks_run
```

---

# Screenshots

Add screenshots for:

* Databricks workflow DAG
* Airflow DAG
* Delta tables
* KPI query results
* streaming checkpoints
* quarantine table examples

---

# Key Concepts Demonstrated

## Data Engineering

* medallion architecture
* Delta Lake pipelines
* schema enforcement
* data quality validation
* late-arriving event handling
* incremental ingestion

## Streaming & Platform Engineering

* Auto Loader ingestion
* checkpoint management
* triggered micro-batches
* replayable raw storage
* operational telemetry workflows

## Analytics Engineering

* dbt marts
* service-level KPIs
* latency percentile analysis
* operational reporting datasets

---

# Status

Completed end-to-end implementation including:

* synthetic data generation
* Bronze / Silver / Gold layers
* streaming ingestion extension
* quarantine workflows
* dbt marts
* Databricks orchestration
* Airflow scheduling and backfill support
* scale validation on ~1.28M records
