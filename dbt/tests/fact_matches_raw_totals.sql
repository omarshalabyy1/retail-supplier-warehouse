-- Nothing lost or doubled between the raw file and the fact: same rows, same sales, same freight.
with raw as (
    select count(*) as item_rows, sum(price::numeric) as sales, sum(freight_value::numeric) as freight
    from {{ source('raw', 'order_items') }}
), fact as (
    select count(*) as item_rows, sum(price) as sales, sum(freight) as freight
    from {{ ref('fact_order_items') }}
)
select * from raw, fact
where raw.item_rows <> fact.item_rows or raw.sales <> fact.sales or raw.freight <> fact.freight
