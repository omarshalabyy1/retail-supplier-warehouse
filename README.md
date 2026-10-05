# Retail supplier warehouse

**99,441 orders loaded and tested every morning: 100 of 3,095 sellers account for half of all late-delivered items.**

New client? See [docs/new-client.md](docs/new-client.md).

## The problem

An online store sells products from thousands of sellers, its suppliers. Orders, items, sellers, products and reviews come out as separate exports. Every report starts with a day of cleaning, every team gets a different total, and nobody can say which suppliers make customers wait.

## The solution

A warehouse that rebuilds itself every morning. The input files are checked and load as they are, SQL cleans them, a star schema answers the questions, data tests check every load, and a Power BI report reads the result.

![How it works](docs/how-it-works.svg)

The mental model is four layers. Each one only reads the layer below it, so a mistake can be traced down to the file it came from.

![One warehouse, four layers](docs/layers.svg)

## The result

- **99,441 orders** (112,650 order items) load every morning, and **31 data tests** pass on every run: keys, missing values, links between tables, and totals that must equal the raw file to the cent.
- **6.8% of delivered orders arrive late** (6,534 of 96,470).
- **100 of the 3,095 sellers account for 50.4% of late-delivered items**, while shipping 41.6% of all delivered items. Their late rate is 8.0%, against 5.6% for every other seller: a short list for the supplier team to call first.
- **Late orders lose two stars:** they average 2.27 out of 5, against 4.29 for orders on time.

![100 sellers cause half of late items](docs/charts/late-items-by-seller.png)

![Average review, late against on time](docs/charts/review-late-vs-on-time.png)

Every number above is computed in [`analysis/analysis.ipynb`](analysis/analysis.ipynb), which runs top to bottom against the warehouse and saves its outputs. How each one is measured:

| Number | Measured as |
|---|---|
| Orders loaded | Rows in `raw.orders` after the morning load (`raw.load_log` keeps the count of every load) |
| Data tests passing | Tests with status `pass` in the last `dbt build` (`dbt/target/run_results.json`) |
| Late | Order delivered (status `delivered` with a delivery date) on a later day than the date promised to the customer |
| Seller share of late items | Late items of the 100 sellers with the most late items (`dim_seller.is_top_late_seller`, ties broken by seller id), over all late items. Counted per item, because one order can hold items from several sellers |
| Average review | Each reviewed order counted once; when an order was reviewed twice, the latest review |

## Power BI report

Three pages: **Sales**, **Suppliers** and **Late deliveries**. The [`powerbi/`](powerbi/) folder builds it from nothing, step by step, and lists the numbers each page must show.

*Screenshots are added here once the report is built.*

## How to run it

You need Docker Desktop, and Python 3.10+ for the notebook.

1. Get the data (see [Data](#data)) and unzip the six CSV files into `data/input/` (the committed `departments.csv` is already there; [input guide](data/input/README.md)).
2. Create the settings file and set a password of your own in it:
   ```bash
   cp .env.example .env
   ```
3. Start the warehouse (Postgres on `localhost:5441`) and Airflow (`http://127.0.0.1:8091`):
   ```bash
   docker compose up -d --build
   ```
4. In Airflow, turn on the `retail_warehouse` DAG and trigger it (it then runs by itself at 6am, Cairo time). It takes about half a minute: `load_raw`, then `dbt build`.
5. Run the notebook:
   ```bash
   pip install pandas matplotlib "psycopg[binary]" pyyaml python-dotenv jupyter
   jupyter nbconvert --to notebook --execute --inplace analysis/analysis.ipynb
   ```
6. Build the report with [`powerbi/README.md`](powerbi/README.md).

## For engineers

| Decision | Why |
|---|---|
| Load the required columns as text, clean in SQL (ELT) | The raw layer holds the input values unchanged, so any number can be traced back and the cleaning can change without reloading |
| Full reload every morning, in one transaction | The source is a complete export, not a stream of changes. Replacing it is simpler than tracking changes and is safe to rerun; a failed load leaves yesterday's data in place |
| One fact at order-item grain | Sales, freight and seller live on the item. Order-level facts (status, dates, lateness, review) repeat on each item, so measures count orders and reviews once with a distinct count |
| Department as a column of `dim_product` | A star, not a snowflake: one join fewer for every Power BI visual |
| No history (SCD type 2) on sellers yet | The export holds each seller once, with no changes to track. With a live seller feed, a dbt snapshot would add it |
| `dbt build` instead of `dbt run` then `dbt test` | Each model is tested right after it is built, and anything that depends on a failed model is skipped |

```
config/client.yaml       every client value (names, files, rules, schedule, colours); read only through config.py
load.py                  checks the input files, then loads them into the raw schema, logged in raw.load_log
theme.py                 writes the Power BI theme from config/client.yaml
dbt/models/staging/      6 views: types, names, one review per order, departments in English
dbt/models/marts/        the star schema: fact_order_items and four dimensions, with their tests
dbt/tests/               grain, totals against raw, no negative amounts
dags/retail_warehouse.py Airflow: load_raw >> dbt_build, daily at 6am Cairo time
analysis/analysis.ipynb  every number in this README
powerbi/                 the report, step by step
```

Stack: PostgreSQL 17, Python, dbt Core, Apache Airflow 3, Docker Compose, Power BI Desktop.

## Data

The [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) on Kaggle (CC BY-NC-SA 4.0): about 100,000 orders placed from 2016 to 2018. Its sellers stand in for the store's suppliers and its product categories for departments. Amounts are in Brazilian reais. The files are not in this repo (the licence is non-commercial); download them from Kaggle into `data/input/`. `data/input/departments.csv`, the category-to-department mapping, is committed: it is derived from the dataset's category translation file (CC BY-NC-SA 4.0, same Kaggle link); a client's private copy replaces it with their own mapping.
