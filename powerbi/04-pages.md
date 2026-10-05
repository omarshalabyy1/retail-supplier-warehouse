# 4. Pages

Three pages, each 1280 × 720 (**Format page → Canvas settings → Type: 16:9**). Apply the theme first: **View → Themes → Browse for themes →** `05-theme.json`.

Rename the pages (double-click the tab): `Sales`, `Suppliers`, `Late deliveries`.

Build the visuals in the order listed. Positions are in pixels (**Format → General → Properties → Size and position**). The ID (P1-V1 …) is used in `07-interactions.md`. Wells not listed (Legend, Small multiples, Tooltips) stay empty: tooltips show the visual's own fields.

Cards: use the **Card** visual, **Callout value** = the measure, **Category label** on (shows the measure name, or the title given).

## Every page (build these first on page 1, then copy them to pages 2 and 3)

| ID | Visual | Position (x, y, w, h) | Fields | Settings |
|---|---|---|---|---|
| Px-T | Text box | 20, 16, 800, 44 | The page name | Segoe UI Semibold 20, font colour: theme foreground (first swatch), no border |
| Px-S | Slicer | 980, 16, 280, 44 | Field: `dim_date[year]` | **Slicer settings → Style: Tile**; **Selection: Multi-select with Ctrl** on, **Show "Select all"** on; slicer header off |

Copy both to the other pages with Ctrl+C / Ctrl+V; when Power BI asks, choose **Sync** so the year slicer is one filter across the pages. Then check **View → Sync slicers**: for `year`, **Sync** and **Visible** ticked on all three pages.

## Page 1: Sales

*How much did the store sell, and in which departments?*

| ID | Visual | Position (x, y, w, h) | Fields | Format, sort, labels |
|---|---|---|---|---|
| P1-V1 | Card | 20, 72, 295, 100 | Fields: `Sales` | Callout display units **Millions**, 2 decimals (shows 13.59M) |
| P1-V2 | Card | 335, 72, 295, 100 | Fields: `Orders` | Display units **None** (shows 98,666) |
| P1-V3 | Card | 650, 72, 295, 100 | Fields: `Average Order Value` | Display units None, 2 decimals |
| P1-V4 | Card | 965, 72, 295, 100 | Fields: `Freight % of Sales` | Measure format 0.0% |
| P1-V5 | Line chart | 20, 188, 820, 512 | X-axis: `dim_date[year_month]`; Y-axis: `Sales` | Title "Sales by month"; sort axis by `year_month` ascending (**… → Sort axis**); X-axis type **Categorical**; Y-axis display units Thousands; line colour: theme data colour 1 (the default), width 3; data labels off |
| P1-V6 | Bar chart (clustered) | 856, 188, 404, 512 | Y-axis: `dim_product[department]`; X-axis: `Sales` | Title "Top 10 departments by sales"; visual filter on `department`: **Filter type: Top N → Show items: Top 10 → By value: Sales → Apply**; sort by `Sales` descending; data labels on, display units Thousands; bar colour: theme data colour 1 (the default) |

## Page 2: Suppliers

*Which sellers cause the late deliveries, and is it more than their size?*

| ID | Visual | Position (x, y, w, h) | Fields | Format, sort, labels |
|---|---|---|---|---|
| P2-V1 | Card | 20, 72, 295, 100 | Fields: `Sellers` | Display units **None** (shows 3,095) |
| P2-V2 | Card | 335, 72, 295, 100 | Fields: `Late Item Rate` | 0.0% |
| P2-V3 | Card | 650, 72, 295, 100 | Fields: `Top Sellers Late Share` | 0.0%; category label text: rename the field in the well (double-click) to "Late items from the top sellers" |
| P2-V4 | Card | 965, 72, 295, 100 | Fields: `Top Sellers Delivered Share` | 0.0%; rename in the well to "Delivered items from the same sellers" |
| P2-V5 | Table | 20, 188, 820, 512 | Columns, in this order: `dim_seller[seller_id]`, `dim_seller[state]`, `Delivered Items`, `Late Items`, `Late Item Rate`, `Share of All Late Items`, `Average Review` | Title "Sellers by late items"; sort by `Late Items` descending (click the header); **Cell elements → Late Items → Data bars** on, positive bar: theme data colour 1 (the default); **Cell elements → Late Item Rate → Background colour** on, **Format style: Gradient**, theme gradient as it comes: lowest = theme minimum (white), highest = theme maximum (data colour 1); totals row on |
| P2-V6 | Bar chart (clustered) | 856, 188, 404, 512 | Y-axis: `dim_seller[state]`; X-axis: `Late Item Rate` | Title "Late item rate by seller state"; visual filter: drag `Delivered Items` into **Filters on this visual → Show items when the value: is greater than or equal to** **500** **→ Apply** (leaves out states with too few items to judge); sort by `Late Item Rate` descending; data labels on, 0.0%; bar colour: theme data colour 1 (the default) |

## Page 3: Late deliveries

*How often are orders late, and what does it cost?*

| ID | Visual | Position (x, y, w, h) | Fields | Format, sort, labels |
|---|---|---|---|---|
| P3-V1 | Card | 20, 72, 295, 100 | Fields: `Late Order Rate` | 0.0% |
| P3-V2 | Card | 335, 72, 295, 100 | Fields: `Late Orders` | Display units **None** (shows 6,534) |
| P3-V3 | Card | 650, 72, 295, 100 | Fields: `Average Delivery Days` | 1 decimal |
| P3-V4 | Card | 965, 72, 295, 100 | Fields: `Average Review` | 2 decimals |
| P3-V5 | Column chart (clustered) | 20, 188, 400, 512 | X-axis: `fact_order_items[is_late]`; Y-axis: `Average Review` | Title "Average review: on time (False) vs late (True)"; visual filter: `is_delivered` **Basic filtering → True** only; sort by `is_late` ascending; Y-axis range 0 to 5; data labels on, 2 decimals; column colour: theme data colour 1 (the default) |
| P3-V6 | Line chart | 436, 188, 824, 250 | X-axis: `dim_date[year_month]`; Y-axis: `Late Order Rate` | Title "Late order rate by month"; sort axis by `year_month` ascending; X-axis type Categorical; Y-axis 0.0%; line colour: theme data colour 1 (the default), width 3; data labels off |
| P3-V7 | Bar chart (clustered) | 436, 454, 824, 246 | Y-axis: `dim_product[department]`; X-axis: `Late Item Rate` | Title "Late item rate, ten biggest departments"; visual filter on `department`: **Top N → Top 10 → By value: Delivered Items → Apply**; sort by `Late Item Rate` descending; data labels on, 0.0%; bar colour: theme data colour 1 (the default) |

## Count

3 pages, 25 visuals: per page one text box, one synced year slicer, four cards and two or three charts (page 1: 8, page 2: 8, page 3: 9).

## Save

**File → Save as** `powerbi/retail-supplier-warehouse.pbix`. Then set the interactions (`07-interactions.md`), check every number (`06-checks.md`), and save one screenshot per page in `powerbi/screenshots/` (`1-sales.png`, `2-suppliers.png`, `3-late-deliveries.png`).
