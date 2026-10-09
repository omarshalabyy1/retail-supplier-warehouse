-- One row per product, with its department. Products without a category get 'unknown'
-- (load.py stops if a category has no department).
select
    p.product_id,
    coalesce(d.department, 'unknown') as department
from {{ ref('products') }} p
left join {{ ref('departments') }} d using (category_code)
