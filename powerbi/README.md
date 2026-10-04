# The Power BI report: build it step by step

The report reads the warehouse (`stock_rule` and `item`) and answers three questions:

1. **Reorder list:** on a given morning, what must be reordered, how much, and what is already empty?
2. **Stock vs reorder point:** for one item in one store, how did its stock move against the reorder point and the safety stock, and when was its shelf empty?
3. **Slow stock:** how much stock value sits in items with more than 30 days of cover, and in which items?

Every number on it must match the notebook (`analysis/analysis.ipynb`, section 7), listed in
`06-checks.md`.

## Before you start

- The warehouse is up and loaded: `docker compose up -d`, then `python pipeline.py` (or trigger the DAG).
- Power BI Desktop, a recent version (its PostgreSQL connector is built in).

## Follow the files in this order

| Step | File | What you do |
|---|---|---|
| 1 | `05-theme.json` | View > Themes > Browse for themes > pick this file |
| 2 | `01-power-query.md` | Paste the two queries into Power Query, close and apply |
| 3 | `02-model.md` | Add the three small tables, the relationships, sort orders, hidden columns, formats |
| 4 | `03-measures.dax` | Create each measure in its display folder |
| 5 | `04-pages.md` | Build the three pages, visual by visual |
| 6 | `06-checks.md` | Pick the days listed and check every card |
| 7 | `screenshots/` | Save one image per page (`1-reorder-list.png`, `2-stock-vs-reorder-point.png`, `3-slow-stock.png`) and commit them with the `.pbix` |
