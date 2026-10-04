-- One row per order: some orders were reviewed more than once, keep the latest review.
select distinct on (order_id)
    order_id,
    review_score::int                  as review_score,
    review_creation_date::timestamp    as reviewed_at
from {{ source('raw', 'reviews') }}
order by order_id, review_creation_date::timestamp desc, review_answer_timestamp::timestamp desc
