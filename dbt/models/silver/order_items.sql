-- One row per item in an order. Amounts in Brazilian reais (BRL).
select
    order_id,
    order_item_id::int                as order_item_id,
    product_id,
    seller_id,
    price::numeric(12, 2)             as price,
    freight_value::numeric(12, 2)     as freight
from {{ source('bronze', 'order_items') }}
