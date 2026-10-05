# New client

This repo is a GitHub template. A new client gets a **private** repo from it (Use this template > Create a new repository > Private); client data never goes into this public repo.
Everything that changes per client is in three places: `config/client.yaml`, `.env`, and the files in `data/input/`.

It serves three offerings: **2** Automated daily data pipeline, **8** Data warehouse in two weeks, **10** Power BI sales and margin dashboard.

## Done in the template

What the client gets with no work. Hours are an estimate of building each part from scratch.

| Part | Estimate (hours) |
|---|---|
| Docker stack: PostgreSQL warehouse and Airflow in one Compose file, dbt in its own virtual environment (`docker-compose.yml`, `Dockerfile`) | 3 |
| Loader: each input file checked for its columns, every category checked for a department, the required columns loaded with `COPY`, every load logged (`load.py`) | 3 |
| dbt models: 6 staging views and a star schema (order-item fact, product, seller, customer and date dimensions, the late rule, the top-seller ranking) (`dbt/models/`) | 5 |
| dbt tests: 31 on every run, keys, links, grain, totals equal to the raw file to the cent, no negative amounts, late only when delivered (`dbt/`) | 3 |
| Airflow DAG: the client's schedule and time zone, retries, `load_raw` then `dbt build` with the rules as dbt vars (`dags/retail_warehouse.py`) | 2 |
| Client settings: `config/client.yaml`, `config.py` (`load_config()`), `.env`, the Power BI theme written from the config (`theme.py`) | 2 |
| Analysis notebook: every number, three charts, the Power BI check numbers (`analysis/analysis.ipynb`) | 4 |
| Power BI build pack: 6 queries, the model, 18 measures, 3 pages with 25 visuals, interactions, checks, a 17-step checklist (`powerbi/`) | 8 |
| README with its diagrams, and the input file guide (`data/input/README.md`) | 3 |
| **Total** | **33** |

## Configure

Per client, file by file. Hours are an estimate.

| File | Key | Example | Estimate (hours) |
|---|---|---|---|
| `config/client.yaml` | `client.name`, `client.currency`, `client.decimals`, `report.title`, `report.colours` | `EGP`, `2`, `"#0F766E"` | 0.5 |
| `.env` | `DB_PASSWORD` | a new password | 0.25 |
| `data/input/` orders, order items, products, sellers, customers, reviews | `inputs.orders` … `inputs.reviews` | `orders.csv` with `order_status` | 4 |
| `data/input/` departments mapping | `inputs.departments` | `D-01,Kitchen` | 1 |
| `config/client.yaml` | `rules.late_after_days`, `rules.top_sellers`, `schedule.cron`, `schedule.timezone`, `report.check_year`, `report.min_state_items` | `1`, `20`, `"30 7 * * *"`, `Asia/Riyadh` | 0.25 |
| Run the DAG, `theme.py` and the notebook; fix what the checks report | | | 1 |
| Power BI: build from `powerbi/08-build-checklist.md` with the client's server in the Warehouse query; copy the notebook's numbers into `powerbi/06-checks.md` | `warehouse.*` | `127.0.0.1:5441` | 2 |
| **Total** | | | **9** |

## Custom, and the share already done, per offering (estimates)

Template and configure hours count only the parts the offering delivers. Share already done = template ÷ (template + configure + custom).

### 2. Automated daily data pipeline

Uses: Docker stack 3, loader 3, dbt models 5, dbt tests 3, DAG 2, client settings 2, README 3 = **21** template hours. Configure without Power BI: 9 − 2 = **7**.

| Custom work | Estimate (hours) |
|---|---|
| Read the client's real sources (an API, a database or a shared folder) in place of CSV exports | 4 |
| Emailed daily summary and an alert when a run fails | 2 |
| Incremental load in place of the full reload, when the data is large | 2 |
| **Total** | **8** |

Share already done: 21 ÷ (21 + 7 + 8) = 21 ÷ 36 = **58%** (58.3%), an estimate.

### 8. Data warehouse in two weeks

Uses every part: **33** template hours, **9** configure.

| Custom work | Estimate (hours) |
|---|---|
| Map more of the client's sources into the input contract (returns, stock, purchase orders) | 6 |
| One more fact or dimension for the client's top questions | 4 |
| History on suppliers (a dbt snapshot, slowly changing dimension type 2) | 2 |
| **Total** | **12** |

Share already done: 33 ÷ (33 + 9 + 12) = 33 ÷ 54 = **61%** (61.1%), an estimate.

### 10. Power BI sales and margin dashboard

Uses: Docker stack 3, loader 3, dbt models 5, dbt tests 3, client settings 2, notebook 4, Power BI pack 8, README 3 = **31** template hours (no scheduled refresh). Configure without the schedule: **9** (the schedule keys take minutes).

| Custom work | Estimate (hours) |
|---|---|
| Margin: the client's cost per item or a product cost file, the margin measures and a margin page (the demo data has no cost, so the demo has no margin) | 4 |
| Growth against the last period: the time-intelligence measures and visuals | 2 |
| Row-level security, so each manager sees only their area (Advanced tier) | 3 |
| **Total** | **9** |

Share already done: 31 ÷ (31 + 9 + 9) = 31 ÷ 49 = **63%** (63.3%), an estimate.

## Steps

1. Create the private repo from the template and clone it.
2. `cp .env.example .env` and set `DB_PASSWORD`.
3. Edit `config/client.yaml`. If you change `warehouse.port`, `warehouse.database` or `warehouse.user`, change them in `docker-compose.yml` too.
4. Put the seven files in `data/input/` ([columns and examples](../data/input/README.md)).
5. `python theme.py`, then `docker compose up -d --build`, then trigger the `retail_warehouse` DAG in Airflow and run the notebook.
6. Build the Power BI report from `powerbi/`.

## What this repo adds to the template standard

The standard (portfolio `docs/template-standard.md`) was written on a project without dbt or Airflow. Three things this repo needed:

- **dbt gets client values as vars.** The DAG passes `rules.late_after_days` and `rules.top_sellers` with `dbt build --vars`; the models have no defaults, so a missing var stops dbt. The connection reaches `dbt/profiles.yml` as environment variables set by the DAG from `load_config()`, and the password from `.env` through Docker Compose.
- **The warehouse has two addresses.** `config/client.yaml` holds the address from the laptop (`127.0.0.1` and the published port) for the notebook and Power BI; inside Docker the DAG reaches the service `warehouse` on 5432. Compose sets `WAREHOUSE_HOST` and `WAREHOUSE_PORT` for the Airflow container, and `load_config()` prefers them.
- **The DAG reads the config when Airflow parses it.** `schedule.cron` and `schedule.timezone` set the run time, so a client in another time zone changes two keys.

## Second-client drill (2026-10-05)

The acceptance test of the template: a fresh clone of the repo, a made-up second client, a run from scratch in Docker.

**Client B (drill):** name "Client B Market", currency `EGP`, `late_after_days: 1`, `top_sellers: 2`, schedule `30 7 * * *` in `Asia/Riyadh`, teal colours (`#0F766E` main, page `#F0FDFA`), title "Client B warehouse", check year 2025, `min_state_items: 2`. Different file names (`items.csv`, `suppliers.csv`, `dept_map.csv` …), department codes of another shape (`D-01`, `D-02`), three-letter state codes, and an extra column in three files. Input: 7 orders, 9 items, 4 products, 4 sellers, 7 customers, 7 reviews, 2 department codes, with one case per rule: an order delivered 1 day after its promise (on time under the 1-day rule), orders 2 and 4 days late, one shipped and one canceled order, a product without a category, an order reviewed twice, two orders with items from two sellers, and an order in 2024 outside the check year.

| What | Demo (Olist) | Client B (drill), every number checked by hand |
|---|---|---|
| Airflow runs | scheduled and manual: success, 42 of 42 (11 models, 31 tests) | scheduled (7:30am Riyadh) and manual: success, 42 of 42 |
| Orders loaded / in the fact | 99,441 / 98,666 | 7 / 7 |
| Order items | 112,650 | 9 |
| Departments | 74 (73 mapped + unknown) | 3 (Kitchen, Garden, unknown) |
| Late orders | 6,534 of 96,470 delivered, 6.8% | 3 of 5, 60.0% (O0, O3, O4; O2, 1 day after, on time) |
| Late items | 7,264 of 110,189, 6.6% | 4 of 7, 57.1% |
| Top sellers' share of late / delivered items | top 100: 50.4% / 41.6% | top 2 (S3, S1): 75.0% / 71.4% |
| Late item rate, top sellers / others | 8.0% / 5.6% | 60.0% / 50.0% |
| Average review, on time / late | 4.29 / 2.27 | 4.50 / 1.67 (O2's latest review, 4, counts) |
| Sales, freight, freight share | BRL 13,591,643.70, BRL 2,251,909.54, 16.6% | EGP 1,000.00, EGP 100.00, 10.0% |
| Average order value | BRL 137.75 | EGP 142.86 |
| Average delivery days | 12.5 | 9.8 (10, 5, 9, 12, 13) |
| Check year | 2017: BRL 6,155,806.98, 44,579 orders, 5.6% late | 2025: EGP 950.00, 6 orders, 50.0% late |
| State chart top bar | SP, 7.1% (states with at least 500 items) | ALX, 100.0% (states with at least 2 items) |
| Monthly sales chart | last month (3 days of September 2018) left out | March 2025 (4 days) left out: 50, 350, 500 |
| Power BI theme | "Retail Supplier Warehouse", `#2563EB` | "Client B warehouse", `#0F766E`, page `#F0FDFA` |
| Notebook | 0 errors | 0 errors; chart titles name Client B Market, amounts in EGP |

**Clear failures**, one line each, run on the Client B clone before the database was touched:

```
config/client.yaml is missing rules.top_sellers
.env is missing DB_PASSWORD (copy .env.example to .env)
missing input file data/input/suppliers.csv (inputs.sellers in config/client.yaml)
data/input/items.csv is missing column(s): price
data/input/dept_map.csv has no department for category code(s): D-02
```

**Nothing hard-coded:** this search over the code (`*.py`, `dbt/**/*.sql`, `dbt/**/*.yml`, `powerbi/03-measures.dax`), the Power Query M code and the notebook's source cells finds no client value:

```
\bBRL\b|Sample online store|Retail Supplier Warehouse|olist_|5441|8091|#[0-9A-Fa-f]{6}\b|\b100\b|\b500\b|Cairo|2018-09|\b2017\b|departments\.csv
```

Its only matches are the notebook's percentage arithmetic (`* 100`, `set_ylim(0, 100)`) and the demo server in the Warehouse M query, which `01-power-query.md` says to change for a client (as in the pilot). `docker-compose.yml` keeps the published ports and the database name, with a note in `client.yaml`. The README, the diagrams in `docs/` and the numbers in `powerbi/06-checks.md` and `08-build-checklist.md` describe the demo run, so they keep its values on purpose.

**Nothing broke:** the demo ran first on the same commit, from empty volumes: the same 31 passing tests and every number above unchanged from before the template work. The drill ran in a separate clone, so it could not change the demo.
