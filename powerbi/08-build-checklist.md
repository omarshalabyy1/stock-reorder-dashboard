# 8. Build checklist

Follow in order. A **Check** line is a number to verify before going on (all from `06-checks.md`); if
it is off, fix that step first.

## Prepare the warehouse

1. In the repo folder (`C:\Users\you\GitHub\stock-reorder-dashboard`), on a fresh clone only, make
   the demo data: `python data/demo/make_data.py` (a client puts their files in `data/input/` instead).
   **Check:** it prints `913,000 sales rows, 913,000 stock rows, 50 items`.
2. Start Docker Desktop, then run `docker compose up -d`. Wait a minute or two, then open Airflow on
   port 8097 (no login).
3. In Airflow: **Dags > stock_reorder > Trigger**. Wait until load, forecast, rules and alert are all
   green (about 5 minutes). Instead of Airflow, `python pipeline.py` runs the same four steps.
4. **Check:** `docker exec stock-reorder-warehouse-1 psql -U stock -d stock -c "SELECT count(*) FROM stock_rule"`
   prints 913000.
5. **Check:** run the backtest query in `06-checks.md` ("The warehouse, before Power BI"):
   4052 stock-outs · 4052 flagged · 1643 flagged in time.

## Prepare Power BI Desktop

6. Open Power BI Desktop, then **Blank report**.
7. **File > Options and settings > Options > Current file**:
   - **Data load:** untick **Auto date/time**.
   - **Report settings:** tick **Change default visual interaction from cross highlighting to cross filtering**.
8. **View > Themes > Browse for themes**, pick `powerbi/05-theme.json`.

## Power Query (`01-power-query.md`)

9. **Home > Transform data**. Create the two queries in this order, pasting each one's M code:
   `StockRule`, `Item`. Answer the first-connection questions (user `warehouse.user`, password `DB_PASSWORD` from `.env`, no
   encryption, **Run** the native query).
10. **Home > Close & apply** (about half a minute).
11. Open **Table view** (second icon on the left) and click each table; the row count is at the
    bottom left.
    **Check:** StockRule 913,000 · Item 50.

## Model (`02-model.md`)

12. **Modeling > New table** three times: `Date`, `Store`, `Status`.
    **Check:** Date 1,826 · Store 10 · Status 5.
13. Mark `Date` as the date table (column `Date`).
14. **Model view**: delete any relationship Power BI made on its own, then create the four
    relationships in the table, each One to many, Single, Active.
15. Sort `Date[Month]` by `Month Number` and `Status[status]` by `Status Order`. Hide the columns
    listed under "Hide columns". Set the column formats and summarization.

## Measures (`03-measures.dax`)

16. **Home > Enter data**, name the table `_Measures`, **Load**. Create the 14 measures in the order
    of the file, each with its format string and display folder. Hide the empty column.
17. On a blank page, drop three cards (Display units: None): `[Stock Value]`, `[Units Sold]`,
    `[Empty Shelf Days]`.
    **Check:** 7,707,022 (the last day, 31 Dec 2017) · 47,514,528 · 4,434. Delete the three cards.

## Page 1: Reorder list (`04-pages.md`)

18. Rename the page to **Reorder list**. Build visuals 1 to 10 in order, with their position, size,
    fields and settings. Leave the Day slicer on **31 Dec 2017**.
19. **Check** on 31 Dec 2017: Shelves to reorder 0 · Units to order 0 · Empty shelves 0 · Stock value
    7,707,022 · Stock value in slow stock 36.9%. Visual 10: OK 343 · Overstock 157. The table is
    empty.
20. **Check:** pick **16 Jul 2017** in the Day slicer: 111 · 98,020 · 0 · 5,826,826 · 12.6%. Visual
    10: OK 342 · Reorder 111 · Overstock 47. The table lists the 111 shelves, the fewest days left
    at the top. Set the Day slicer back to 31 Dec 2017.

## Page 2: Stock vs reorder point (`04-pages.md`)

21. Add a page, rename it **Stock vs reorder point**. Build visuals 1 to 8 in order, with Store **1**,
    Item **15** and Days **1 Jun 2017 to 31 Aug 2017**.
22. **Check:** Days the shelf closed empty 11 · Units sold 9,494. The line chart shows a sawtooth:
    each Friday's delivery barely clears the reorder point, the danger dots sit on the weekends,
    and the stock touches zero just before a delivery (as in `docs/chart-best-seller-summer.png`). Visual 8
    shows three columns, June to August, adding up to 11.

## Sync the slicers, then page 3

23. **View > Sync slicers** as in `04-pages.md` ("Sync the slicers"): the Day and Store slicers of
    page 1, synced and visible on Reorder list and Slow stock.
24. Add a page, rename it **Slow stock**. The two synced slicers are already there (#2, #3). Build
    visuals 1 and 4 to 9.
25. **Check** on 31 Dec 2017: Stock value 7,707,022 · Slow stock value 2,842,562 · Share in slow
    stock 36.9%. Visual 7: OK 4,864,461 · Overstock 2,842,562. Visual 8 shows 15 bars.

## Interactions and filters (`07-interactions.md`)

26. Set the two visual-level filters (page 1 #9, page 3 #8) if not done while building.
27. Set every interaction, page by page, as in the three matrices.
28. **Check:** on page 3, visual 9 shows every month from Jan 2013 to Dec 2017 whatever day is
    picked; its 2017 points round to Jan 42% · Jul 8% · Dec 37% (hover for the values).
29. **Check:** on page 1 pick 16 Jul 2017 and click **Reorder** in visual 10: the table keeps its
    111 shelves and the cards do not change. Click it again to clear, and set the day back to
    31 Dec 2017.
30. **Check:** on page 2 click the July 2017 column: the cards and the line show July only. Click it
    again to clear.

## Save and screenshots

31. **File > Save as** `powerbi/stock-reorder.pbix`.
32. Export each page at 1280 × 720 (a screenshot of the page, or **File > Export > Export to PDF**)
    to `powerbi/screenshots/`:
    - `1-reorder-list.png` with the Day slicer on **16 Jul 2017** (a full list);
    - `2-stock-vs-reorder-point.png` with store 1, item 15, 1 Jun to 31 Aug 2017;
    - `3-slow-stock.png` with the Day slicer on **31 Dec 2017**.
33. In the main `README.md`, replace the line "_Screenshots of the finished pages go here._" with the
    three images, each with its day in the alt text. Commit the `.pbix`, the screenshots and the
    README, and push.
