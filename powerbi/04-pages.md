# 4. Pages

Three pages, each 1280 × 720 (**Format page → Canvas settings → 16:9**). Apply the theme first: **View → Themes → Browse for themes →** `05-theme.json`.

Positions are in pixels (**Format → General → Properties → Size and position**). Cards show the measure only; set **Category label** on so the measure name shows under the number.

## Every page

| Visual | Position (x, y, w, h) | Fields | Settings |
|---|---|---|---|
| Text box (title) | 20, 16, 800, 44 | The page name | Segoe UI Semibold 20, colour #0E1630 |
| Slicer | 980, 16, 280, 44 | `dim_date[year]` | Style **Tile**, single select off, **Select all** on |

Sync the year slicer across the three pages: select it → **View → Sync slicers** → tick **Sync** and **Visible** for all pages.

No drill-through and no bookmarks: the three pages answer three questions and the year slicer filters all of them.

## Page 1: Sales

*How much did the store sell, and in which departments?*

| Visual | Position (x, y, w, h) | Fields | Sort and formatting |
|---|---|---|---|
| Card | 20, 72, 295, 100 | `Sales` | Display units **Millions**, 2 decimals |
| Card | 335, 72, 295, 100 | `Orders` | Display units **None** |
| Card | 650, 72, 295, 100 | `Average Order Value` | 2 decimals |
| Card | 965, 72, 295, 100 | `Freight % of Sales` | |
| Line chart | 20, 188, 820, 512 | X: `dim_date[year_month]`; Y: `Sales` | Sort by `year_month` ascending; title "Sales by month"; line colour #2563EB |
| Bar chart (clustered) | 856, 188, 404, 512 | Y: `dim_product[department]`; X: `Sales` | Visual filter on `department`: **Top N**, show top 10 by `Sales`; sort by `Sales` descending; title "Top 10 departments by sales"; data labels on |

Tooltips: default (the fields in the visual).

## Page 2: Suppliers

*Which sellers cause the late deliveries, and is it more than their size?*

| Visual | Position (x, y, w, h) | Fields | Sort and formatting |
|---|---|---|---|
| Card | 20, 72, 295, 100 | `Sellers` | Display units **None** |
| Card | 335, 72, 295, 100 | `Late Item Rate` | |
| Card | 650, 72, 295, 100 | `Top 100 Sellers Late Share` | Title "Late items from the top 100 sellers" |
| Card | 965, 72, 295, 100 | `Top 100 Sellers Delivered Share` | Title "Delivered items from the same 100" |
| Table | 20, 188, 820, 512 | `dim_seller[seller_id]`, `dim_seller[state]`, `Delivered Items`, `Late Items`, `Late Item Rate`, `Share of All Late Items`, `Average Review` | Sort by `Late Items` descending; **Conditional formatting → Data bars** on `Late Items` (bar colour #2563EB); **Background colour → Gradient** on `Late Item Rate` (lowest #FFFFFF, highest #FCA5A5); title "Sellers by late items" |
| Bar chart (clustered) | 856, 188, 404, 512 | Y: `dim_seller[state]`; X: `Late Item Rate` | Visual filter: `Delivered Items` **is greater than or equal to** 500 (leaves out states with too few items to judge); sort by `Late Item Rate` descending; title "Late item rate by seller state"; data labels on |

Tooltips on the table rows: default.

## Page 3: Late deliveries

*How often are orders late, and what does it cost?*

| Visual | Position (x, y, w, h) | Fields | Sort and formatting |
|---|---|---|---|
| Card | 20, 72, 295, 100 | `Late Order Rate` | |
| Card | 335, 72, 295, 100 | `Late Orders` | Display units **None** |
| Card | 650, 72, 295, 100 | `Average Delivery Days` | 1 decimal |
| Card | 965, 72, 295, 100 | `Average Review` | 2 decimals |
| Column chart (clustered) | 20, 188, 400, 512 | X: `fact_order_items[is_late]`; Y: `Average Review` | Visual filter: `is_delivered` **is** True; sort by `is_late` ascending (False = on time, True = late); data labels on, 2 decimals; Y axis from 0 to 5; title "Average review: on time (False) vs late (True)" |
| Line chart | 436, 188, 824, 250 | X: `dim_date[year_month]`; Y: `Late Order Rate` | Sort by `year_month` ascending; title "Late order rate by month" |
| Bar chart (clustered) | 436, 454, 824, 246 | Y: `dim_product[department]`; X: `Late Item Rate` | Visual filter on `department`: **Top N**, top 10 by `Delivered Items`; sort by `Late Item Rate` descending; title "Late item rate, ten biggest departments"; data labels on |

## Interactions

Leave the defaults: clicking a bar or a table row cross-filters the other visuals on the same page. On page 2, check that clicking a state in the bar chart filters the table to that state's sellers, while the two "top 100" cards stay the same (they ignore the seller filter by design).

## Save

**File → Save as** `powerbi/retail-supplier-warehouse.pbix`. Then follow `06-checks.md`, and save one screenshot per page in `powerbi/screenshots/` (`1-sales.png`, `2-suppliers.png`, `3-late-deliveries.png`).
