# 1. Power Query

Two queries, both loaded to the model. Each reads the warehouse with a SQL query, because
`stock_rule` is a materialized view and the PostgreSQL navigator lists only tables and views.

**For each query:** Home > Get data > Blank query > Advanced Editor > replace everything with the
code below > Done > rename the query (right pane, Name) to the name given.

The first time, Power BI asks:

- **Credentials:** choose *Database*, user `stock`, password `stock` (the local warehouse, `docker-compose.yml`).
- **Encryption:** the local warehouse has no SSL; when asked to connect without encryption, choose OK.
- **Native database query:** "Permission is required to run this native database query" > Run.

## StockRule

One row per day, store and item: the day's closing stock judged by the rules (`sql/03_rules.sql`).

```m
let
    Source = PostgreSQL.Database("localhost:5447", "stock", [Query = "SELECT * FROM stock_rule"]),
    Typed = Table.TransformColumnTypes(Source, {
        {"date", type date}, {"store", Int64.Type}, {"item", Int64.Type},
        {"units_sold", Int64.Type}, {"units_received", Int64.Type},
        {"on_hand", Int64.Type}, {"on_order", Int64.Type},
        {"stock_value", Currency.Type},
        {"daily_demand", type number}, {"safety_stock", type number},
        {"reorder_point", type number}, {"days_of_cover", type number},
        {"status", type text}, {"order_qty", Int64.Type}
    })
in
    Typed
```

Applied steps: **Source** (the SQL query) > **Typed** (column types below).

| Column | Type | Meaning |
|---|---|---|
| date | Date | the day (stock at closing) |
| store, item | Whole number | which shelf |
| units_sold, units_received | Whole number | sold that day, delivered that morning |
| on_hand, on_order | Whole number | on the shelf at closing, ordered and not yet delivered |
| stock_value | Fixed decimal | on_hand x unit cost |
| daily_demand, safety_stock, reorder_point | Decimal | the forecast and the two lines |
| days_of_cover | Decimal | how many days the shelf lasts at the current pace (blank when nothing sells) |
| status | Text | Out of stock, Dead, Reorder, Overstock or OK |
| order_qty | Whole number | how many to order (0 when not on the reorder list) |

## Item

One row per item, with its unit cost.

```m
let
    Source = PostgreSQL.Database("localhost:5447", "stock", [Query = "SELECT item, unit_cost FROM item"]),
    Typed = Table.TransformColumnTypes(Source, {{"item", Int64.Type}, {"unit_cost", Currency.Type}})
in
    Typed
```

Applied steps: **Source** > **Typed** (`item` whole number, `unit_cost` fixed decimal).

Then Home > Close & Apply. StockRule loads 913,000 rows (about half a minute).
