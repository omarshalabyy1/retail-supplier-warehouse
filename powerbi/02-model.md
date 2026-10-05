# 2. The model

A star schema: one fact table in the middle, four dimensions around it. Build it in **Model view** (the third icon on the left).

## Tables

| Table | Grain (one row per) | Key |
|---|---|---|
| `fact_order_items` | item in an order | `order_id` + `order_item_id` |
| `dim_product` | product | `product_id` |
| `dim_seller` | seller (supplier) | `seller_id` |
| `dim_customer` | customer_id (a new one per order) | `customer_id` |
| `dim_date` | calendar day | `date` |

Order-level columns (`order_status`, the dates, `is_late`, `delivery_days`, `review_score`) repeat on every item of the same order. The measures that count orders or average review scores take each order once.

## Date table

`dim_date` comes from the warehouse (query in `01-power-query.md`): one row per day for whole calendar years, 2016-01-01 to 2018-12-31 (1,096 days), so every order date has a row.

1. Select `dim_date` → **Table tools → Mark as date table** → date column `date` → **OK**. Why: time functions and the date slicer then use this table, not hidden copies.
2. **File → Options and settings → Options → Current file → Data load** → untick **Auto date/time**. Why: Power BI otherwise builds a hidden date table for every date column, which bloats the file and competes with `dim_date`.

## Relationships

Power BI may create some automatically. Delete any it made, then drag each one yourself (**Manage relationships → New** works too):

| From (many) | To (one) | Cardinality | Cross-filter direction | Active |
|---|---|---|---|---|
| `fact_order_items[product_id]` | `dim_product[product_id]` | Many to one | Single | Yes |
| `fact_order_items[seller_id]` | `dim_seller[seller_id]` | Many to one | Single | Yes |
| `fact_order_items[customer_id]` | `dim_customer[customer_id]` | Many to one | Single | Yes |
| `fact_order_items[order_date]` | `dim_date[date]` | Many to one | Single | Yes |

Why many to one: each dimension key is unique (tested by dbt), the fact repeats it. Why single direction: filters flow from the dimensions into the fact, never back, so no ambiguous paths. Why only `order_date` to the date table: every page reads by order date; the promised and delivered dates stay plain columns.

## Sort-by columns

Select the column, then **Column tools → Sort by column**:

| Column | Sort by |
|---|---|
| `dim_date[month_name]` | `dim_date[month_number]` |
| `dim_date[weekday_name]` | `dim_date[weekday_number]` |

## Column formats

Select the column → **Column tools → Format**:

| Column | Format |
|---|---|
| `fact_order_items[price]`, `fact_order_items[freight]` | Decimal number, 2 decimals, thousands separator on |
| `fact_order_items[order_date]`, `[promised_date]`, `[delivered_date]`, `dim_date[date]` | Date, `yyyy-mm-dd` |
| `fact_order_items[delivery_days]`, `[review_score]`, `dim_seller[late_rank]` | Whole number |
| `dim_date[year]` | Whole number, thousands separator **off** (shows 2017, not 2,017) |
| `dim_seller[zip_prefix]`, `dim_customer[zip_prefix]` | Text (keeps leading zeros) |

## Hide

Right-click → **Hide in report view**. Report users pick fields from the dimensions and the measures only.

- In `fact_order_items`: `product_id`, `seller_id`, `customer_id`, `order_date`, `price`, `freight`, `delivery_days`, `review_score`, `order_item_id`.
- In `dim_customer`: `customer_id`.
- In `dim_seller`: `late_rank`, `is_top_late_seller` (used by the top-seller measures; set in the warehouse from `rules.top_sellers`, so the notebook, the SQL checks and the report share one ranking).

Keep visible in the fact: `order_id`, `order_status`, `is_delivered`, `is_late`, `promised_date`, `delivered_date` (used on axes and in visual filters).

Why hide the keys and raw amounts: a user who drags `price` gets a plain sum without the rules in the measures; the measures are the one way to read the numbers.

## Measures table and display folders

1. **Home → Enter data**, name the table `Measures`, **Load**.
2. Create every measure in `03-measures.dax` on this table (**Table tools → New measure**).
3. For each measure set **Measure tools → Display folder** to the folder named in its comment (`Sales`, `Delivery`, `Suppliers`) and the **Format** shown.
4. Delete the `Column1` column of `Measures`; the table then shows at the top of the Data pane with a calculator icon.
