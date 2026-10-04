-- The warehouse: the three daily exports, as they arrive. The keys stop a day being loaded twice,
-- the checks stop impossible numbers (negative sales or stock) getting in.

CREATE TABLE IF NOT EXISTS item (           -- one row per item
    item       int PRIMARY KEY,
    unit_cost  numeric(8, 2) NOT NULL CHECK (unit_cost > 0)
);

CREATE TABLE IF NOT EXISTS sales (          -- one row per day, store and item
    date        date NOT NULL,
    store       int  NOT NULL,
    item        int  NOT NULL REFERENCES item,
    units_sold  int  NOT NULL CHECK (units_sold >= 0),
    PRIMARY KEY (date, store, item)
);

CREATE TABLE IF NOT EXISTS stock (          -- one row per day, store and item, at closing time
    date            date NOT NULL,
    store           int  NOT NULL,
    item            int  NOT NULL REFERENCES item,
    units_received  int  NOT NULL CHECK (units_received >= 0),
    on_hand         int  NOT NULL CHECK (on_hand >= 0),
    on_order        int  NOT NULL CHECK (on_order >= 0),    -- ordered, not delivered yet
    PRIMARY KEY (date, store, item)
);
