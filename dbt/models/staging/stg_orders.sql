-- One row per order: timestamps typed, the promised date kept as a date.
select
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp::timestamp       as purchased_at,
    order_delivered_customer_date::timestamp  as delivered_at,
    order_estimated_delivery_date::date       as promised_date
from {{ source('raw', 'orders') }}
