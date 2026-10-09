<p align="center">
  <img width="100%" src="docs/header.svg" alt="Retail supplier warehouse: 99,441 orders in one star schema. 100 of 3,095 sellers account for half of all late-delivered items.">
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1200&color=2DD4BF&center=true&vCenter=true&width=760&lines=Retail+supplier+warehouse;Load.+Clean.+Model.+Report.;99%2C441+orders%2C+one+star+schema" alt="Retail supplier warehouse">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10">
  <img src="https://img.shields.io/badge/dbt-1.10-FF694B?style=for-the-badge&logo=dbt&logoColor=white" alt="dbt 1.10">
  <img src="https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL 17">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/Power_BI-Report-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" alt="Power BI">
</p>

> 📖 **New to data?** [The project explained, from zero](docs/explained.md): every word, every number and the interview questions, in plain words.

<h3 align="center">99,441 orders in one star schema:<br>100 of 3,095 sellers account for half of all late-delivered items.</h3>

## The problem

An online store sells products from thousands of sellers, its suppliers. Orders, items, sellers, products and reviews come out as separate exports. Every report starts with a day of cleaning, every team gets a different total, and nobody can say which suppliers make customers wait.

## 🛠️ The solution

A warehouse built in one run. The input files are checked and load as they are, SQL cleans them, the business rules flag late orders and rank sellers, a star schema and a few summary views answer the questions, and a Power BI report reads the result.

![How it works](docs/how-it-works.svg)

The mental model is six layers, left to right. Each one reads only the layer before it, so a mistake can be traced back to the file it came from. A row the load refuses is kept in `bronze.quarantine` with the reason.

![One warehouse, six layers](docs/layers.svg)

## 📈 The result

<p align="center">
  <img src="https://user-images.githubusercontent.com/74038190/221352987-68da234d-4d62-4e9d-9d7f-098dc657c2dc.gif" width="100" alt="Moving chart">
</p>

- **99,441 orders** (112,650 order items) load into one star schema in one run.
- **6.8% of delivered orders arrive late** (6,534 of 96,470).
- **100 of the 3,095 sellers account for 50.4% of late-delivered items**, while shipping 41.6% of all delivered items. Their late rate is 8.0%, against 5.6% for every other seller: a short list for the supplier team to call first.
- **Late orders lose two stars:** they average 2.27 out of 5, against 4.29 for orders on time.

![100 sellers cause half of late items](docs/charts/late-items-by-seller.png)

![Average review, late against on time](docs/charts/review-late-vs-on-time.png)

Every number above is computed in [`analysis/analysis.ipynb`](analysis/analysis.ipynb), which runs top to bottom against the warehouse and saves its outputs. How each one is measured:

| Number | Measured as |
|---|---|
| Orders loaded | Rows in `bronze.orders` after the load (`ops.load_log` keeps the count of every load, and of the rows refused to `bronze.quarantine`: 0) |
| Late | Order delivered (status `delivered` with a delivery date) on a later day than the date promised to the customer |
| Seller share of late items | Late items of the 100 sellers with the most late items (`is_top_late_seller`, set in the Gold layer by `gold.seller_late_rank`, ties broken by seller id), over all late items. Counted per item, because one order can hold items from several sellers |
| Average review | Each reviewed order counted once; when an order was reviewed twice, the latest review |

## 📊 Power BI report

Three pages: **Sales**, **Suppliers** and **Late deliveries**. The [`powerbi/`](powerbi/) folder builds it from nothing, step by step, and lists the numbers each page must show.

*Screenshots are added here once the report is built.*

## ▶️ How to run it

<p align="center">
  <img src="https://user-images.githubusercontent.com/74038190/212284087-bbe7e430-757e-4901-90bf-4cd2ce3e1852.gif" width="100" alt="Code">
</p>

You need Docker Desktop, and Python 3.10+ for the notebook.

1. Get the data (see [Data](#data)) and unzip the six CSV files into `data/input/` (the committed `departments.csv` is already there; [input guide](data/input/README.md)).
2. Start the warehouse (Postgres on port 5441, user and password `warehouse`):
   ```bash
   docker compose up -d
   ```
3. Install the Python tools:
   ```bash
   pip install -r requirements.txt pandas matplotlib jupyter
   ```
4. Load the files into the Bronze layer, then build the other layers:
   ```bash
   python load.py
   cd dbt && dbt run && cd ..
   ```
5. Run the notebook:
   ```bash
   jupyter nbconvert --to notebook --execute --inplace analysis/analysis.ipynb
   ```
6. Build the report with [`powerbi/README.md`](powerbi/README.md).

## 🏗️ For engineers

Every table, the tables it is built from, and its row count after one run:

![Data flow, table by table](docs/data-flow.svg)

The Semantic layer, the star schema Power BI imports:

![The star schema](docs/data-model.svg)

The same lineage as dbt sees it, model by model, from each model's `source()` and `ref()`:

![dbt lineage: 7 Bronze sources, 7 Silver views, 2 Gold tables, the fact and four dimensions in the Semantic layer, 3 Analytical views](docs/dbt-lineage.svg)

| Decision | Why |
|---|---|
| Load the required columns as text, clean in SQL (ELT) | The Bronze layer holds the input values unchanged, with the file and row each came from, so any number can be traced back and the cleaning can change without reloading |
| Refuse a bad row, stop on a bad file | A row with an empty required value or a value that would not convert goes to `bronze.quarantine` with the reason (0 rows in this data). A missing file or column, an empty file, a key that appears twice or a category without a department stops the load before anything changes |
| Full reload in one transaction, no scheduler | The source is a fixed export that never changes, so there is nothing to refresh on a timer. Running it again gives the same result |
| One fact at order-item grain | Sales, freight and seller live on the item. Order-level facts (status, dates, lateness, review) repeat on each item, so measures count orders and reviews once with a distinct count |
| Seller late rank in the Gold layer, from Silver | A rule belongs in Gold, and a dimension built from the fact would be a loop. `dim_seller` reads the rank from `gold.seller_late_rank` |
| Department as a column of `dim_product` | A star, not a snowflake: one join fewer for every Power BI visual |
| No history (SCD type 2) on sellers yet | The export holds each seller once, with no changes to track. With a live seller feed, a dbt snapshot would add it |

```
load.py                  Bronze layer: checks the input files, loads them as text, refused rows to bronze.quarantine, logged in ops.load_log
dbt/models/silver/       Silver layer, 7 views: types, names, one review per order
dbt/models/gold/         Gold layer: the delivery rules per order and the seller late rank
dbt/models/semantic/     Semantic layer: the star schema, fact_order_items and four dimensions
dbt/models/analytical/   Analytical layer, 3 views: by month, by seller, review by lateness
dbt/dbt_project.yml      the two rules: late after 0 days, top 100 sellers
analysis/analysis.ipynb  every number in this README, from the Semantic and Analytical layers
powerbi/                 Reporting layer: the report, step by step
```

Stack: PostgreSQL 17, Python, dbt Core, Docker Compose, Power BI Desktop.

## 🗂️ Data

The [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) on Kaggle (CC BY-NC-SA 4.0): about 100,000 orders placed from 2016 to 2018. Its sellers stand in for the store's suppliers and its product categories for departments. Amounts are in Brazilian reais. The files are not in this repo (the licence is non-commercial); download them from Kaggle into `data/input/`. `data/input/departments.csv`, the category-to-department mapping, is committed: it is derived from the dataset's category translation file (CC BY-NC-SA 4.0, same Kaggle link).

<p align="center">
  <img width="100%" src="docs/footer.svg" alt="A warehouse built in one run.">
</p>
