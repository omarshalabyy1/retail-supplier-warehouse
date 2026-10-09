# Power BI report

Built in Power BI Desktop (free) on the warehouse's Semantic layer (schema `semantic`, the star schema), by copying and pasting from the files below.

## What it answers

| Page | Question |
|---|---|
| 1. Sales | How much did the store sell, by month and by department? |
| 2. Suppliers | Which sellers cause the late deliveries, and is it more than their size? |
| 3. Late deliveries | How often are orders late, and what does it cost in reviews? |

## Build it in this order

Follow [`08-build-checklist.md`](08-build-checklist.md): it walks through the files below step by step, with the numbers to check at each stop.

1. Start the warehouse, then load and build it once (see the main README).
2. [`01-power-query.md`](01-power-query.md): connect and load the five tables.
3. [`02-model.md`](02-model.md): date table, relationships, column formats, sort-by columns, hidden columns.
4. [`03-measures.dax`](03-measures.dax): the 18 measures, with folder, format and the pages that use them.
5. [`05-theme.json`](05-theme.json): **View → Themes → Browse for themes**. The portfolio site's colours, so every project report looks like one family.
6. [`04-pages.md`](04-pages.md): the three pages, 25 visuals, each with its position, fields and format.
7. [`07-interactions.md`](07-interactions.md): which visual filters which, and the visual-level filters.
8. [`06-checks.md`](06-checks.md): every card must match; if one doesn't, the table says where to look.
9. Save `retail-supplier-warehouse.pbix` here and one screenshot per page in `screenshots/`.
