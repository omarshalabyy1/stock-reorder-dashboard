# 6. Checks: the numbers the report must show

Every number below comes from the notebook (`analysis/analysis.ipynb`, sections 1 to 7) and is
checked again by the SQL query under it, run against the warehouse:

```bash
docker exec -it stock-reorder-warehouse-1 psql -U stock -d stock
```

No store is picked unless a row says so. If a card differs, the build is wrong somewhere: check the
relationships, the measure's filter and the slicer's pick first. `08-build-checklist.md` says at
which step each number is checked.

## The warehouse, before Power BI

After the DAG run (`08-build-checklist.md`, steps 3 to 5).

| Number | Must show |
|---|---|
| Rows in `stock_rule` | 913,000 |
| Stock-outs in the history | 4,052 |
| ...with a reorder flag in the 7 days before | 4,052 |
| ...flagged in time to order (5 or more days before) | 1,643 (41%) |

```sql
SELECT count(*) FROM stock_rule;

WITH r AS (
  SELECT on_hand,
         lag(on_hand) OVER w AS prev_on_hand,
         bool_or(order_qty > 0) OVER (w ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) AS flagged,
         bool_or(order_qty > 0) OVER (w ROWS BETWEEN 7 PRECEDING AND 5 PRECEDING) AS in_time
  FROM stock_rule
  WINDOW w AS (PARTITION BY store, item ORDER BY date)
)
SELECT count(*) AS stockouts,
       count(*) FILTER (WHERE flagged) AS flagged,
       count(*) FILTER (WHERE in_time) AS flagged_in_time
FROM r
WHERE on_hand = 0 AND coalesce(prev_on_hand, 1) > 0;
```

The backtest numbers are not on the report: they are the project's result, measured in the notebook.

## Table rows (Table view, bottom left)

| Table | Rows |
|---|---|
| StockRule | 913,000 |
| Item | 50 |
| Store | 10 |
| Status | 5 |
| Date | 1,826 (1 Jan 2013 to 31 Dec 2017) |

## Page 1: Reorder list, and the cards of page 3

| Card | 31 Dec 2017 (the last day) | 16 Jul 2017 (a summer Sunday) |
|---|---|---|
| Items to Reorder (Shelves to reorder) | 0 | 111 |
| Units to Order | 0 | 98,020 |
| Out of Stock Items (Empty shelves) | 0 | 0 |
| Stock Value | 7,707,022 | 5,826,826 |
| Slow Stock Share | 36.9% | 12.6% |
| Shelves by status (#10) | OK 343, Overstock 157 | OK 342, Reorder 111, Overstock 47 |

```sql
SELECT date,
       count(*) FILTER (WHERE order_qty > 0)                     AS items_to_reorder,
       sum(order_qty)                                            AS units_to_order,
       count(*) FILTER (WHERE on_hand = 0)                       AS out_of_stock_items,
       round(sum(stock_value))                                   AS stock_value,
       round(100.0 * sum(stock_value) FILTER (WHERE status = 'Overstock') / sum(stock_value), 1) AS slow_stock_share
FROM stock_rule
WHERE date IN ('2017-12-31', '2017-07-16')
GROUP BY date;

SELECT date, status, count(*) FROM stock_rule
WHERE date IN ('2017-12-31', '2017-07-16') GROUP BY date, status ORDER BY date, status;
```

## Page 2: Stock vs reorder point (store 1, item 15, 1 Jun to 31 Aug 2017)

| Card | Must show |
|---|---|
| Empty Shelf Days | 11 |
| Units Sold | 9,494 |

```sql
SELECT count(*) FILTER (WHERE on_hand = 0) AS empty_shelf_days, sum(units_sold) AS units_sold
FROM stock_rule
WHERE store = 1 AND item = 15 AND date BETWEEN '2017-06-01' AND '2017-08-31';
```

## Page 3: Slow stock (31 Dec 2017)

| Visual | Must show |
|---|---|
| Stock Value (#4) | 7,707,022 |
| Slow Stock Value (#5) | 2,842,562 |
| Slow Stock Share (#6) | 36.9% |
| Stock value by status (#7) | OK 4,864,461, Overstock 2,842,562 |
| Month-end line (#9), 2017, rounded to whole percent | Jan 42%, Feb 36%, Mar 29%, Apr 19%, May 18%, Jun 14%, Jul 8%, Aug 18%, Sep 18%, Oct 21%, Nov 20%, Dec 37% |

```sql
SELECT status, round(sum(stock_value)) AS stock_value
FROM stock_rule WHERE date = '2017-12-31' GROUP BY status;

SELECT date,
       round(100.0 * sum(stock_value) FILTER (WHERE status = 'Overstock') / sum(stock_value)) AS slow_pct
FROM stock_rule
WHERE date = (date_trunc('month', date) + interval '1 month - 1 day')::date
  AND date >= '2017-01-01'
GROUP BY date ORDER BY date;
```

## The whole history (a card with no filter, `08-build-checklist.md` step 17)

| Number | Must show |
|---|---|
| Units Sold, all days | 47,514,528 |
| Empty Shelf Days, all days | 4,434 |
| Empty Shelf Days, 2017 | 567 |

```sql
SELECT count(*) AS rows, sum(units_sold) AS units_sold,
       count(*) FILTER (WHERE on_hand = 0) AS empty_shelf_days,
       count(*) FILTER (WHERE on_hand = 0 AND date >= '2017-01-01') AS empty_shelf_days_2017
FROM stock_rule;
```
