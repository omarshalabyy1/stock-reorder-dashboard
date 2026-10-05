-- The stock rules, written once. The morning email, the Power BI report and the analysis notebook
-- all read them from here. One row per day, store and item: that day's closing stock judged
-- against the forecast. The thresholds are client settings (rules in config/client.yaml, set by
-- pipeline.py as client.*); each item's delivery time is lead_days in the items input file.
--
--   safety stock   service_z x daily swing x √lead_days   covers that share of the ups and downs in
--                                                       demand until the delivery
--   reorder point  daily demand x lead_days + safety stock   order when the stock falls to this
--   position       on hand + on order                   what the shelf will have, counting orders on the way
--   days of cover  on hand / daily demand               how long the shelf lasts at the current pace
--   order qty      daily demand x (lead_days + cover_days_after_delivery) + safety stock - position
--                                                       enough until the delivery and the days after it
--   status         Out of stock   nothing left at closing
--                  Dead           stock on the shelf, not one sale in the forecast window
--                  Reorder        position at or below the reorder point
--                  Overstock      more than overstock_days of cover
--                  OK             everything else

DROP MATERIALIZED VIEW IF EXISTS stock_rule;

CREATE MATERIALIZED VIEW stock_rule AS
WITH judged AS (
    SELECT s.date, s.store, s.item, sa.units_sold, s.units_received, s.on_hand, s.on_order,
           s.on_hand + s.on_order                AS position,
           s.on_hand * i.unit_cost               AS stock_value,
           i.lead_days,
           f.daily_demand,
           current_setting('client.service_z')::numeric * coalesce(f.daily_swing, 0) * sqrt(i.lead_days::numeric)
                                                 AS safety_stock
    FROM stock s
    JOIN sales sa   USING (date, store, item)
    JOIN forecast f USING (date, store, item)
    JOIN item i     USING (item)
)
SELECT date, store, item, units_sold, units_received, on_hand, on_order, stock_value,
       round(daily_demand, 2)                               AS daily_demand,
       round(safety_stock, 2)                               AS safety_stock,
       round(daily_demand * lead_days + safety_stock, 2)    AS reorder_point,
       round(on_hand / nullif(daily_demand, 0), 1)          AS days_of_cover,
       CASE WHEN on_hand = 0                                         THEN 'Out of stock'
            WHEN daily_demand = 0                                    THEN 'Dead'
            WHEN position <= daily_demand * lead_days + safety_stock THEN 'Reorder'
            WHEN on_hand > daily_demand * current_setting('client.overstock_days')::int THEN 'Overstock'
            ELSE 'OK' END                                   AS status,
       CASE WHEN position <= daily_demand * lead_days + safety_stock
            THEN ceil(daily_demand * (lead_days + current_setting('client.cover_days_after_delivery')::int)
                      + safety_stock - position)::int
            ELSE 0 END                                      AS order_qty
FROM judged;

CREATE INDEX ON stock_rule (date);
