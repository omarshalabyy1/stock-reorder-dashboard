# 4. The pages

Canvas: View > Page view > Fit to page; Format page > Canvas settings > 16:9 (1280 x 720). Positions
are x, y, width, height in pixels (Format > General > Properties > Size and position). Every visual
gets the title written here (Format > General > Title).

## Page 1: Reorder list

The morning view: what to order today, and how the 500 shelves stand.

| Visual | Position | Fields | Settings |
|---|---|---|---|
| Text box | 20, 12, 880, 52 | "Reorder list" (20 pt, bold) and below it "Stock at closing on the day picked. The 7am email lists the same rows." (11 pt, grey) | - |
| Slicer "Day" | 940, 12, 320, 56 | Date[Date] | Style Dropdown (Slicer settings > Options > Style), Single select on, pick **31 Dec 2017** |
| Slicer "Store" | 20, 72, 1240, 48 | Store[store] | Style Tile, Multi-select with Ctrl, "Select all" on, nothing picked |
| Card | 20, 132, 236, 100 | [Items to Reorder] | Callout amber (#F59E0B) |
| Card | 271, 132, 236, 100 | [Units to Order] | |
| Card | 522, 132, 236, 100 | [Out of Stock Items] | |
| Card | 773, 132, 236, 100 | [Stock Value] | |
| Card | 1024, 132, 236, 100 | [Slow Stock Share] | |
| Table "To reorder" | 20, 248, 800, 452 | Store[store], Item[item], StockRule: on_hand, on_order, days_of_cover, reorder_point, order_qty | Rename the columns (double-click in Columns): Store, Item, On hand, On order, Days left, Reorder point, Order. Filter on this visual: order_qty is greater than 0. Sort by Days left, ascending. Cell elements: Days left background by rules, value < 4 = #FDE68A; Order data bars, amber |
| Bar chart "Shelves by status" | 836, 248, 424, 452 | Y-axis Status[status], X-axis [Store Items] | Sort by Status[status] ascending (uses Status Order). Data labels on. Colours (Format > Bars > Colors, show all): Out of stock #B45309, Reorder #F59E0B, OK #94A3B8, Overstock #0E1630, Dead #CBD5E1 |

Check: on 31 Dec 2017 the table is empty (nothing to reorder); pick 16 Jul 2017 and it lists 111 rows.

## Page 2: Stock vs reorder point

The README's mental-model picture, drawn from the real data for one shelf.

| Visual | Position | Fields | Settings |
|---|---|---|---|
| Text box | 20, 12, 1240, 52 | "Stock vs reorder point" and "One shelf: its stock at closing, the reorder point, the safety stock, and the days it was on the reorder list." | - |
| Slicer "Store" | 20, 72, 200, 56 | Store[store] | Dropdown, Single select, pick **1** |
| Slicer "Item" | 236, 72, 200, 56 | Item[item] | Dropdown, Single select, pick **15** |
| Slicer "Days" | 452, 72, 420, 56 | Date[Date] | Style Between, **1 Jun 2017** to **31 Aug 2017** |
| Card | 888, 72, 180, 80 | [Empty Shelf Days] | |
| Card | 1080, 72, 180, 80 | [Units Sold] | |
| Line chart "Stock and its two lines" | 20, 168, 1240, 330 | X-axis Date[Date] (type Continuous), Y-axis [Stock On Hand], [Reorder Point], [Safety Stock], [Stock When Flagged] | Lines (Format > Lines, per series): Stock On Hand navy 3 px; Reorder Point amber, dashed; Safety Stock grey, dotted; Stock When Flagged stroke width 0 with Markers on, circle, amber, size 6. Legend top |
| Column chart "Empty shelf days per month" | 20, 514, 1240, 190 | X-axis Date[Month], Y-axis [Empty Shelf Days] | Sort by Date[Month] ascending. Columns amber. Data labels on |

## Page 3: Slow stock

Where the cash sits on the shelves.

| Visual | Position | Fields | Settings |
|---|---|---|---|
| Text box | 20, 12, 880, 52 | "Slow stock" and "Stock value in items with more than 30 days of cover, on the day picked." | - |
| Slicer "Day" | 940, 12, 320, 56 | Date[Date] | Same as page 1 and synced with it (below) |
| Slicer "Store" | 20, 72, 1240, 48 | Store[store] | Same as page 1 and synced with it |
| Card | 20, 132, 405, 100 | [Stock Value] | |
| Card | 437, 132, 405, 100 | [Slow Stock Value] | Callout amber |
| Card | 855, 132, 405, 100 | [Slow Stock Share] | Callout amber |
| Bar chart "Stock value by status" | 20, 248, 400, 220 | Y-axis Status[status], X-axis [Stock Value] | Sorted by status. Same colours as page 1. Data labels on |
| Bar chart "Slow stock value by item, top 15" | 436, 248, 824, 220 | Y-axis Item[item], X-axis [Slow Stock Value] | Filter on this visual: Item[item] Top N, show Top 15 by [Slow Stock Value]. Sort by Slow Stock Value, descending. Bars navy |
| Line chart "Slow stock share at each month end" | 20, 484, 1240, 220 | X-axis Date[Month], Y-axis [Slow Stock Share] | Sort by Date[Month] ascending. Line amber. Edit interactions (below): the Day slicer does not filter it |

## Slicer sync, interactions, tooltips

- **Sync slicers** (View > Sync slicers): the Day slicers of pages 1 and 3 in one group named `Day`,
  and the Store slicers of pages 1 and 3 in one group named `Store`, synced and visible on both.
  The page 2 slicers stay on their own.
- **Edit interactions** (Format > Edit interactions): on page 3, select the Day slicer and set the
  month-end line chart to None, so it always shows every month.
- **Tooltips:** the default ones. **Drill-through and bookmarks:** none.
