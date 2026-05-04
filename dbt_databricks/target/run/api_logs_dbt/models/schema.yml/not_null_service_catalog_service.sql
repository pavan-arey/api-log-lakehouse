
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select service
from `workspace`.`gold_dbt_gold_dbt`.`service_catalog`
where service is null



  
  
      
    ) dbt_internal_test