-- One row per product, with its category code (empty when the product has none).
select
    product_id,
    product_category_name as category_code
from {{ source('bronze', 'products') }}
