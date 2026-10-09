-- One row per delivery outcome of a delivered, reviewed order ('On time', 'Late'):
-- each order counted once, with its latest review.
select
    case when is_late then 'Late' else 'On time' end as delivery,
    count(*)                                          as reviewed_orders,
    avg(review_score)                                 as average_review
from (select distinct order_id, is_late, review_score
      from {{ ref('fact_order_items') }}
      where is_delivered and review_score is not null) o
group by 1
