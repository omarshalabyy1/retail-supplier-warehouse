-- One row per product, with its department.
select product_id, department, weight_g
from {{ ref('stg_products') }}
