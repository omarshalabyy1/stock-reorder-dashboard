-- The stock rules, written once. The morning email, the Power BI report and the analysis notebook
-- all read them from here. One row per day, store and item: that day's closing stock judged
-- against the forecast. The supplier takes 4 days to deliver.
--
--   safety stock   1.65 x daily swing x 2            covers 95% of the ups and downs in demand over
--                                                    the 4 days to delivery (2 = square root of 4)
--   reorder point  daily demand x 4 + safety stock   order when the stock falls to this
--   position       on hand + on order                what the shelf will have, counting orders on the way
--   days of cover  on hand / daily demand            how long the shelf lasts at the current pace
--   order qty      daily demand x 11 + safety stock - position
--                                                    enough for the 4 days to delivery and a week after
--   status         Out of stock   nothing left at closing
--                  Dead           stock on the shelf, not one sale in 28 days
--                  Reorder        position at or below the reorder point
--                  Overstock      more than 30 days of cover
--                  OK             everything else

DROP MATERIALIZED VIEW IF EXISTS stock_rule;

CREATE MATERIALIZED VIEW stock_rule AS
WITH judged AS (
    SELECT s.date, s.store, s.item, sa.units_sold, s.units_received, s.on_hand, s.on_order,
           s.on_hand + s.on_order                AS position,
           s.on_hand * i.unit_cost               AS stock_value,
           f.daily_demand,
           1.65 * coalesce(f.daily_swing, 0) * 2 AS safety_stock
    FROM stock s
    JOIN sales sa   USING (date, store, item)
    JOIN forecast f USING (date, store, item)
    JOIN item i     USING (item)
)
SELECT date, store, item, units_sold, units_received, on_hand, on_order, stock_value,
       round(daily_demand, 2)                       AS daily_demand,
       round(safety_stock, 2)                       AS safety_stock,
       round(daily_demand * 4 + safety_stock, 2)    AS reorder_point,
       round(on_hand / nullif(daily_demand, 0), 1)  AS days_of_cover,
       CASE WHEN on_hand = 0                                 THEN 'Out of stock'
            WHEN daily_demand = 0                            THEN 'Dead'
            WHEN position <= daily_demand * 4 + safety_stock THEN 'Reorder'
            WHEN on_hand > daily_demand * 30                 THEN 'Overstock'
            ELSE 'OK' END                           AS status,
       CASE WHEN position <= daily_demand * 4 + safety_stock
            THEN ceil(daily_demand * 11 + safety_stock - position)::int
            ELSE 0 END                              AS order_qty
FROM judged;

CREATE INDEX ON stock_rule (date);
