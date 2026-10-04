# Power BI report

Built in Power BI Desktop (free) on the warehouse's `marts` schema, by copying and pasting from the files below.

## What it answers

| Page | Question |
|---|---|
| 1. Sales | How much did the store sell, by month and by department? |
| 2. Suppliers | Which sellers cause the late deliveries, and is it more than their size? |
| 3. Late deliveries | How often are orders late, and what does it cost in reviews? |

## Build it in this order

1. Start the stack and run the `retail_warehouse` DAG once (see the main README).
2. [`01-power-query.md`](01-power-query.md): connect and load the five tables.
3. [`02-model.md`](02-model.md): relationships, date table, sort-by columns, hidden columns.
4. [`03-measures.dax`](03-measures.dax): every measure, with its folder and format.
5. [`05-theme.json`](05-theme.json): **View → Themes → Browse for themes**.
6. [`04-pages.md`](04-pages.md): the three pages, visual by visual.
7. [`06-checks.md`](06-checks.md): every card must match; if one doesn't, the table says where to look.
8. Save `retail-supplier-warehouse.pbix` here and one screenshot per page in `screenshots/`.
