-- One row per seller: the suppliers that sell through the store.
-- late_rank orders sellers by their late items over all time (ties broken by seller_id); the first
-- var('top_sellers') of them (dbt_project.yml) are the "top sellers" of the report.
-- A dimension attribute derived from the fact, so the notebook, the SQL checks and Power BI share one ranking.
with late as (
    select seller_id, count(*) filter (where is_late) as late_items
    from {{ ref('fact_order_items') }}
    group by seller_id
), ranked as (
    select s.seller_id, s.zip_prefix, s.city, s.state,
           row_number() over (order by coalesce(l.late_items, 0) desc, s.seller_id) as late_rank
    from {{ ref('stg_sellers') }} s
    left join late l using (seller_id)
)
select seller_id, zip_prefix, city, state, late_rank,
       late_rank <= {{ var('top_sellers') }} as is_top_late_seller
from ranked
