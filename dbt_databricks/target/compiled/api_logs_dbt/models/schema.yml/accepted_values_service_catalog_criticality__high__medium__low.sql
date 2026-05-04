
    
    

with all_values as (

    select
        criticality as value_field,
        count(*) as n_records

    from `workspace`.`gold_dbt_gold_dbt`.`service_catalog`
    group by criticality

)

select *
from all_values
where value_field not in (
    'high','medium','low'
)


