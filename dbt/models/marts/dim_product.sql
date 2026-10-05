-- One row per product, with its department.
select product_id, department
from {{ ref('stg_products') }}
