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

## Mark the date table

Select `dim_date` → **Table tools → Mark as date table** → date column `date` → **OK**.

## Relationships

Power BI may create some automatically. Delete any it made, then drag each one yourself (**Manage relationships → New** works too):

| From (many) | To (one) | Cardinality | Cross-filter direction |
|---|---|---|---|
| `fact_order_items[product_id]` | `dim_product[product_id]` | Many to one | Single |
| `fact_order_items[seller_id]` | `dim_seller[seller_id]` | Many to one | Single |
| `fact_order_items[customer_id]` | `dim_customer[customer_id]` | Many to one | Single |
| `fact_order_items[order_date]` | `dim_date[date]` | Many to one | Single |

All four are active. Single direction keeps filters flowing from the dimensions into the fact, never back.

## Sort-by columns

Select the column, then **Column tools → Sort by column**:

| Column | Sort by |
|---|---|
| `dim_date[month_name]` | `dim_date[month_number]` |
| `dim_date[weekday_name]` | `dim_date[weekday_number]` |

## Hide

Right-click → **Hide in report view**. Report users pick fields from the dimensions and the measures only.

- In `fact_order_items`: `product_id`, `seller_id`, `customer_id`, `order_date`, `price`, `freight`, `delivery_days`, `review_score`, `order_item_id`.
- In `dim_customer`: `customer_id`.

Keep visible in the fact: `order_id`, `order_status`, `is_delivered`, `is_late`, `promised_date`, `delivered_date` (used in slicers and tables).

## Measures table and display folders

1. **Home → Enter data**, name the table `Measures`, **Load**.
2. Create every measure in `03-measures.dax` on this table (**Table tools → New measure**).
3. For each measure set **Measure tools → Display folder** to the folder named in its comment (`Sales`, `Delivery`, `Suppliers`) and the **Format** shown.
4. Delete the `Column1` column of `Measures`; the table then shows at the top of the Data pane with a calculator icon.
