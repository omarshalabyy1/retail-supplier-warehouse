-- One row per calendar day, whole years around the first and last order. Mark as the date table in Power BI.
with bounds as (
    select date_trunc('year', min(purchased_at))::date as first_day,
           (date_trunc('year', max(purchased_at)) + interval '1 year - 1 day')::date as last_day
    from {{ ref('orders') }}
)
select
    d::date                              as date,
    extract(year from d)::int            as year,
    extract(quarter from d)::int         as quarter,
    extract(month from d)::int           as month_number,
    to_char(d, 'Mon')                    as month_name,
    to_char(d, 'YYYY-MM')                as year_month,
    extract(isodow from d)::int          as weekday_number,
    to_char(d, 'Dy')                     as weekday_name
from bounds, generate_series(bounds.first_day, bounds.last_day, interval '1 day') as d
