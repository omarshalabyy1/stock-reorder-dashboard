# 1. Power Query

The report reads the local warehouse: PostgreSQL on `127.0.0.1:5447`, database `stock`, after
`docker compose up -d` and one run of the `stock_reorder` DAG (steps 1 to 4 of
`08-build-checklist.md`). Nothing is read from files.

Why `127.0.0.1` and not `localhost`: Docker binds the warehouse to `127.0.0.1` only, and on
Windows `localhost` can resolve to the IPv6 address first, where nothing listens.

Open Power BI Desktop, then **Home > Transform data** to open the Power Query editor. For each query
below: **Home > New source > Blank query**, rename it (right-click > Rename) to the name in the
heading, open **Home > Advanced editor**, delete what is there and paste the code.

| Query | Source | Columns | Renames | Load |
|---|---|---|---|---|
| `StockRule` | the `stock_rule` view in the warehouse | 14 | none | yes |
| `Item` | the `item` table in the warehouse | 2 | none | yes |

Why a SQL query in each source: `stock_rule` is a materialized view, and Power BI's PostgreSQL
navigator lists tables and plain views only. The query names every column, so the column order and
set never change when the warehouse does.

Why no renames: the names match `sql/03_rules.sql` and the SQL in `06-checks.md`, so a number on a
card can be checked against the warehouse word for word. Visuals show friendly names, set on the
visual (`04-pages.md`).

Why no query is disabled from load: both are used by the model; there are no helper queries.

The three small tables (`Date`, `Store`, `Status`) are DAX tables made in the model
(`02-model.md`), not Power Query.

## The first connection

Power BI asks three things the first time a query runs:

1. **Credentials:** choose **Database**, user name `stock`, password `stock` (the local warehouse in
   `docker-compose.yml`, reachable only from this laptop), level `127.0.0.1:5447;stock`, **Connect**.
2. **Encryption:** the local warehouse has no SSL certificate. If Power BI says it could not connect
   with an encrypted connection, choose **OK** to connect without encryption.
3. **Native database query:** "Permission is required to run this native database query" > **Run**.

## StockRule (loads)

The fact table: one row per day, store and item, with that day's closing stock judged by the rules.
913,000 rows.

```m
let
    Source = PostgreSQL.Database(
        "127.0.0.1:5447",
        "stock",
        [Query = "SELECT date, store, item, units_sold, units_received, on_hand, on_order,
                         stock_value, daily_demand, safety_stock, reorder_point, days_of_cover,
                         status, order_qty
                  FROM stock_rule"]
    ),
    ChangedTypes = Table.TransformColumnTypes(
        Source,
        {
            {"date", type date}, {"store", Int64.Type}, {"item", Int64.Type},
            {"units_sold", Int64.Type}, {"units_received", Int64.Type},
            {"on_hand", Int64.Type}, {"on_order", Int64.Type},
            {"stock_value", Currency.Type},
            {"daily_demand", type number}, {"safety_stock", type number},
            {"reorder_point", type number}, {"days_of_cover", type number},
            {"status", type text}, {"order_qty", Int64.Type}
        }
    )
in
    ChangedTypes
```

Applied steps: **Source** (the SQL query) > **ChangedTypes**.

| Column | Type in Power BI | Meaning |
|---|---|---|
| `date` | Date | the day; stock is counted at closing |
| `store` | Whole number | store 1 to 10 |
| `item` | Whole number | item 1 to 50 |
| `units_sold` | Whole number | units sold that day |
| `units_received` | Whole number | units delivered that morning |
| `on_hand` | Whole number | units on the shelf at closing |
| `on_order` | Whole number | units ordered and not yet delivered |
| `stock_value` | Fixed decimal number | `on_hand` × the item's unit cost |
| `daily_demand` | Decimal number | average daily sales of the last 28 days |
| `safety_stock` | Decimal number | 1.65 × the daily swing × 2 |
| `reorder_point` | Decimal number | daily demand × 4 + safety stock |
| `days_of_cover` | Decimal number | `on_hand` ÷ daily demand; blank when nothing sells |
| `status` | Text | Out of stock, Dead, Reorder, Overstock or OK |
| `order_qty` | Whole number | units to order; 0 when the shelf is not on the reorder list |

`Currency.Type` is Power BI's fixed decimal number, so stock values add up exactly to the cent.

## Item (loads)

One row per item with its unit cost. 50 rows.

```m
let
    Source = PostgreSQL.Database(
        "127.0.0.1:5447",
        "stock",
        [Query = "SELECT item, unit_cost FROM item"]
    ),
    ChangedTypes = Table.TransformColumnTypes(
        Source,
        {{"item", Int64.Type}, {"unit_cost", Currency.Type}}
    )
in
    ChangedTypes
```

Applied steps: **Source** > **ChangedTypes**.

| Column | Type in Power BI | Meaning |
|---|---|---|
| `item` | Whole number | item 1 to 50 |
| `unit_cost` | Fixed decimal number | cost of one unit (generated, see the main README's Data section) |

Then **Home > Close & apply**. StockRule takes about half a minute to load.

## After a new day of data

Run the DAG again (or `python pipeline.py`), then **Home > Refresh** in Power BI.
