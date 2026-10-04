# 2. The model

A star: one fact table (StockRule) and four small dimension tables around it.

| Table | Grain (one row per) | Key | Made by |
|---|---|---|---|
| StockRule | day, store and item | date + store + item | Power Query |
| Item | item | item | Power Query |
| Store | store | store | DAX, below |
| Date | day | Date | DAX, below |
| Status | status | status | DAX, below |

## The three DAX tables

Modeling > New table, paste each one.

```dax
Date =
VAR FirstDay = MIN ( StockRule[date] )
VAR LastDay = MAX ( StockRule[date] )
RETURN
    ADDCOLUMNS (
        CALENDAR ( FirstDay, LastDay ),
        "Year", YEAR ( [Date] ),
        "Month", FORMAT ( [Date], "mmm yyyy" ),
        "Month Number", YEAR ( [Date] ) * 100 + MONTH ( [Date] ),
        "Weekday", FORMAT ( [Date], "ddd" ),
        "Weekday Number", WEEKDAY ( [Date], 2 )
    )
```

```dax
Store = DISTINCT ( StockRule[store] )
```

```dax
Status =
DATATABLE (
    "status", STRING,
    "Status Order", INTEGER,
    {
        { "Out of stock", 1 },
        { "Reorder", 2 },
        { "OK", 3 },
        { "Overstock", 4 },
        { "Dead", 5 }
    }
)
```

**Mark the date table:** select the Date table > Table tools > Mark as date table > column `Date`.

## Relationships

Model view > Manage relationships > New. All are one-to-many, single filter direction (from the
dimension to StockRule), active.

| From (one) | To (many) |
|---|---|
| Date[Date] | StockRule[date] |
| Store[store] | StockRule[store] |
| Item[item] | StockRule[item] |
| Status[status] | StockRule[status] |

## Sort by column

| Column | Sort by |
|---|---|
| Date[Month] | Date[Month Number] |
| Date[Weekday] | Date[Weekday Number] |
| Status[status] | Status[Status Order] |

## Hide (right-click > Hide in report view)

- StockRule: `date`, `store`, `item`, `status` (filter through the dimensions instead), `units_sold`,
  `units_received`, `stock_value`, `daily_demand`, `safety_stock` (used by measures only).
- Date: `Month Number`, `Weekday Number`. Status: `Status Order`. Item: `unit_cost`.

## Formats and summarization (Column tools)

| Column | Format | Summarization |
|---|---|---|
| StockRule[on_hand], [on_order], [order_qty] | Whole number, thousands separator | Sum |
| StockRule[reorder_point] | Whole number, thousands separator (0 decimals) | Sum |
| StockRule[days_of_cover] | Decimal, 1 decimal place | Sum |
| Store[store], Item[item] | Whole number | Don't summarize |
| Date[Date] | `d mmm yyyy` | - |

(Each row of the reorder list is one day, store and item, so Sum shows the row's own value.)

## Display folders (Model view > select the measure > Properties > Display folder)

- **Day:** the measures for one picked day (`03-measures.dax`, first block).
- **History:** the measures over a period (second block).
