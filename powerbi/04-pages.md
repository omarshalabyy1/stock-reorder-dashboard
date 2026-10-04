# 4. Pages and visuals

Canvas: 16:9, 1280 × 720 (the default). Set each visual's position and size in **Format > General >
Properties**: `x, y, w, h` in pixels from the top-left corner. Apply the theme (`05-theme.json`)
first, so colours and fonts are already right.

Rename the three pages (double-click the tab) to **Reorder list**, **Stock vs reorder point** and
**Slow stock**.

**Colours** are slots of the shared theme, never typed hex codes. Data colours 1 to 6 are the top row
of every colour picker: 1 blue, 2 navy, 3 light blue, 4 slate, 5 deep blue, 6 pale blue. **Danger**
is the theme's "bad" colour; it is not in the picker, so choose **Custom color** and type `C2410C`.

**Number formats** come from each measure's format string (`03-measures.dax`) and the column formats
(`02-model.md`); no visual sets its own. On every card set **Format > Visual > Callout value >
Display units: None**, so the card shows the full number (7,707,022, not 7.71M) as in
`06-checks.md`. Chart axes keep Auto display units.

**Titles:** every visual except text boxes and slicers shows its title (**Format > General > Title**,
text as given below). Slicer headers show the slicer's name. Visuals are listed in build order; the
`#` is used in `07-interactions.md` and `08-build-checklist.md`.

## Page 1: Reorder list

What to order this morning, and how the 500 shelves stand on the day picked.

| # | Visual | x, y, w, h | Fields | Settings |
|---|---|---|---|---|
| 1 | Text box | 24, 16, 860, 52 | "Reorder list: what to order this morning" | Segoe UI Semibold 20, colour theme colour 2 |
| 2 | Slicer "Day" | 900, 12, 356, 60 | Field: `Date[Date]` | Slicer settings > Options > Style: **Dropdown**. Selection: **Single select** on. Header text "Day". Pick **31 Dec 2017**. Search on (… > Search) to type a day |
| 3 | Slicer "Store" | 24, 84, 1232, 52 | Field: `Store[store]` | Style: **Tile**. Selection: multi-select with Ctrl, "Select all" option on. Header text "Store". Nothing picked |
| 4 | Card | 24, 148, 240, 96 | `[Items to Reorder]` | Title "Shelves to reorder". Callout colour theme colour 1 |
| 5 | Card | 272, 148, 240, 96 | `[Units to Order]` | Title "Units to order" |
| 6 | Card | 520, 148, 240, 96 | `[Out of Stock Items]` | Title "Empty shelves". Callout colour danger |
| 7 | Card | 768, 148, 240, 96 | `[Stock Value]` | Title "Stock value at cost" |
| 8 | Card | 1016, 148, 240, 96 | `[Slow Stock Share]` | Title "Stock value in slow stock" |
| 9 | Table | 24, 260, 820, 444 | Columns in this order: `Store[store]`, `Item[item]`, `StockRule[on_hand]`, `StockRule[on_order]`, `StockRule[days_of_cover]`, `StockRule[reorder_point]`, `StockRule[order_qty]` | Title "To reorder, most urgent first". Rename the columns on the visual (double-click in the Columns well): Store, Item, On hand, On order, Days left, Reorder point, Order. Visual-level filter `order_qty` is greater than 0 (`07-interactions.md`). Sort by Days left, ascending. Totals off. Cell elements: **Days left** font colour by rules, value < 4 → danger; **Order** data bars, positive bar theme colour 1. Column headers in bold |
| 10 | Clustered bar chart | 860, 260, 396, 444 | Y-axis: `Status[status]`; X-axis: `[Store Items]` | Title "Shelves by status". Sort axis by `status`, ascending (Out of stock at the top). Data labels on. Bars > Colors, Show all: Out of stock danger, Reorder theme colour 1, OK theme colour 6, Overstock theme colour 2, Dead theme colour 4. X-axis title off |

On 31 Dec 2017 the table (#9) is empty: no shelf is at its reorder point that Sunday. Pick 16 Jul
2017 to see a full list (111 shelves).

## Page 2: Stock vs reorder point

One shelf, day by day: the mental model in the main README, drawn from the data.

| # | Visual | x, y, w, h | Fields | Settings |
|---|---|---|---|---|
| 1 | Text box | 24, 16, 560, 52 | "Stock vs reorder point: one shelf, day by day" | Segoe UI Semibold 20, colour theme colour 2 |
| 2 | Slicer "Store" | 600, 12, 150, 60 | Field: `Store[store]` | Style: **Dropdown**. Single select on. Header text "Store". Pick **1** |
| 3 | Slicer "Item" | 766, 12, 150, 60 | Field: `Item[item]` | Style: **Dropdown**. Single select on. Header text "Item". Pick **15** |
| 4 | Slicer "Days" | 932, 12, 324, 60 | Field: `Date[Date]` | Style: **Between**. Header text "Days". Set **1 Jun 2017** to **31 Aug 2017** |
| 5 | Card | 24, 84, 612, 96 | `[Empty Shelf Days]` | Title "Days the shelf closed empty". Callout colour danger |
| 6 | Card | 644, 84, 612, 96 | `[Units Sold]` | Title "Units sold" |
| 7 | Line chart | 24, 196, 1232, 320 | X-axis: `Date[Date]`; Y-axis: `[Stock On Hand]`, `[Reorder Point]`, `[Safety Stock]`, `[Stock When Flagged]`; Tooltips: `[Units Sold]` | Title "Stock at closing, reorder point and safety stock". X-axis type: **Continuous**. Legend on, position Top. Lines, per series: Stock On Hand theme colour 2, width 3; Reorder Point theme colour 1, width 2, line style Dashed; Safety Stock theme colour 4, width 2, line style Dotted; Stock When Flagged width 0 (no line; if the box refuses 0, set its Transparency to 100%), Markers on, shape circle, size 6, colour danger. Data labels off |
| 8 | Clustered column chart | 24, 532, 1232, 172 | X-axis: `Date[Month]`; Y-axis: `[Empty Shelf Days]` | Title "Empty shelf days per month". X-axis type: **Categorical**. Sort axis by `Month`, ascending. Columns colour danger. Data labels on. Y-axis title off |

The line chart's flags (danger dots) sit on the weekends; the shelf empties on Thursdays, the day
before the Friday delivery.

## Page 3: Slow stock

Where cash sits on the shelves, on the day picked and at every month end.

| # | Visual | x, y, w, h | Fields | Settings |
|---|---|---|---|---|
| 1 | Text box | 24, 16, 860, 52 | "Slow stock: cash sitting on the shelves" | Segoe UI Semibold 20, colour theme colour 2 |
| 2 | Slicer "Day" | 900, 12, 356, 60 | Field: `Date[Date]` | Not built by hand: the synced copy of page 1 #2, placed here by Sync slicers (below) |
| 3 | Slicer "Store" | 24, 84, 1232, 52 | Field: `Store[store]` | Not built by hand: the synced copy of page 1 #3 |
| 4 | Card | 24, 148, 405, 96 | `[Stock Value]` | Title "Stock value at cost" |
| 5 | Card | 437, 148, 405, 96 | `[Slow Stock Value]` | Title "Slow stock value". Callout colour danger |
| 6 | Card | 851, 148, 405, 96 | `[Slow Stock Share]` | Title "Share in slow stock". Callout colour danger |
| 7 | Clustered bar chart | 24, 260, 400, 220 | Y-axis: `Status[status]`; X-axis: `[Stock Value]` | Title "Stock value by status". Sort axis by `status`, ascending. Data labels on. Same status colours as page 1 #10. X-axis title off |
| 8 | Clustered bar chart | 440, 260, 816, 220 | Y-axis: `Item[item]`; X-axis: `[Slow Stock Value]` | Title "Slow stock value by item, top 15". Visual-level filter: `Item[item]` Top N, Show items Top 15, By value `[Slow Stock Value]` (`07-interactions.md`). Sort by Slow Stock Value, descending. Bars theme colour 2. Data labels on. X-axis title off |
| 9 | Line chart | 24, 496, 1232, 208 | X-axis: `Date[Month]`; Y-axis: `[Slow Stock Share]` | Title "Slow stock share at each month end". X-axis type: **Categorical**. Sort axis by `Month`, ascending. Line theme colour 1, width 2, Markers on. Data labels off. Not filtered by the Day slicer (`07-interactions.md`) |

## Sync the slicers

**View > Sync slicers**:

Do this after page 1 is built and before building page 3:

- Select the Day slicer (page 1 #2): tick **Sync** and **Visible** for Reorder list and Slow stock;
  leave Stock vs reorder point unticked. A copy appears on Slow stock at the same place: that is
  page 3 #2.
- Select the Store slicer (page 1 #3): the same, Reorder list and Slow stock. Its copy is page 3 #3.

Page 2's slicers (Store, Item, Days) are its own and are not synced: page 2 shows one shelf over a
range of days, while pages 1 and 3 show every shelf on one day.
