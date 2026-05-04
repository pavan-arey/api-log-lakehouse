with logs as (

    select * from `workspace`.`gold_dbt`.`stg_api_logs_clean`

)

select
    event_date,
    event_hour,
    service,
    endpoint,
    count(*) as total_requests,
    round(
        1.0 * (sum(is_client_error) + sum(is_server_error)) / count(*),
        4
    ) as error_rate,
    round(avg(latency_ms), 2) as avg_latency_ms,
    percentile_approx(latency_ms, 0.95) as p95_latency_ms,
    sum(bytes_out) as total_bytes_out

from logs
group by
    event_date,
    event_hour,
    service,
    endpoint