# 7. Interactions and filters

## Report setting (once)

**File > Options and settings > Options > Current file > Report settings**: tick **Change default
visual interaction from cross highlighting to cross filtering**.

Why: clicking a bar then filters the other visuals instead of greying out part of each bar, so every
card and chart shows real numbers for what was clicked.

## How to set a cell

Select the source visual (the one you click), then **Format > Edit interactions**. Each other visual
shows icons in its top-right corner: **Filter** (funnel) or **None** (circle with a line). Click the
one the table says. Click **Edit interactions** again to finish.

Numbers are the visual `#` in `04-pages.md`. Text boxes (#1) take no part. Cards are never a source:
clicking a card selects nothing.

## Page 1: Reorder list

| Source (click) | Day slicer #2 | Store slicer #3 | Cards #4-8 | Reorder table #9 | Status bar #10 |
|---|---|---|---|---|---|
| Day slicer #2 | | None | Filter | Filter | Filter |
| Store slicer #3 | None | | Filter | Filter | Filter |
| Reorder table #9 | None | None | None | | None |
| Status bar #10 | None | None | None | Filter | |

- **Slicers never filter each other:** every day and every store always stay pickable.
- **The table (#9) filters nothing:** it is the list to read or export, not a filter.
- **A status in #10** narrows the table to the shelves on the list with that status (Out of stock
  shows which empty shelves need an order). The cards stay on the whole day, so the day's totals
  never change by a click.

## Page 2: Stock vs reorder point

| Source (click) | Store slicer #2 | Item slicer #3 | Days slicer #4 | Cards #5-6 | Line chart #7 | Month columns #8 |
|---|---|---|---|---|---|---|
| Store slicer #2 | | None | None | Filter | Filter | Filter |
| Item slicer #3 | None | | None | Filter | Filter | Filter |
| Days slicer #4 | None | None | | Filter | Filter | Filter |
| Line chart #7 | None | None | None | None | | None |
| Month columns #8 | None | None | None | Filter | Filter | |

- **A month in #8** zooms the line chart and both cards to that month: click July 2017 to see that
  July's empty days and sales. Click it again to clear.
- **A point on the line (#7)** filters nothing: one day of one shelf is already readable from the
  tooltip.

## Page 3: Slow stock

| Source (click) | Day slicer #2 | Store slicer #3 | Cards #4-6 | Status bar #7 | Top items bar #8 | Month-end line #9 |
|---|---|---|---|---|---|---|
| Day slicer #2 | | None | Filter | Filter | Filter | **None** |
| Store slicer #3 | None | | Filter | Filter | Filter | Filter |
| Status bar #7 | None | None | Filter | | None | None |
| Top items bar #8 | None | None | Filter | Filter | | Filter |
| Month-end line #9 | None | None | None | None | None | |

- **The Day slicer does not filter the month-end line (#9):** the line always shows every month end,
  so the day picked can be read against the whole history (8% to 42% across 2017).
- **An item in #8** shows that item across all stores: its stock value and slow share in the cards,
  its status split in #7, and its own month-end history in #9.
- **A status in #7** sets the cards to that status (Stock Value then shows that status's value; the
  share keeps all statuses as its base).

## Filters pane

| Level | Filter | Why |
|---|---|---|
| Visual: page 1 #9 | `StockRule[order_qty]` **is greater than** `0` (Filter type: Advanced filtering) | The table is the reorder list: only shelves with something to order |
| Visual: page 3 #8 | `Item[item]` Filter type **Top N**, Show items **Top 15**, By value `[Slow Stock Value]`, **Apply filter** | Fifteen bars stay readable; the rest are in the card total |
| Page level | none | Each page's slicers do the filtering, visibly |
| Report level | none | Every page covers the whole history |

## Not used, and why

- **Drill-through:** none. Page 2 has its own Store and Item slicers; a drill-through filter from
  page 1 would fight them and leave the page blank when they disagree.
- **Bookmarks and buttons:** none. Three pages and their tabs are the whole navigation.
- **Tooltip pages:** none. Page 2 #7 uses the default tooltip with `[Units Sold]` added to its
  Tooltips well; every other visual uses the default tooltip.
