# API Log Lakehouse (Databricks + Delta)

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

## Tables (Medallion Architecture)

### Bronze

* `bronze.api_logs_raw`

  * Raw JSON logs stored as text (`raw_payload`)
  * Includes ingestion metadata (`ingest_ts`, `source_file`)

### Silver

* `silver.api_logs_clean`

  * Parsed, validated, deduplicated records
* `silver.api_logs_quarantine`

  * Invalid or malformed records

### Gold

* `gold.service_daily_kpis`

  * Aggregated service-level metrics (error rate, latency, SLA breaches)

---

## Data Quality Definitions

* **Late data**
  Records where `event_time` belongs to a previous day but arrive in a later ingest batch.

* **Bad data**
  Invalid records such as:

  * missing `request_id`
  * negative `latency_ms`
  * invalid `status_code`

* **Duplicate data**
  Multiple records with the same `request_id`.

---

## Business Questions

1. Which services had the highest error rate each day?
2. Which endpoints had the highest p95 latency?
3. Which services breached SLA most often?
