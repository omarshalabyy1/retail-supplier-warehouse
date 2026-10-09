# The project explained, from zero

This page explains the whole project in plain words: what it does, what every word means, where every number comes from, and how to talk about it in an interview. You do not need to know SQL or Power BI to read it.

[← Back to the README](../README.md)

## 1. The project in one minute

An online store does not make most of what it sells. Thousands of **sellers** (the store's suppliers) list their products on it, and when a customer orders, each seller ships its own items. The store promises the customer a delivery date.

The store's data comes out as separate files: orders, the items in each order, products, sellers, customers and reviews. So simple questions take a day of cleaning, and every team gets a different answer:

- How many orders arrive late?
- Which sellers make customers wait?
- Does a late delivery hurt the review the customer leaves?

This project answers them. It loads the files into a database unchanged, cleans them with SQL, applies the business rules (which order is late, which sellers are late most often), builds a **star schema** (one big table of order items with small lookup tables around it) and a few summary views, and puts a Power BI report on top. A notebook computes every number in the README from the star schema and the summary views.

Think of it like a parcel sorting hall. Every item that was ever ordered gets one ticket. The ticket says who sold it, what it is, who bought it, when it was promised and when it arrived. Once every item has a ticket in one pile, "which seller was late most often" is just a count of tickets.

## 2. Words you will meet

| Word | What it means here |
|---|---|
| **Seller, supplier** | A business that sells its products through the store. The project treats sellers as the store's suppliers. There are 3,095. |
| **Order** | One purchase by a customer. It can hold several items. |
| **Order item** | One product line inside an order. An order with a lamp and two cups from two sellers has items 1, 2 and 3. |
| **Price, freight** | Price is what the item cost; freight is the delivery charge for it. **Sales** in this project means price only, without freight. |
| **BRL** | Brazilian real, the currency of the data. "BRL 13.59M" means 13.59 million reais. |
| **Promised date** | The delivery date the store gave the customer when they ordered (`order_estimated_delivery_date` in the input). |
| **Delivered** | The order has the status `delivered` and a delivery date. Both must be there. |
| **Late** | A delivered order that arrived on a later day than the promised date. Arriving on the promised day counts as on time. |
| **Review score** | The 1 to 5 stars a customer gave the order. |
| **Department** | The group a product belongs to, such as "bed bath table" or "health beauty". The input has a category code per product; `departments.csv` turns each code into a department name in English. |
| **Top sellers** | The 100 sellers with the most late items. The number 100 is a setting (see `dbt_project.yml` below). |
| **Database** | A program that stores tables and answers questions about them. This project uses **PostgreSQL** (often "Postgres"), a free and widely used one. |
| **SQL** | Structured Query Language: the language used to ask a database questions and build tables. Every `.sql` file in `dbt/models/` is SQL. |
| **Table, row, column** | Like a spreadsheet sheet: each row is one thing (one order, one seller), each column is one fact about it (its date, its state). |
| **CSV** | Comma-separated values: a plain text file of a table, one row per line. The seven inputs are CSV files. |
| **Schema** | A folder of tables inside the database. This project has one per layer (`bronze`, `silver`, `gold`, `semantic`, `analytical`) and `ops` for the load log. |
| **Layer** | One step of the warehouse, each reading only the step before it: the **Bronze layer** (the files as they came, as text), the **Silver layer** (cleaned and typed), the **Gold layer** (the business rules: delivered, late, the seller late rank), the **Semantic layer** (the star schema), the **Analytical layer** (summary views: by month, by seller, review by lateness) and the **Reporting layer** (the notebook and Power BI). See [layers.svg](layers.svg). |
| **Warehouse** | A database built for reporting, not for running the store. Here, the PostgreSQL database with the layer schemas. |
| **ELT** | Extract, load, transform: load the files first, exactly as they are, then clean them inside the database. The opposite order (clean, then load) is ETL. |
| **`COPY`** | The PostgreSQL command that loads a whole file into a table at once. `load.py` uses it. |
| **`ops.load_log`** | A small table that records, for every load, which file went into which table: rows in the file, rows loaded, rows refused. |
| **Quarantine** | `bronze.quarantine`: where `load.py` puts a row it refuses (a required value is empty, or a value would not turn into a date or number), with the file, the row number and the reason. In this data it holds 0 rows. |
| **Transaction** | A group of database changes that either all happen or none do. `load.py` replaces the Bronze tables in one transaction, so a failed run leaves the old tables as they were. |
| **dbt** | dbt Core ("data build tool"): a free program that runs SQL files in the right order and turns each into a table or a view. `dbt run` builds the Silver, Gold, Semantic and Analytical layers. |
| **Model** | In dbt, one `.sql` file that builds one table or view. |
| **View, table** | A table stores its rows. A view stores only its query and runs it when read. The Silver and Analytical layers are views; the Gold and Semantic layers are tables. |
| **`vars`** | Settings in `dbt/dbt_project.yml`: `late_after_days: 0` and `top_sellers: 100`. The SQL reads them, so a rule can change without editing the SQL. |
| **Fact table** | The big table of events you count and add up. Here `fact_order_items`: one row per order item. |
| **Dimension table** | A smaller lookup table that describes the facts: `dim_product`, `dim_seller`, `dim_customer`, `dim_date`. You filter and group by them. |
| **Star schema** | One fact table in the middle with dimension tables around it, like a star. It is the standard shape for Power BI. See [data-model.svg](data-model.svg). |
| **Snowflake schema** | A star where a dimension has its own lookup table (for example product → department table). This project avoids it on purpose. |
| **Grain** | What one row of a table stands for. The grain of `fact_order_items` is "one item in one order". |
| **Primary key (PK)** | The column (or columns) that makes each row unique. For the fact it is `order_id` + `order_item_id`. |
| **Foreign key (FK)** | A column that points to a row in another table, like `seller_id` in the fact pointing to `dim_seller`. |
| **Natural key, surrogate key** | A natural key already exists in the data (the 32-character ids such as `seller_id`). A surrogate key is a made-up number like 1, 2, 3. This project uses natural keys only. |
| **Date table** | A dimension with one row per day, so every day exists even if nobody ordered on it. Power BI needs one to group by month and year. |
| **Distinct count** | Counting each value once. Because the fact has one row per item, an order with 3 items appears 3 times; a distinct count of `order_id` counts it once. |
| **SCD type 2** | Slowly changing dimension, type 2: keeping the old version of a row when it changes (for example a seller who moves state). The README says why it is not used yet. |
| **Lineage** | Which table is built from which. [dbt-lineage.svg](dbt-lineage.svg) draws it, model by model. |
| **Python, pandas** | Python is a programming language. pandas is its library for tables. The notebook uses them. |
| **Notebook** | `analysis/analysis.ipynb`, a file that mixes code, its output and notes. It computes every number in the README. |
| **Docker, Docker Compose** | Docker runs programs in a ready-made box called a container, so nobody installs PostgreSQL by hand. `docker-compose.yml` says which box to start. |
| **Port 5441** | The "door number" the database listens on. Each portfolio project uses its own number so several can run at once. |
| **Power BI** | Microsoft's tool for interactive reports and dashboards. **Import mode** means it copies the tables in, rather than asking the database on every click. |
| **Power Query** | The part of Power BI that connects to the database and loads the tables. |
| **DAX, measure** | Data Analysis Expressions: the formula language of Power BI. A **measure** is one formula, like "Late Order Rate". `powerbi/03-measures.dax` has 18 of them. |

## 3. How it works, file by file

Run in this order (the commands are in the README's "How to run it" section):

| Step | File | What it does |
|---|---|---|
| 0 | `docker-compose.yml` | Starts PostgreSQL 17 in a container on port 5441. |
| 1 | `load.py` | Checks the 7 input files before touching the database: each file exists, has its required columns, and every product category has a department. If not, it stops with one line. Then it loads only the required columns, as text, into 7 `bronze` tables with `COPY`, in one transaction, each row with its file, row number and run id. A row with an empty required value, or a value that would not turn into a date or number, goes to `bronze.quarantine` with the reason instead (0 rows here). An empty file or a key that appears twice stops the run. Each table's counts go to `ops.load_log`. |
| 2 | `dbt/models/silver/*.sql` | Silver layer, 7 views that clean the Bronze tables: turn text into dates and numbers, tidy city names and state codes, keep one review per order. Products keep their category code; `departments` maps each code to a department. |
| 3 | `dbt/models/gold/*.sql` | Gold layer, the business rules. `order_delivery` works out `is_delivered`, `is_late` and `delivery_days` for every order. `seller_late_rank` counts each seller's late items, ranks the sellers and flags the top 100 (`late_rank`, `is_top_late_seller`). |
| 4 | `dbt/models/semantic/*.sql` | Semantic layer, the star schema. `fact_order_items` joins each item to its order, its delivery rules and its review. The four dimensions: `dim_product` (with its department), `dim_seller` (with its rank from Gold), `dim_customer`, `dim_date` (one row per day). |
| 5 | `dbt/models/analytical/*.sql` | Analytical layer, 3 views over the star schema: `kpis_by_month` (sales and late counts per month), `kpis_by_seller` (delivered and late items per seller), `review_by_lateness` (average review, late against on time). |
| 2 to 5 | `dbt/dbt_project.yml` | The two settings: late after 0 days, top 100 sellers. Also says which layers are views and which are tables. |
| 6 | `analysis/analysis.ipynb` | Reporting layer: reads the Analytical and Semantic layers with SQL (and `ops.load_log` for the load counts), computes every number in the README and draws the charts in `docs/charts/`. |
| 6 | `powerbi/` | Reporting layer: Step-by-step instructions to build the three-page Power BI report: queries, model, 18 measures, pages, and the numbers each card must show (`06-checks.md`). |

The 7 input files: 6 come from the store (orders, order items, products, sellers, customers, reviews; you download them, see Data in the README) and 1 is a small mapping file committed in `data/input/` (`departments.csv`, category code to department). [`data/input/README.md`](../data/input/README.md) lists every column.

The notebook's notes still call the two settings `rules.late_after_days` and `rules.top_sellers`. Those are older names: the settings now live in `vars` in `dbt/dbt_project.yml`.

### The rules, with an example

One real order from the data, `001c85b5…`. It holds one item: product `84f45695…` in category `cama_mesa_banho`, sold by seller `4a3ca931…` from Ibitinga, São Paulo state (SP), price BRL 99.00 plus BRL 13.71 freight. The customer gave it 2 stars.

1. **Load.** `load.py` copies the order, item, product, seller and review rows into the `bronze` tables exactly as written, all as text: `"2017-12-22 18:37:40"` is still just characters.
2. **Clean.** The Silver views turn the text into types. Ordered at 19:19 on 24 Nov 2017, delivered at 18:37 on 22 Dec 2017, promised for 14 Dec 2017 (the promised date is kept as a date only). The price becomes the number 99.00. The category code `cama_mesa_banho` stays on the product; in the Semantic layer `dim_product` shows it as the department **bed bath table** through `departments.csv`. The city `ibitinga` becomes `Ibitinga`. The order has one review, so there is nothing to choose between.
3. **Delivered.** In the Gold layer: the status is `delivered` and there is a delivery date, so `is_delivered` is true.
4. **Late.** The delivery day (22 Dec) is later than the promised day plus 0 days (14 Dec), so `is_late` is true: 8 days late. Had it arrived any time on 14 Dec, it would be on time, because the rule compares days, not hours.
5. **Delivery days.** 22 Dec − 24 Nov = 28 days, stored as `delivery_days`.
6. **Seller rank.** This is one of the 189 late items of seller `4a3ca931…`, more than any other seller, so `gold.seller_late_rank` gives it `late_rank` 1 and `is_top_late_seller` true, and `dim_seller` shows both.
7. **Counting.** In the notebook this order adds BRL 99.00 to sales (freight is left out), 1 to delivered orders, 1 to late orders, 1 to late items, and its 2 stars go into the "Late" review average.

The review row is dated 16 Dec 2017, six days before the parcel arrived: the customer rated the order while still waiting for it.

## 4. Every number, explained

The notebook is [`analysis/analysis.ipynb`](../analysis/analysis.ipynb). The cell numbers below count from 0, the first cell. Cell 18 prints all the numbers again in one summary table, with the percentages rounded to one decimal.

### The headline and the results

| Number | What it means | How it is worked out | Where |
|---|---|---|---|
| **99,441 orders** | Every order in the orders file. | Rows loaded into `bronze.orders`, read back from `ops.load_log`. | notebook cell 3 |
| **112,650 order items** | Every item of every order. | Rows in `fact_order_items` (and in `bronze.order_items`: none is lost, none refused). | notebook cell 3 |
| **3,095 sellers** | Every seller in the sellers file. All of them sold at least one item. | Rows in `dim_seller`. | notebook cell 3 |
| **96,470 delivered orders** | Orders with status `delivered` and a delivery date. | Distinct count of `order_id` where `is_delivered`. | notebook cell 5 |
| **6,534 late orders, 6.8%** | Delivered orders that arrived after the promised day. | Distinct count of `order_id` where `is_late`. 6,534 / 96,470 = 6.8%. | notebook cell 5 |
| **100 of the 3,095 sellers** | The top sellers: the 100 with the most late items. | `late_rank` 1 to 100 in `gold.seller_late_rank`. 100 is `top_sellers` in `dbt/dbt_project.yml`. | `seller_late_rank.sql`; notebook cell 7 |
| **50.4% of late items ("half")** | The share of all late items that came from those 100 sellers. | 3,660 late items of the top 100 / 7,264 late items in total. | notebook cell 7 |
| **41.6% of delivered items** | The share of all delivered items those 100 sellers shipped. | 45,842 / 110,189 delivered items. | notebook cell 7 |
| **8.0% against 5.6%** | How often an item is late: top 100 sellers against every other seller. | Top 100: 3,660 late / 45,842 delivered = 8.0%. The other 2,995: 3,604 late / 64,347 delivered = 5.6%. | notebook cell 7 |
| **2.27 against 4.29 ("two stars")** | Average review of late orders against on-time orders. | Each delivered, reviewed order counted once. Late: 6,381 orders average 2.27. On time: 89,443 orders average 4.29. 4.29 − 2.27 = 2.02 stars. | notebook cell 10 |
| **0 days** | The late rule: late means delivered more than 0 days after the promised date, so any later day. | `late_after_days` in `dbt/dbt_project.yml`. | `order_delivery.sql` |
| **Port 5441** | The database's door number. | Set in `docker-compose.yml` and `dbt/profiles.yml`. | `docker-compose.yml` |

The seller numbers 3,660, 45,842, 3,604 and 64,347 are not printed in the notebook (it prints only the shares). They are the sums of `analytical.kpis_by_seller` (top 100 against the rest), and were rechecked by recounting the input files with pandas, outside the database.

The two charts in the README are drawn by the notebook: [late-items-by-seller.png](charts/late-items-by-seller.png) in cell 8 (its title rounds 50.4% to 50%), and [review-late-vs-on-time.png](charts/review-late-vs-on-time.png) in cell 10. A third chart, [sales-by-month.png](charts/sales-by-month.png), is drawn in cell 14 and used by the Power BI checks, not the README.

### Other numbers the notebook prints

These are not in the README but are on the Power BI check list (`powerbi/06-checks.md`), so an interviewer may ask.

| Number | What it means | Where |
|---|---|---|
| **98,666 orders** | Orders that have at least one item, so they are in the fact table. | cell 3 |
| **BRL 13,591,643.70 sales** | Sum of `price` over every item of every order, whatever its status. | cell 14 |
| **BRL 2,251,909.54 freight, 16.6% of sales** | Sum of `freight`. 2,251,909.54 / 13,591,643.70 = 16.6%. | cell 14 |
| **BRL 137.75 average order value** | 13,591,643.70 / 98,666 orders. | cell 14 |
| **12.5 days** | Average days from order to delivery, each delivered order once. | cell 14 |
| **4.10** | Average review over every reviewed order, delivered or not. | cell 14 |
| **7,264 late items of 110,189, 6.6%** | The late rate counted per item instead of per order. | cell 5 |
| **1,274 sellers** | Sellers with at least one late item. The other 1,821 never delivered late. | cell 7 |
| **74 departments** | The 73 departments of `departments.csv` plus "unknown". | cell 3 |
| **2017: BRL 6,155,806.98, 44,579 orders, 5.6% late** | The same numbers for orders placed in 2017. | cell 16 |
| **SP 7.1%** | São Paulo state sellers: 5,585 late / 78,598 delivered items, the highest late rate among states with at least 500 delivered items. | cell 16 |
| **Health beauty 7.6%** | 716 late / 9,465 delivered items, the highest late rate among the ten departments with the most delivered items. | cell 12 |

Things that can look wrong but are not:

- **99,441 orders loaded, but 98,666 in the fact table.** The fact table is built from items. 775 orders have no item at all (603 `unavailable`, 164 `canceled`, 5 `created`, 2 `invoiced`, 1 `shipped`, counted with pandas on the input file). They stay in `bronze.orders`, `silver.orders` and `gold.order_delivery`, but have nothing to put in the fact.
- **6.8% of orders are late, but 6.6% of items.** Two different counts. 6,534 late orders hold 7,264 late items, because one order can hold several items.
- **Half is 50.4%.** The headline rounds it. The exact count is 3,660 of 7,264.
- **Exactly which 100 sellers are "top" is partly a tie-break.** The sellers ranked 93 to 107 all have 15 late items. The rank breaks the tie by `seller_id`, so it is the same on every run. The 50.4% does not move whichever of them are picked, because each has the same 15 late items; the 41.6% and 8.0% could move slightly.
- **96,478 orders have the status `delivered`, but 96,470 are counted as delivered.** 8 of them have no delivery date, so the project cannot say if they were late. 6 orders have a delivery date but another status; they are not counted as delivered either.
- **99,224 reviews, but 98,673 reviewed orders.** 547 orders were reviewed more than once (551 extra rows). `silver.reviews` keeps the latest review per order.
- **6,534 late orders, but 6,381 in the review average.** 153 late orders have no review.
- **99,441 customers, the same as orders.** The data gives a new `customer_id` to every order. `customer_unique_id` is the real person: 96,096 of them, counted with pandas.
- **Sales of 2016 + 2017 + 2018 add up to the total.** 49,785.92 + 6,155,806.98 + 7,386,050.80 = 13,591,643.70, and 312 + 44,579 + 53,775 = 98,666 orders (2018 is in `06-checks.md`; 2016 was counted with pandas).

### The diagrams

| Number | Where you see it | What it means |
|---|---|---|
| **7 CSV files, 6 store exports** | data-flow.svg, layers.svg | The 6 files from the store plus `departments.csv`. |
| **99,441** | data-flow.svg, data-model.svg, layers.svg, header.svg | Rows in `bronze.orders`, `silver.orders`, `gold.order_delivery`, `bronze.customers`, `silver.customers` and `dim_customer`: one customer row per order. |
| **112,650** | data-flow.svg, data-model.svg, layers.svg | Rows in `bronze.order_items`, `silver.order_items` and `fact_order_items`: the item count never changes. |
| **99,224 → 98,673** | data-flow.svg | Review rows in `bronze.reviews`, then one per order in `silver.reviews` (see above). |
| **3,095** | data-flow.svg, data-model.svg, header.svg | Rows in `bronze.sellers`, `silver.sellers`, `gold.seller_late_rank` and `dim_seller`. |
| **32,951** | data-flow.svg, data-model.svg | Rows in `bronze.products`, `silver.products` and `dim_product`. Every product was sold at least once. |
| **73** | data-flow.svg | Rows in `departments.csv`, `bronze.departments` and `silver.departments`: one per category code. |
| **1,096** | data-flow.svg, data-model.svg | Days in `dim_date`: whole years from 1 Jan 2016 to 31 Dec 2018 (366 + 365 + 365), around the first order (4 Sep 2016) and the last (3 Sep 2018). |
| **446,875 rows** | layers.svg | All 7 Bronze tables together: 99,441 + 112,650 + 32,951 + 3,095 + 99,441 + 99,224 + 73. |
| **6.8%, 50.4%, 41.6%, 100** | header.svg | The headline numbers from the table above. |
| **1 to \*** | data-model.svg | One dimension row links to many fact rows: one seller has many items. |
| **0** | layers.svg, data-flow.svg | Rows in `bronze.quarantine`: no row of this data was refused. |
| **24, 3,095, 2** | data-flow.svg | Rows in the Analytical views: 24 order months, one row per seller, late and on time. |
| **1 to 6** | how-it-works.svg, layers.svg, data-flow.svg | The six layers: Bronze, Silver, Gold, Semantic, Analytical, Reporting. |

The diagram row counts come from counting each table after a run; they are not in the notebook. The Silver and `dim_date` counts were rechecked from the input files with pandas.

## 5. What the results mean for the business

- **Most orders arrive on time.** 93.2% of delivered orders (100% − 6.8%) came on or before the promised day. The problem is real but not everywhere.
- **Late deliveries are concentrated.** 100 sellers, about 3% of them, cause half of the late items. The supplier team has a short list to call first instead of chasing 3,095 sellers.
- **It is not only because they are big.** Those 100 ship 41.6% of the items but cause 50.4% of the late ones. Their items are late 8.0% of the time against 5.6% for everyone else.
- **Late costs reviews.** A late order averages 2.27 stars against 4.29 on time, about two stars less. New customers read reviews before they buy, so lateness can also cost future sales.
- **Most sellers are never late.** 1,821 of the 3,095 sellers had no late item at all. A bad experience comes from a minority of suppliers.

## 6. Interview questions you can expect

**Explain the project in 30 seconds.**
An online store sells through thousands of suppliers, and its data came as separate exports that every team cleaned differently. I loaded them into PostgreSQL as they are, cleaned them with dbt, and built a star schema with one row per order item plus a Power BI report. Result: 6.8% of delivered orders arrive late, 100 of 3,095 sellers cause half of the late items, and late orders score 2.27 stars against 4.29.

**Why one row per order item, and not per order?**
Price, freight and seller belong to the item: one order can hold items from two sellers. At order grain I could not say which seller shipped what. The cost is that order facts (status, dates, lateness, review) repeat on each item, so every order count is a distinct count of `order_id` and every review average counts each order once.

**Why compare share of late items with share of delivered items?**
Big sellers ship more, so they will have more late items even if they are no worse. Putting 50.4% of late items next to 41.6% of delivered items shows the top 100 are late more often than their size explains: 8.0% against 5.6%.

**Why is the top-seller flag a column in `dim_seller` and not a Power BI formula?**
So the ranking is worked out once and everyone reads the same answer: the notebook, the SQL checks and Power BI all use `is_top_late_seller`. If Power BI ranked sellers itself, a filter on the page could change who is "top" and the cards would stop matching the notebook.

**Why load everything as text and clean in SQL?**
The Bronze layer then holds the input values unchanged, so any number can be traced back to the file it came from. If a cleaning rule changes, I change one SQL file and rebuild, without loading again.

**How do you avoid duplicates if the load runs twice?**
`load.py` drops and recreates each Bronze table inside one transaction, and dbt rebuilds every table from those. Running it twice gives the same result, and a failed run leaves the old tables in place.

**Why no scheduler and no incremental load?**
The source is a fixed export that never changes, so there is nothing to refresh on a timer, and 446,875 rows rebuild quickly. With a live daily feed I would schedule it and load only new rows.

**Why is department a column of `dim_product` and not its own table?**
That would make a snowflake: Power BI would need one more join for every visual that groups by department. A department is just a label on a product, so it sits on the product.

**Why natural keys and no history (SCD type 2)?**
The ids in the export are stable and each seller appears once, with nothing changing over time to track. With a live seller feed where a seller can move state, I would add a dbt snapshot to keep the old versions, and a surrogate key to tell them apart.

**How do you know the numbers are right?**
`load.py` refuses to load if a file, a column or a department mapping is missing, a file is empty or a key appears twice; it puts any row it cannot read into `bronze.quarantine` with the reason, and `ops.load_log` keeps every row count. Sales add up to the same BRL 13,591,643.70 in the Bronze, Silver, Semantic and Analytical layers. The notebook computes every README number from the Analytical and Semantic layers with plain SQL, and `powerbi/06-checks.md` lists the number each Power BI card must show, with the SQL to check it. There are no automated dbt tests: the data is a fixed export, so I checked it once. With a live feed I would add tests for unique keys, missing values and broken links between tables.

## 7. Limits, in plain words

- "Late" compares the delivery day with the promised day. It ignores the time of day and does not say whose fault the delay was: the seller's or the carrier's.
- Lateness belongs to the order, so when one order holds items from several sellers, every seller in it gets the same late flag. This affects 27 of the 7,264 late items (13 orders), counted with pandas.
- The seller ranking is over all time. A seller who was late in 2017 and fixed it in 2018 still ranks by its old late items.
- Sales count every order with items, whatever its status, including canceled ones.
- 775 orders without items, and 8 "delivered" orders without a delivery date, are left out of the counts above.
- The data is a fixed export. There is no seller history and no automated data test.
- Amounts are in Brazilian reais.
