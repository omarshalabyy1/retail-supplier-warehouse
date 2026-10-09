-- One row per customer_id (a new id per order); customer_unique_id is the real person.
select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix   as zip_prefix,
    initcap(trim(customer_city)) as city,
    upper(trim(customer_state))  as state
from {{ source('bronze', 'customers') }}
