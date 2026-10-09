-- One row per seller: delivered and late items, with the seller's late rank and top-seller flag.
-- Counted per item, because one order can hold items from several sellers.
select
    s.seller_id,
    s.state,
    s.late_rank,
    s.is_top_late_seller,
    count(f.order_id) filter (where f.is_delivered) as delivered_items,
    count(f.order_id) filter (where f.is_late)      as late_items
from {{ ref('dim_seller') }} s
left join {{ ref('fact_order_items') }} f using (seller_id)
group by s.seller_id, s.state, s.late_rank, s.is_top_late_seller
