-- One row per seller (the retailer's suppliers). The zip prefix stays text to keep leading zeros.
select
    seller_id,
    seller_zip_code_prefix   as zip_prefix,
    initcap(trim(seller_city)) as city,
    upper(trim(seller_state))  as state
from {{ source('bronze', 'sellers') }}
