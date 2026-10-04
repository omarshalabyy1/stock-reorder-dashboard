# 6. Checks: the numbers the report must show

Every number below comes from the notebook (`analysis/analysis.ipynb`, section 7) and is checked again
by the SQL query under it, run against the warehouse:

```bash
docker exec -it stock-reorder-warehouse-1 psql -U stock -d stock
```

No store is picked unless a row says so. If a card differs, the build is wrong somewhere: check the
relationships and the measure's filter first.

## Page 1: Reorder list, and page 3: Slow stock

| Card | 31 Dec 2017 (the last day) | 16 Jul 2017 (a summer Sunday) |
|---|---|---|
| Items to Reorder | 0 | 111 |
| Units to Order | 0 | 98,020 |
| Out of Stock Items | 0 | 0 |
| Stock Value | 7,707,022 | 5,826,826 |
| Slow Stock Share | 36.9% | 12.6% |
| Shelves by status | OK 343, Overstock 157 | OK 342, Reorder 111, Overstock 47 |

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

Page 3, the month-end line: 2017 runs from 8% (July) to 42% (January); 37% at December's end.

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

## The whole history (any page with no filters)

| Number | Must show |
|---|---|
| Rows in StockRule | 913,000 |
| Units Sold, all days | 47,514,528 |
| Empty Shelf Days, all days | 4,434 |
| Empty Shelf Days, 2017 | 567 |

```sql
SELECT count(*) AS rows, sum(units_sold) AS units_sold,
       count(*) FILTER (WHERE on_hand = 0) AS empty_shelf_days,
       count(*) FILTER (WHERE on_hand = 0 AND date >= '2017-01-01') AS empty_shelf_days_2017
FROM stock_rule;
```

## The backtest (notebook only, not on the report)

4,052 stock-outs; a flag came before all of them; 1,643 (41%) early enough to order in time.

```sql
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
