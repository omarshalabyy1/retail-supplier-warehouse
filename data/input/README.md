# Input files

The seven files the client supplies, as CSV with a header row, UTF-8. The file names are set in `config/client.yaml` under `inputs`.
Extra columns are ignored and only the columns below are loaded. Before the database is touched, `python load.py` (the `load_raw` task) stops with a one-line message if a file is missing, a required column is not there, or a product category has no department.

## orders (`inputs.orders`)

One row per order.

| Column | Type | Example |
|---|---|---|
| order_id | text, unique | e481f51cbdc54678b7cc49136f2d6af7 |
| customer_id | text, in customers | 9ef432eb6251297304e76186b10a928d |
| order_status | text; `delivered` marks a delivered order, any other value is not delivered | delivered |
| order_purchase_timestamp | timestamp | 2017-10-02 10:56:33 |
| order_delivered_customer_date | timestamp, empty until delivered | 2017-10-10 21:25:13 |
| order_estimated_delivery_date | date (or timestamp) promised to the customer | 2017-10-18 00:00:00 |

## order_items (`inputs.order_items`)

One row per item in an order.

| Column | Type | Example |
|---|---|---|
| order_id | text, in orders | 00010242fe8c5a6d1ba2dd792cb16214 |
| order_item_id | whole number, 1, 2 ... within the order | 1 |
| product_id | text, in products | 4244733e06e7ecb4970a6e2683c13e61 |
| seller_id | text, in sellers | 48436dade18ac8b2bce089ec2a041202 |
| price | decimal, not negative | 58.90 |
| freight_value | decimal, not negative | 13.29 |

## products (`inputs.products`)

| Column | Type | Example |
|---|---|---|
| product_id | text, unique | 1e9e8ef04dbcff4541ed26657ea517e5 |
| product_category_name | text, in departments; empty = department "unknown" | perfumaria |

## sellers (`inputs.sellers`)

The store's suppliers.

| Column | Type | Example |
|---|---|---|
| seller_id | text, unique | 3442f8959a84dea7ee197c632cb2df15 |
| seller_zip_code_prefix | text (leading zeros kept) | 13023 |
| seller_city | text | campinas |
| seller_state | text | SP |

## customers (`inputs.customers`)

| Column | Type | Example |
|---|---|---|
| customer_id | text, unique | 06b8999e2fba1a1fbc88172c00ba8bc7 |
| customer_unique_id | text, the same person across orders | 861eff4711a542e4b93843c6dd7febb0 |
| customer_zip_code_prefix | text (leading zeros kept) | 14409 |
| customer_city | text | franca |
| customer_state | text | SP |

## reviews (`inputs.reviews`)

One row per review; an order reviewed twice keeps its latest review.

| Column | Type | Example |
|---|---|---|
| order_id | text, in orders | 73fc7af87114b39712e6da79b0a377eb |
| review_score | whole number, 1 to 5 | 4 |
| review_creation_date | timestamp | 2018-01-18 00:00:00 |
| review_answer_timestamp | timestamp (breaks ties between two reviews on the same day) | 2018-01-18 21:46:59 |

## departments (`inputs.departments`)

Every `product_category_name` that appears in products, with the department the report shows.

| Column | Type | Example |
|---|---|---|
| category_code | text, unique (any shape) | perfumaria |
| department | text | perfumery |

## The demo files

`departments.csv` is committed. The other six are the Olist files from Kaggle (see Data in the main README); download them into this folder. They are not committed.
