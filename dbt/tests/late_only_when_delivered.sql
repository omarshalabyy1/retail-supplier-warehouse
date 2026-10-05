-- An order can only be late once it is delivered.
select order_id, order_item_id
from {{ ref('fact_order_items') }}
where is_late and not is_delivered
