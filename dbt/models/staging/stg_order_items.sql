-- One row per item in an order. Amounts in the store's currency (BRL).
select
    order_id,
    order_item_id::int                as order_item_id,
    product_id,
    seller_id,
    shipping_limit_date::timestamp    as ship_by_at,
    price::numeric(12, 2)             as price,
    freight_value::numeric(12, 2)     as freight
from {{ source('raw', 'order_items') }}
