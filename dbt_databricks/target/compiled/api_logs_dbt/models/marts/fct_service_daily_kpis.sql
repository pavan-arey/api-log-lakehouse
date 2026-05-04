with logs as(
    select * from `workspace`.`gold_dbt`.`stg_api_logs_clean`
),

svc as(
    select 
        service,
        team,
        cast(sla_ms as int) as sla_ms,
        criticality
    from `workspace`.`gold_dbt_gold_dbt`.`service_catalog`
)

select
    l.event_date,
    l.service,
    s.team,
    s.criticality,
    count(*) as total_requests,
    sum(l.is_client_error) as client_error_requests,
    sum(l.is_server_error) as server_error_requests,
    round(
        1.0 * (sum(l.is_client_error) + sum(l.is_server_error)) / count(*),
        4
    ) as error_rate,
    round(avg(l.latency_ms), 2) as avg_latency_ms,
    percentile_approx(l.latency_ms, 0.95) as p95_latency_ms,
    sum(case when l.latency_ms > s.sla_ms then 1 else 0 end) as sla_breach_requests,
    sum(l.bytes_out) as total_bytes_out
from logs l
left join svc s
    on l.service = s.service

group by 
    l.event_date,
    l.service,
    s.team,
    s.criticality