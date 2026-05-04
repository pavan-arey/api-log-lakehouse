
    
    

select
    service as unique_field,
    count(*) as n_records

from `workspace`.`gold_dbt_gold_dbt`.`service_catalog`
where service is not null
group by service
having count(*) > 1


