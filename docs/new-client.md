# New client

This repo is a GitHub template. A new client gets a **private** repo from it (Use this template >
Create a new repository > Private); client data never goes into this public repo. Everything that
changes per client is in three places: `config/client.yaml`, `.env`, and the files in `data/input/`.

It serves offering **12. Stock dashboard with reorder alerts**.

## Done in the template

What the client gets with no work. Hours are an estimate of building each part from scratch.

| Part | Estimate (hours) |
|---|---|
| Docker stack: PostgreSQL warehouse, Airflow with its own records database, one Compose file (`docker-compose.yml`) | 2 |
| Loader: each input file and its columns checked before the warehouse is touched, extra columns ignored, keys, checks and an item foreign key, no missing day, re-runs add nothing twice (`pipeline.py` `load`, `sql/01_tables.sql`) | 3 |
| Forecast and rules in SQL: moving-average demand and swing, safety stock from each item's lead time, reorder point on stock plus orders on the way, order quantity, days of cover, five statuses (`sql/02_forecast.sql`, `sql/03_rules.sql`) | 4 |
| Morning reorder email, saved as HTML and sent through Gmail (`pipeline.py` `alert`) | 1.5 |
| Airflow DAG: the client's schedule and time zone, one task per step, a retry (`dags/stock_reorder.py`) | 1.5 |
| Client settings: `config/client.yaml`, `config.py` (`load_config()`), `.env`, the Power BI theme written from the config (`theme.py`) | 2 |
| Analysis notebook: the backtest, best sellers, slow stock, three charts, the Power BI check numbers (`analysis/analysis.ipynb`) | 4 |
| Power BI build pack: 2 queries, the model, 14 measures, 3 pages with 27 visuals, interactions, checks, a 33-step checklist (`powerbi/`) | 8 |
| README with its diagrams, and the input file guide (`data/input/README.md`) | 3 |
| **Total** | **29** |

## Configure

Per client, file by file. Hours are an estimate.

| File | Key | Example | Estimate (hours) |
|---|---|---|---|
| `config/client.yaml` | `client.name`, `client.currency`, `report.title`, `report.colours` | `Delta Corner Shops`, `EGP`, `"#0F766E"` | 0.5 |
| `.env` | `DB_PASSWORD`, and `GMAIL_USER`, `GMAIL_APP_PASSWORD` for the email | a new password | 0.25 |
| `data/input/` sales and stock | `inputs.sales`, `inputs.stock` | the client's daily exports turned into one row per day, store and item, with `on_order` | 4 |
| `data/input/` items | `inputs.items` | `501,4.00,2`: unit cost and each supplier's delivery days | 1 |
| `config/client.yaml` | `rules.*`, `schedule.cron`, `schedule.timezone`, `alert.mail_to`, `report.best_sellers`, `report.check_days`, `report.check_shelf` | `forecast_days: 5`, `"30 6 * * *"`, `Asia/Riyadh` | 0.5 |
| Run the DAG, `theme.py` and the notebook; fix what the checks report | | | 1 |
| Power BI: build from `powerbi/08-build-checklist.md` with the client's server in both queries; copy the notebook's section 7 into `powerbi/06-checks.md` | `warehouse.*` | `127.0.0.1:5448` | 2 |
| **Total** | | | **9.25** |

## Custom

Typical per-client work the template does not do. Hours are an estimate.

| Custom work | Estimate (hours) |
|---|---|
| A department or category view: a category column on items, stock value by category, a category slicer (the listing promises "stock value tied up by category") | 3 |
| Read the client's real stock system or branch Excel sheets in place of CSV exports | 3 |
| Round order quantities to the supplier's case size or minimum order | 2 |
| **Total** | **8** |

## Share already done (estimate)

Template ÷ (template + configure + custom) = 29 ÷ (29 + 9.25 + 8) = 29 ÷ 46.25 = **63%** (62.7%), an
estimate. No prices.

## Steps

1. Use this template to create the client's private repo, and clone it.
2. `cp .env.example .env` and set `DB_PASSWORD` (and the Gmail lines for a real email).
3. Edit `config/client.yaml`. If you change `warehouse.port`, `warehouse.user` or `warehouse.database`,
   change the same values in `docker-compose.yml`.
4. Put the client's three files in `data/input/` as `data/input/README.md` describes.
5. `docker compose up -d`, then Trigger `stock_reorder` in Airflow (or `python pipeline.py`).
6. `python theme.py`, then run `analysis/analysis.ipynb` (0 errors), and copy its section 7 into
   `powerbi/06-checks.md`.
7. Build the Power BI report from `powerbi/08-build-checklist.md`.

## Second-client drill (2026-10-05)

The acceptance test of the template: a fresh clone, a made-up second client, a run from scratch
through the Airflow DAG, every number checked by hand.

**Client B (drill):** "Delta Corner Shops", currency `EGP`, teal colours (`#0F766E` main, page
`#F0FDFA`), title "Delta Corner stock", schedule `30 6 * * *` in `Asia/Riyadh`, warehouse on port
5448. Rules: `forecast_days: 5`, `service_z: 2.05`, `cover_days_after_delivery: 3`,
`overstock_days: 10`, `warning_window_days: 6`. Input: other file names (`daily_sales.csv`,
`shelf_counts.csv`, `products.csv`), an extra column in each, stores 101 and 102, items 501 to 505
with lead times 2, 3, 5, 2 and 6 days, 10 days of history (100 + 100 + 5 rows). Planted: a stock-out
flagged too late, one flagged in time, a dead item, overstock, a reorder, an order on the way that
keeps a shelf off the list, and uneven sales to test the safety stock.

| What | Demo | Client B (drill) |
|---|---|---|
| Rows loaded | 913,000 sales, 913,000 stock, 50 items | 100 sales, 100 stock, 5 items |
| DAG run | green | green; run time 6:30am Riyadh (`scheduled__2026-10-05T03:30:00+00:00`) |
| Stock-outs, flagged, in time | 4,052, 4,052, 1,643 (41%) | 2, 2, 1 (50%): store 101 item 501 flagged day 7, empty day 9, 2 days < 2 + 1, too late; store 102 item 501 flagged day 4, empty day 8, 4 days ≥ 3, in time |
| Best sellers, median warning | 10 items, 4 days | 501 (150 units) and 504 (108), (2 + 4) ÷ 2 = 3 days |
| Last day: shelves to reorder, units | 31 Dec 2017: 0, 0 | 10 Mar 2025: 3, 86 = 53 + 23 + 10 |
| Safety stock check | | store 101 item 504: sales 8, 6, 10, 8, 6, mean 7.6, sd √(11.2 ÷ 4) = 1.673, safety 2.05 × 1.673 × √2 = 4.85, reorder point 7.6 × 2 + 4.85 = 20.05 |
| Order on the way | | store 101 item 505: 20 on hand + 30 on order = 50 > reorder point 30, so OK, not on the list |
| Stock value, slow share | 7,707,022 USD, 36.9% | 2,820 EGP, 1,750 ÷ 2,820 = 62.1% |
| Second check day | 16 Jul 2017: 111 shelves, 98,020 units | 7 Mar 2025: 3 shelves, 78 = 30 + 38 + 10 units, 2,920 EGP, 59.9% |
| Statuses, last day | OK 343, Overstock 157 | Out of stock 2, Reorder 1, OK 3, Overstock 3, Dead 1 |
| Email subject | "Sample stores: reorder today, 0 items (31 Dec 2017)" | "Delta Corner Shops: reorder today, 3 items (10 Mar 2025)" |
| Power BI theme | "Stock reorder dashboard", `#2563EB` | "Delta Corner stock", `#0F766E`, page `#F0FDFA` |
| Notebook | 0 errors | 0 errors; chart titles name Delta Corner Shops, values in EGP |

Every Client B number matches a hand calculation. The first hand figure for units to order (65)
was mine and wrong: it left out the swing in the last five days of the two emptying shelves;
redone by hand, 53 + 23 + 10 = 86, as the rules give.

**Clear failures**, one line each, run on the Client B copy:

```
config/client.yaml is missing rules.overstock_days
config/client.yaml is not valid YAML near line 33 (quote a value with # or :)
.env is missing DB_PASSWORD (copy .env.example to .env)
missing input file data/input/products.csv (inputs.items in config/client.yaml)
data/input/shelf_counts.csv is missing column(s): on_order
Key (item)=(506) is not present in table "item".
1 store-item(s) with a missing day in the sales file
```

(The drill run printed the last one as "1 store-items have a missing day in the sales file"; it was reworded after.)

**Nothing hard-coded:** this search over the code (`*.py` outside `data/demo/`, `dags/`, `sql/*.sql`,
`powerbi/03-measures.dax`) and the notebook's source cells finds nothing:

```
Sample stores|USD|#[0-9A-Fa-f]{6}|5447|sales\.csv|stock\.csv|item\.csv|2017|1\.65|Africa/Cairo|0 7 \* \* \*|Stock reorder dashboard|lead_days = 4|LEAD_DAYS
```

The README, the diagrams in `docs/`, `powerbi/06-checks.md` and the Power BI build guide describe
the demo run, so they keep its values on purpose; `data/demo/` is demo-only tooling.

**Nothing broke:** after the drill, `python pipeline.py` and the notebook on the demo data gave the
same totals (0 new rows on the rerun).

## Gaps

- `docker-compose.yml` repeats `warehouse.port`, `warehouse.user` and `warehouse.database`: Compose
  cannot read `client.yaml`, so its comment says to change both together.
- The Power BI build guide (`powerbi/01-power-query.md`) has the demo's server in its two queries;
  for a client, type `warehouse.host:warehouse.port` there.
- Store and item are whole numbers. A client with text codes (`CAI-01`, a SKU string) needs the three
  tables' types changed or a mapping file: custom work today.
- No delivery-day key: the rules need only each item's lead time. The weekly delivery rhythm exists
  only in the demo's generated history (`data/demo/make_data.py`).
- The forecast is a moving average with no season; a client whose sales swing by season needs
  custom work.
- Right after `docker compose up -d`, the first scheduled run can fail while Airflow's API server is
  still starting; the DAG's one retry, two minutes later, covers it.
- The Power BI report itself (a `.pbip` project) is not in the template yet: the pack is a manual
  build.
