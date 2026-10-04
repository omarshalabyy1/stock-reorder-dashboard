# Power BI: build the report step by step

The report reads the local warehouse (`stock_rule` and `item` in PostgreSQL) and answers three
questions:

1. **Reorder list:** on a given morning, which shelves must be reordered, how many units, and which
   are already empty?
2. **Stock vs reorder point:** for one item in one store, how did its stock move against the reorder
   point and the safety stock, and when was the shelf empty?
3. **Slow stock:** how much stock value sits in shelves with more than 30 days of cover, in which
   items, and how that share moves month by month?

Everything below is copy and paste. **Start with [`08-build-checklist.md`](08-build-checklist.md)**:
33 numbered steps from `docker compose up -d` and the DAG run to the last screenshot, with a check
number at each point. It points to the other files:

| File | What it holds |
|---|---|
| [`01-power-query.md`](01-power-query.md) | Two queries (M code) on the local warehouse: columns, types, why no renames |
| [`02-model.md`](02-model.md) | Five tables (three made in DAX), the date table, four relationships, hidden columns, sort, formats, display folders, with the reason for each |
| [`03-measures.dax`](03-measures.dax) | The `_Measures` table and 14 measures, grouped by page |
| [`04-pages.md`](04-pages.md) | Three pages, 27 visuals: type, fields, position and size, title, sort, colours, settings, slicer sync |
| [`05-theme.json`](05-theme.json) | The shared theme of every project report: **View > Themes > Browse for themes**, pick this file |
| [`06-checks.md`](06-checks.md) | The numbers every card and chart must show, each with its SQL |
| [`07-interactions.md`](07-interactions.md) | Which visual filters which, per page; visual filters; why no drill-through, bookmarks or tooltip pages |
| [`08-build-checklist.md`](08-build-checklist.md) | The build, step by step |

The theme uses the portfolio site's colours (navy, blue, soft grey page), the same in all the project
reports. The pages name colours by theme slot (theme colour 1 is the blue, danger is the theme's
"bad" colour), never by hex code.

After a new day of data, run the DAG (or `python pipeline.py`) and press **Refresh** in Power BI.

When the report is built:

- Save it as `powerbi/stock-reorder.pbix`.
- Export one image per page to `powerbi/screenshots/` (`1-reorder-list.png`,
  `2-stock-vs-reorder-point.png`, `3-slow-stock.png`; days in step 32 of the checklist).
- Put the three images in the main README's "The Power BI report" section.
