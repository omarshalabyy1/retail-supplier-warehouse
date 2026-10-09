-- One row per order: the delivery rules.
-- is_delivered: status 'delivered' with a delivery date.
-- is_late: delivered more than var('late_after_days') days (dbt_project.yml) after the promised date;
-- null while the order is not delivered.
select
    order_id,
    delivered_at is not null and order_status = 'delivered' as is_delivered,
    case when delivered_at is not null and order_status = 'delivered'
         then delivered_at::date > promised_date + {{ var('late_after_days') }} end as is_late,
    delivered_at::date - purchased_at::date as delivery_days
from {{ ref('orders') }}
