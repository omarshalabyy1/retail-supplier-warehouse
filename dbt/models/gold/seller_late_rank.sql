-- One row per seller: late items over all time, and the rank by them (ties broken by seller_id).
-- The first var('top_sellers') of them (dbt_project.yml) are the "top sellers" of the report.
-- Built from Silver order items and the Gold delivery rules, so the notebook, the SQL checks and
-- Power BI share one ranking.
with late as (
    select i.seller_id, count(*) filter (where d.is_late) as late_items
    from {{ ref('order_items') }} i
    join {{ ref('order_delivery') }} d using (order_id)
    group by i.seller_id
), ranked as (
    select s.seller_id,
           coalesce(l.late_items, 0) as late_items,
           row_number() over (order by coalesce(l.late_items, 0) desc, s.seller_id) as late_rank
    from {{ ref('sellers') }} s
    left join late l using (seller_id)
)
select seller_id, late_items, late_rank,
       late_rank <= {{ var('top_sellers') }} as is_top_late_seller
from ranked
