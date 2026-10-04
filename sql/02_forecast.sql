-- Forecast: the expected daily demand per store and item, from recent sales.
-- One row per day, store and item: the average of the last 28 days of sales (that day included),
-- and how much a day's sales swing around it (standard deviation), which sizes the safety stock.
-- "Last 28 rows" means the last 28 days because the load checks no day is missing.

DROP MATERIALIZED VIEW IF EXISTS forecast CASCADE;

CREATE MATERIALIZED VIEW forecast AS
SELECT date, store, item,
       avg(units_sold)          OVER last_28 AS daily_demand,
       stddev_samp(units_sold)  OVER last_28 AS daily_swing
FROM sales
WINDOW last_28 AS (PARTITION BY store, item ORDER BY date ROWS BETWEEN 27 PRECEDING AND CURRENT ROW);
