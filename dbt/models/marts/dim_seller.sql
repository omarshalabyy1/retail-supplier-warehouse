-- One row per seller: the suppliers that sell through the store.
select seller_id, zip_prefix, city, state
from {{ ref('stg_sellers') }}
