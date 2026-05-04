
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    service as unique_field,
    count(*) as n_records

from `workspace`.`gold_dbt_gold_dbt`.`service_catalog`
where service is not null
group by service
having count(*) > 1



  
  
      
    ) dbt_internal_test