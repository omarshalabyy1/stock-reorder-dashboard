-- Forecast: the expected daily demand per store and item, from recent sales.
-- One row per day, store and item: the average of the last client.forecast_days days of sales (that
-- day included), and how much a day's sales swing around it (standard deviation), which sizes the
-- safety stock. "Last N rows" means the last N days because the load checks no day is missing.
-- pipeline.py sets client.forecast_days from rules.forecast_days in config/client.yaml.

DROP MATERIALIZED VIEW IF EXISTS forecast CASCADE;

CREATE MATERIALIZED VIEW forecast AS
SELECT date, store, item,
       avg(units_sold)          OVER recent AS daily_demand,
       stddev_samp(units_sold)  OVER recent AS daily_swing
FROM sales
WINDOW recent AS (PARTITION BY store, item ORDER BY date
                 ROWS BETWEEN current_setting('client.forecast_days')::int - 1 PRECEDING AND CURRENT ROW);
