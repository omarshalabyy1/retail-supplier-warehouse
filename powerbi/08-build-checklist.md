# 8. Build checklist

Follow it top to bottom. **Check** lines are the numbers you must see before moving on; if one is off, `06-checks.md` says where to look.

## Before Power BI

1. In the repo folder, start the warehouse:
   ```bash
   docker compose up -d
   ```
2. Load and build it (README, How to run it, step 4). **Check:** `dbt run` ends with `PASS=11` and no errors.

## Power BI Desktop

3. Open Power BI Desktop → **Blank report**. **File → Options and settings → Options → Current file → Data load** → untick **Auto date/time** → OK (`02-model.md`, Date table).
4. **Power Query** (`01-power-query.md`): create `Warehouse` (load off), then `fact_order_items`, `dim_product`, `dim_seller`, `dim_customer`, `dim_date` → **Close & Apply**.
   **Check** (Table view, row count bottom left): `fact_order_items` 112,650 · `dim_product` 32,951 · `dim_seller` 3,095 · `dim_customer` 99,441 · `dim_date` 1,096.
5. **Model** (`02-model.md`): mark `dim_date` as date table, the four relationships, column formats, sort-by columns, hidden columns.
   **Check:** Model view shows four many-to-one lines, all ending on `fact_order_items`, single arrows pointing to the fact.
6. **Measures** (`02-model.md` last section, then `03-measures.dax`): create the `Measures` table, paste the 18 measures in file order, set each folder and format, delete `Column1`.
   **Check** (drop each into a temporary card, then delete it): `Items` 112,650 · `Delivered Items` 110,189 · `Late Items` 7,264 · `Sales` 13,591,643.70.
7. **Theme** (`05-theme.json`): **View → Themes → Browse for themes** → pick the file. **Check:** the page background turns light grey-blue.

## Pages (`04-pages.md`)

8. Page 1 **Sales**: canvas 16:9, then Px-T, Px-S, P1-V1 to P1-V6 in order.
   **Check:** Sales 13.59M · Orders 98,666 · Average Order Value 137.75 · Freight % of Sales 16.6% · top department bar health beauty.
9. Copy Px-T and Px-S to a new page **Suppliers** (choose **Sync**), then P2-V1 to P2-V6.
   **Check:** Sellers 3,095 · Late Item Rate 6.6% · Top sellers late share 50.4% · Top sellers delivered share 41.6% · table first row seller 4a3ca9315b744ce9f8e9374361493884 with 1,949 delivered, 189 late, 9.7%.
10. Copy Px-T and Px-S to a new page **Late deliveries** (choose **Sync**), then P3-V1 to P3-V7.
    **Check:** Late Order Rate 6.8% · Late Orders 6,534 · Average Delivery Days 12.5 · Average Review 4.10 · review chart False 4.29, True 2.27 · top department bar health beauty 7.6%.
11. **View → Sync slicers**: `year` synced and visible on all three pages. Click **2017** on any page.
    **Check:** Sales 6,155,806.98 · Orders 44,579 · Late Order Rate 5.6%. Then 2016: 1.1%; 2018: 7.7%. Set it back to **Select all**.

## Interactions and save

12. **Interactions** (`07-interactions.md`): set the three matrices.
    **Check:** on Suppliers, click a state bar: the table shows only that state's sellers, the two top-seller cards stay at 50.4% and 41.6%. On Late deliveries, click a column of the review chart: nothing else changes.
13. **File → Save as** `powerbi/retail-supplier-warehouse.pbix`.
14. Run every SQL query in `06-checks.md` (any SQL tool on `127.0.0.1:5441`, database `warehouse`). **Check:** each result matches its page.

## Screenshots and finish

15. Year slicer on **Select all**, nothing clicked. For each page: Win + Shift + S → window snip of the report canvas → save as `powerbi/screenshots/1-sales.png`, `2-suppliers.png`, `3-late-deliveries.png`.
16. Commit the `.pbix` and the three screenshots; the README's Power BI section then shows them.
17. Stop the stack and remove its data (the repo rebuilds it):
    ```bash
    docker compose down -v
    ```
