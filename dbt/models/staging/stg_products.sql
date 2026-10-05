-- One row per product, with its department from the client's departments file
-- (load.py stops if a category has no department). Products without a category get 'unknown'.
select
    p.product_id,
    coalesce(d.department, 'unknown') as department
from {{ source('raw', 'products') }} p
left join {{ source('raw', 'departments') }} d
    on d.category_code = p.product_category_name
