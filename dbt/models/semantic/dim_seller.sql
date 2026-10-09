-- One row per seller: the suppliers that sell through the store, with their late rank from the Gold layer.
select s.seller_id, s.zip_prefix, s.city, s.state, r.late_rank, r.is_top_late_seller
from {{ ref('sellers') }} s
join {{ ref('seller_late_rank') }} r using (seller_id)
