with src as (
    select * from {{ source('silver','silver_api_logs_clean') }}
)
select
    request_id,
    cast(event_time as timestamp) as event_time,
    to_date(cast(event_time as timestamp)) as event_date,
    hour(cast(event_time as timestamp)) as event_hour,
    service,
    endpoint,
    method,
    cast(status_code as int) as status_code,
    cast(latency_ms as bigint) as latency_ms,
    cast(bytes_in as bigint) as bytes_in,
    cast(bytes_out as bigint) as bytes_out,
    client_type,
    region,
    host,
    case when cast(status_code as int) between 400 and 499 then 1 else 0 end as is_client_error,
    case when cast(status_code as int) >= 500 then 1 else 0 end as is_server_error
from src