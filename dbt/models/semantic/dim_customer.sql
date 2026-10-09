-- One row per customer_id (one per order); customer_unique_id counts real people.
select customer_id, customer_unique_id, zip_prefix, city, state
from {{ ref('customers') }}
