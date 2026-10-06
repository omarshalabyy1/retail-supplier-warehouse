# 1. Power Query

Five queries read the five tables of the `marts` schema. One extra query, `Warehouse`, holds the connection, so the server name is typed once.

**Before you start:** the warehouse is running (`docker compose up -d`) and has been loaded and built once (main README), so the `marts` tables exist.

## Connect

1. Power BI Desktop → **Home → Get data → Blank query**. The Power Query editor opens.
2. **Home → Advanced Editor**, paste the query, **Done**.
3. Rename the query (right pane, **Name**) to the name in the heading.
4. The first time, Power BI asks for credentials: choose **Database**, user `warehouse`, password `warehouse`. If it says it can't connect with encryption, choose **OK** to connect without it (the database only listens on your own computer).

Repeat steps 1 to 3 for each query below.

## Warehouse (staging only, not loaded)

The warehouse from `docker-compose.yml`: port 5441, database `warehouse`. Credentials: user `warehouse`, password `warehouse`.

```m
let
    Source = PostgreSQL.Database("127.0.0.1:5441", "warehouse")
in
    Source
```

Right-click `Warehouse` → untick **Enable load**. It only feeds the other queries.

## fact_order_items

```m
let
    Source = Warehouse,
    Table = Source{[Schema = "marts", Item = "fact_order_items"]}[Data],
    Typed = Table.TransformColumnTypes(Table, {
        {"order_id", type text},
        {"order_item_id", Int64.Type},
        {"product_id", type text},
        {"seller_id", type text},
        {"customer_id", type text},
        {"order_date", type date},
        {"order_status", type text},
        {"price", Currency.Type},
        {"freight", Currency.Type},
        {"promised_date", type date},
        {"delivered_date", type date},
        {"is_delivered", type logical},
        {"is_late", type logical},
        {"delivery_days", Int64.Type},
        {"review_score", Int64.Type}
    })
in
    Typed
```

## dim_product

```m
let
    Source = Warehouse,
    Table = Source{[Schema = "marts", Item = "dim_product"]}[Data],
    Typed = Table.TransformColumnTypes(Table, {
        {"product_id", type text},
        {"department", type text}
    })
in
    Typed
```

## dim_seller

```m
let
    Source = Warehouse,
    Table = Source{[Schema = "marts", Item = "dim_seller"]}[Data],
    Typed = Table.TransformColumnTypes(Table, {
        {"seller_id", type text},
        {"zip_prefix", type text},
        {"city", type text},
        {"state", type text},
        {"late_rank", Int64.Type},
        {"is_top_late_seller", type logical}
    })
in
    Typed
```

## dim_customer

```m
let
    Source = Warehouse,
    Table = Source{[Schema = "marts", Item = "dim_customer"]}[Data],
    Typed = Table.TransformColumnTypes(Table, {
        {"customer_id", type text},
        {"customer_unique_id", type text},
        {"zip_prefix", type text},
        {"city", type text},
        {"state", type text}
    })
in
    Typed
```

## dim_date

```m
let
    Source = Warehouse,
    Table = Source{[Schema = "marts", Item = "dim_date"]}[Data],
    Typed = Table.TransformColumnTypes(Table, {
        {"date", type date},
        {"year", Int64.Type},
        {"quarter", Int64.Type},
        {"month_number", Int64.Type},
        {"month_name", type text},
        {"year_month", type text},
        {"weekday_number", Int64.Type},
        {"weekday_name", type text}
    })
in
    Typed
```

## Load

**Home → Close & Apply.** Five tables load; `Warehouse` does not. The zip prefixes stay text so leading zeros survive.

After a new `dbt run`, **Home → Refresh** brings in the new data.
