# Input files

The three files a client supplies, as CSV with a header row. Their names are the `inputs` keys in
`config/client.yaml`. Only the columns below are loaded; any other column is ignored. The files are
gitignored: client data never goes into the public repo. For the demo, `python data/demo/make_data.py`
writes all three here.

Before the warehouse is touched, `pipeline.py` checks each file and stops with one line:

```
missing input file data/input/item.csv (inputs.items in config/client.yaml)
data/input/stock.csv is missing column(s): on_order
Key (item)=(51) is not present in table "item".
1 store-item(s) with a missing day in the sales file
```

## Sales (`inputs.sales`)

One row per day, store and item: what was sold. Every day from a shelf's first row to its last must
be there (a day with no sale is a row with 0), because the forecast counts rows as days.

| Column | Type | Meaning |
|---|---|---|
| `date` | date, `YYYY-MM-DD` | the day |
| `store` | whole number | the store's number |
| `item` | whole number | the item's number, as in the items file |
| `units_sold` | whole number, 0 or more | units sold that day |

```
date,store,item,units_sold
2017-12-31,1,15,64
```

## Stock (`inputs.stock`)

One row per day, store and item, counted at closing, with a matching sales row.

| Column | Type | Meaning |
|---|---|---|
| `date`, `store`, `item` | as in the sales file | the shelf and the day |
| `units_received` | whole number, 0 or more | units delivered that morning |
| `on_hand` | whole number, 0 or more | units on the shelf at closing |
| `on_order` | whole number, 0 or more | units ordered and not yet delivered |

```
date,store,item,units_received,on_hand,on_order
2017-12-31,1,15,0,609,0
```

## Items (`inputs.items`)

One row per item. Every item in the sales and stock files must be here.

| Column | Type | Meaning |
|---|---|---|
| `item` | whole number | the item's number |
| `unit_cost` | decimal, above 0 | the cost of one unit, in `client.currency` |
| `lead_days` | whole number, above 0 | days the supplier takes to deliver after an order |

```
item,unit_cost,lead_days
15,29.54,4
```
