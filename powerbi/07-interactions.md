# 7. Interactions and filters

## Edit interactions

On each page: select the **source** visual → **Format → Edit interactions** → on every other visual click the icon in the table (**Filter** = funnel, **None** = circle with a line). Click **Edit interactions** again to finish. Visual IDs are from `04-pages.md`.

Why Filter, not Highlight: the cards and rates must recompute for the selection; a highlight would leave them at the page total.

### Page 1: Sales

| Source ↓ / Target → | V1 Sales | V2 Orders | V3 AOV | V4 Freight % | V5 Line | V6 Departments |
|---|---|---|---|---|---|---|
| P1-V5 line (click a month) | Filter | Filter | Filter | Filter | — | Filter |
| P1-V6 departments (click a bar) | Filter | Filter | Filter | Filter | Filter | — |

### Page 2: Suppliers

| Source ↓ / Target → | V1 Sellers | V2 Late rate | V3 Top sellers late | V4 Top sellers delivered | V5 Table | V6 States |
|---|---|---|---|---|---|---|
| P2-V5 table (click a seller) | Filter | Filter | Filter | Filter | — | None |
| P2-V6 states (click a bar) | Filter | Filter | Filter | Filter | Filter | — |

V3 and V4 stay at 50.4% and 41.6% when a seller or state is clicked: both measures ignore seller filters on purpose. V5 → V6 is None because a single seller's state may fall under the `report.min_state_items` filter and the chart would go empty.

### Page 3: Late deliveries

| Source ↓ / Target → | V1 Late rate | V2 Late orders | V3 Delivery days | V4 Review | V5 Review chart | V6 Line | V7 Departments |
|---|---|---|---|---|---|---|---|
| P3-V5 review chart (click a column) | None | None | None | None | — | None | None |
| P3-V6 line (click a month) | Filter | Filter | Filter | Filter | Filter | — | Filter |
| P3-V7 departments (click a bar) | Filter | Filter | Filter | Filter | Filter | Filter | — |

P3-V5 filters nothing: clicking "True" would make every late rate 100%.

The year slicer (Px-S) and the text box (Px-T) keep the defaults: the slicer filters every visual on its page, the text box has no data.

## Filters

| Level | Filter |
|---|---|
| Report (all pages) | None |
| Page | None on all three pages |
| Visual | P1-V6: `department` Top 10 by `Sales` · P2-V6: `Delivered Items` ≥ `report.min_state_items` (demo: 500) · P3-V5: `is_delivered` is True · P3-V7: `department` Top 10 by `Delivered Items` |

## Not used

- **Drill-through pages:** none. Each page answers its own question; the table on page 2 already lists every seller.
- **Bookmarks and buttons:** none. Move between pages with the page tabs.
- **Tooltip pages:** none. Every visual keeps the default tooltip (its own fields).
