-- A price or freight below zero means the export is broken.
select order_id, order_item_id, price, freight
from {{ ref('fact_order_items') }}
where price < 0 or freight < 0
