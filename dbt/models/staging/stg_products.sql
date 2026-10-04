-- One row per product. The department is the product category in English; two categories
-- have no English name (kept in Portuguese) and products without a category get 'unknown'.
select
    p.product_id,
    replace(coalesce(t.product_category_name_english, p.product_category_name, 'unknown'), '_', ' ') as department,
    p.product_weight_g::int as weight_g
from {{ source('raw', 'products') }} p
left join {{ source('raw', 'category_translation') }} t
    on t.product_category_name = p.product_category_name
