-- Grain: one row per item in an order (order_id, order_item_id).
-- Order-level facts (status, dates, lateness, review) repeat on each item of the order.
-- is_late: delivered more than var('late_after_days') days after the promised date (rules.late_after_days
-- in config/client.yaml); null while the order is not delivered. Status 'delivered' marks a delivered order.
select
    i.order_id,
    i.order_item_id,
    i.product_id,
    i.seller_id,
    o.customer_id,
    o.purchased_at::date                         as order_date,
    o.order_status,
    i.price,
    i.freight,
    o.promised_date,
    o.delivered_at::date                         as delivered_date,
    o.delivered_at is not null
        and o.order_status = 'delivered'         as is_delivered,
    case when o.delivered_at is not null and o.order_status = 'delivered'
         then o.delivered_at::date > o.promised_date + {{ var('late_after_days') }} end as is_late,
    o.delivered_at::date - o.purchased_at::date  as delivery_days,
    r.review_score
from {{ ref('stg_order_items') }} i
join {{ ref('stg_orders') }} o on o.order_id = i.order_id
left join {{ ref('stg_reviews') }} r on r.order_id = i.order_id
