-- Grain: one row per item in an order (order_id, order_item_id).
-- Order-level facts (status, dates, lateness, review) repeat on each item of the order.
-- is_delivered, is_late and delivery_days are the Gold layer's delivery rules (gold.order_delivery).
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
    d.is_delivered,
    d.is_late,
    d.delivery_days,
    r.review_score
from {{ ref('order_items') }} i
join {{ ref('orders') }} o on o.order_id = i.order_id
join {{ ref('order_delivery') }} d on d.order_id = i.order_id
left join {{ ref('reviews') }} r on r.order_id = i.order_id
