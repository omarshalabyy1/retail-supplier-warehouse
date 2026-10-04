# 6. Checks

Once the report is built, every number below must match, with the year slicer on **Select all** unless the row says otherwise. They come from `analysis/analysis.ipynb` and from the SQL under each table (run it in any SQL tool against `localhost:5441`, database `warehouse`). If a number is off, the cause is in the measure or the model step named in the last column.

Data as loaded on 2026-10-04: orders from 2016-09-04 to 2018-09-03.

## Page 1: Sales

| Visual | Must show | If not, check |
|---|---|---|
| Sales card | 13.59M (13,591,643.70) | `Sales` sums `price`, not `price + freight` |
| Orders card | 98,666 | `Orders` is a distinct count of `order_id`, not a row count |
| Average Order Value card | 137.75 | |
| Freight % of Sales card | 16.6% | |
| Top department by sales | health beauty, 1,258,681.34 | `dim_product` relationship is many to one, single direction |
| Year slicer = 2017 | Sales 6,155,806.98; Orders 44,579 | `dim_date` is marked as date table; relationship on `order_date` |
| Year slicer = 2018 | Sales 7,386,050.80; Orders 53,775 | |

```sql
select sum(price) as sales, count(distinct order_id) as orders,
       sum(price) / count(distinct order_id) as average_order_value,
       sum(freight) / sum(price) as freight_share
from marts.fact_order_items;

select extract(year from order_date) as year, sum(price) as sales, count(distinct order_id) as orders
from marts.fact_order_items group by 1 order by 1;
```

## Page 2: Suppliers

| Visual | Must show | If not, check |
|---|---|---|
| Sellers card | 3,095 | |
| Late Item Rate card | 6.6% (7,264 late of 110,189 delivered items) | `Delivered Items` and `Late Items` filter on `is_delivered` and `is_late` |
| Top 100 sellers late share card | 50.4% | Both `TOPN` calls break ties by `seller_id` |
| Top 100 sellers delivered share card | 41.6% | |
| Table, first row | seller 4a3ca9315b744ce9f8e9374361493884: 1,949 delivered, 189 late, 9.7% | Table sorted by `Late Items` descending |
| Table, second row | seller 1f50f920176fa81dab994f9023523100: 1,926 delivered, 150 late, 7.8% | |
| Click a state in the bar chart | the two top-100 cards stay at 50.4% and 41.6% | Both measures use `REMOVEFILTERS ( dim_seller )` |

```sql
with sellers as (
    select seller_id,
           count(*) filter (where is_delivered) as delivered_items,
           count(*) filter (where is_late)      as late_items,
           row_number() over (order by count(*) filter (where is_late) desc, seller_id) as late_rank
    from marts.fact_order_items
    group by seller_id
)
select sum(late_items) filter (where late_rank <= 100)::numeric / sum(late_items)           as top_100_late_share,
       sum(delivered_items) filter (where late_rank <= 100)::numeric / sum(delivered_items) as top_100_delivered_share
from sellers;
```

## Page 3: Late deliveries

| Visual | Must show | If not, check |
|---|---|---|
| Late Order Rate card | 6.8% (6,534 late of 96,470 delivered orders) | |
| Late Orders card | 6,534 | |
| Average Delivery Days card | 12.5 | Measure counts each delivered order once |
| Average Review card | 4.10 | Measure counts each reviewed order once, not each item |
| Column chart | False (on time) 4.29; True (late) 2.27 | Visual filter `is_delivered` is True |
| Year slicer = 2016 / 2017 / 2018 | Late Order Rate 1.1% / 5.6% / 7.7% | |
| Department bar chart, top bar | health beauty, 7.6% | Top N filter is by `Delivered Items`, sort by `Late Item Rate` |

```sql
select count(distinct order_id) filter (where is_late)::numeric
       / count(distinct order_id) filter (where is_delivered) as late_order_rate
from marts.fact_order_items;

select is_late, avg(review_score) as average_review
from (select distinct order_id, is_late, review_score
      from marts.fact_order_items
      where is_delivered and review_score is not null) o
group by is_late;
```
