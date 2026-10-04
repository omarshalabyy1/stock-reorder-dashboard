# 2. The model

A star: one fact table, `StockRule`, with four small tables around it that every slicer and axis
uses. Open **Model view** (the third icon on the left).

## Tables

| Table | Grain (one row per) | Key | Rows | Made by |
|---|---|---|---|---|
| `StockRule` | day, store and item | `date` + `store` + `item` | 913,000 | Power Query (`01-power-query.md`) |
| `Item` | item | `item` | 50 | Power Query |
| `Store` | store | `store` | 10 | DAX table, below |
| `Status` | status word | `status` | 5 | DAX table, below |
| `Date` | day, 2013-01-01 to 2017-12-31 | `Date` | 1,826 | DAX table, below |
| `_Measures` | holds the measures only | none | 1 (hidden) | Enter data (`03-measures.dax`) |

There are no calculated columns.

## The three DAX tables

For each one: **Modeling > New table**, paste the code, press Enter.

```dax
Date =
VAR FirstDay = MIN ( StockRule[date] )
VAR LastDay = MAX ( StockRule[date] )
RETURN
    ADDCOLUMNS (
        CALENDAR ( FirstDay, LastDay ),
        "Month", FORMAT ( [Date], "mmm yyyy" ),
        "Month Number", YEAR ( [Date] ) * 100 + MONTH ( [Date] )
    )
```

Why: one row per day with no gaps, from the first to the last day in the data, so months group
correctly and the Day slicer lists every day. `Month Number` (201301 to 201712) only sorts `Month`.

```dax
Store =
DISTINCT ( StockRule[store] )
```

Why: one Store slicer that filters the fact table through a relationship, as a star schema should.
`DISTINCT` (not `VALUES`) avoids a circular dependency when the relationship is created.

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

Why: the five words from `sql/03_rules.sql` in a fixed order, most urgent first, so every status
chart lists them the same way. Dead never occurs in this data (no shelf with stock goes 28 days
without a sale) but stays, so the charts keep the same five words and colours if it ever does.

## Mark the date table

Select the `Date` table, then **Table tools > Mark as date table**, pick the `Date` column, **Save**.

Why: Power BI then treats `Date` as the calendar. Also turn off **File > Options and settings >
Options > Current file > Data load > Auto date/time**, so Power BI adds no hidden date tables of its
own.

## Relationships

Drag each "one" column onto its "many" column, then double-click the line and check the settings.

| From (one) | To (many) | Cardinality | Cross-filter direction | Active | Why |
|---|---|---|---|---|---|
| `Date[Date]` | `StockRule[date]` | One to many | Single | Yes | The Day slicer, the date range and the month axes |
| `Store[store]` | `StockRule[store]` | One to many | Single | Yes | The Store slicers |
| `Item[item]` | `StockRule[item]` | One to many | Single | Yes | The Item slicer and the top-items chart |
| `Status[status]` | `StockRule[status]` | One to many | Single | Yes | The status charts and the Slow Stock Value measure |

Power BI may create some of these on its own after Close & apply; delete any other relationship it
made. Why single direction everywhere: filters flow from the small tables to the fact table, never
back, so every number has one meaning.

## Hide columns

Right-click > **Hide in report view**, so slicers and axes always use the small tables:

- `StockRule[date]`, `StockRule[store]`, `StockRule[item]`, `StockRule[status]`: use `Date`, `Store`,
  `Item` and `Status` instead.
- `StockRule[units_sold]`, `StockRule[units_received]`, `StockRule[stock_value]`,
  `StockRule[daily_demand]`, `StockRule[safety_stock]`: used by measures only.
- `Item[unit_cost]`: already inside `stock_value`.
- `Date[Month Number]`, `Status[Status Order]`: used only for sorting.
- The empty column of `_Measures` (after `03-measures.dax`).

`StockRule[on_hand]`, `[on_order]`, `[days_of_cover]`, `[reorder_point]` and `[order_qty]` stay
visible: the reorder list (page 1, visual 9) shows them shelf by shelf.

## Sort by column

| Column | Sort by | Why |
|---|---|---|
| `Date[Month]` | `Date[Month Number]` | Months run Jan 2013 to Dec 2017, not alphabetically |
| `Status[status]` | `Status[Status Order]` | Out of stock first, then Reorder, OK, Overstock, Dead |

Select the column, then **Column tools > Sort by column**.

## Column formats and summarization

Set in **Column tools** with the column selected.

| Column | Format | Summarization | Why |
|---|---|---|---|
| `StockRule[on_hand]`, `[on_order]`, `[order_qty]` | Whole number, thousands separator on | Don't summarize | Units on one shelf; the reorder list shows each shelf's own value |
| `StockRule[reorder_point]` | Decimal number, 0 decimal places, thousands separator on | Don't summarize | A unit count; the decimals are the rule's arithmetic |
| `StockRule[days_of_cover]` | Decimal number, 1 decimal place | Don't summarize | "Days left", as in the morning email |
| `Store[store]`, `Item[item]` | Whole number, thousands separator off | Don't summarize | Names, not amounts |
| `Date[Date]` | Custom `d mmm yyyy` | - | Reads as 31 Dec 2017 in the slicers and checks |

Every other number on the report comes from a measure, with its own format string.

## Display folders

Set on each measure in `03-measures.dax` (**Properties pane > Display folder**), one folder per page:

| Folder | Measures |
|---|---|
| 1 Reorder list | Selected Day, Items to Reorder, Units to Order, Out of Stock Items, Store Items, Stock Value |
| 2 Stock vs reorder point | Units Sold, Empty Shelf Days, Stock On Hand, Reorder Point, Safety Stock, Stock When Flagged |
| 3 Slow stock | Slow Stock Value, Slow Stock Share |

Page 3 also uses Stock Value from folder 1, and page 1 shows Slow Stock Share from folder 3.
