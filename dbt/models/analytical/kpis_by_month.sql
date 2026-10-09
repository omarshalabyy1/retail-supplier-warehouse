-- One row per order month: sales and delivery counts. An order has one order date, so every column
-- adds up across months to the all-time total. Sales are item prices without freight, any status.
select
    d.year_month,
    sum(f.price)                                          as sales,
    sum(f.freight)                                        as freight,
    count(distinct f.order_id)                            as orders,
    count(*)                                              as items,
    count(distinct f.order_id) filter (where f.is_delivered) as delivered_orders,
    count(distinct f.order_id) filter (where f.is_late)   as late_orders,
    count(*) filter (where f.is_delivered)                as delivered_items,
    count(*) filter (where f.is_late)                     as late_items
from {{ ref('fact_order_items') }} f
join {{ ref('dim_date') }} d on d.date = f.order_date
group by d.year_month
