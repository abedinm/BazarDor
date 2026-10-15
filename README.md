# BazarDor (বাজার দর)

**Daily Market Price Tracker for Households**
CSC 4162 Programming in Python, Fall 2026–27, mid-term group project

BazarDor helps families in Dhaka at the two moments that matter:

- **At the stall:** is the price the seller asks fair, and where is it cheaper?
- **At home:** what will this month's bazar cost, does it fit the budget, and which
  market sells the whole list for the least?

## Team

| Student ID | Name | Main part |
|------------|------|-----------|
| 21-44625-1 | Minhazul Abedin | `main.py`, `ui.py`, Prices tab, integration |
| | | `price_record.py`, `validation.py`, Fair Price Check tab, sample data |
| | | `price_book.py`, Price Board tab |
| | | `analysis.py`, Analysis tab |
| | | Shopping List tab, report |

## How to run

You need Python 3.12 or newer. Tkinter comes with Python on Windows and macOS.

```bash
pip install -r requirements.txt
python main.py
```

`main.py` is the file to run.

## Features

- **Prices:** add, update and delete price records; filter by item and market.
- **Fair Price Check:** type the price a seller asks and get *Fair price*, *A little
  high* or *Overpriced*, compared with what markets charge now, plus the cheapest
  market and a price ruler. Save the price to your records in one click.
- **Analysis:** for one item, the average, median, lowest and highest price now, the
  cheapest market, the change since the first record, price stability, a buy signal
  and a bar chart of the latest price at each market.
- **Price Board:** every item on one screen with its buy signal, price alerts for items
  up more than 10%, today's good buys, and a `.txt` report export.
- **Shopping List:** build a list or load a typical monthly basket for a family of any
  size; see the cost at each item's cheapest market, the single cheapest market for the
  whole list, and whether it fits your monthly budget.
- Records are saved to `data/prices.json` after every change and loaded at start.

## Files

| File | What it contains |
|------|------------------|
| `main.py` | `BazarDorApp`: the window, header and message bar; puts the five tabs together |
| `ui.py` | Colours, fonts and small helpers for buttons, tables and cards |
| `tab_prices.py` | `PricesTab`: add, update, delete and search records |
| `tab_fair_price.py` | `FairPriceTab`: the fair-price verdict and price ruler |
| `tab_analysis.py` | `AnalysisTab`: statistics cards and the market bar chart |
| `tab_board.py` | `BoardTab`: every item at a glance, alerts, report export |
| `tab_shopping.py` | `ShoppingTab`: shopping list, family basket, budget, best market |
| `price_record.py` | `PriceRecord` class, the `ITEMS` dictionary and the `MARKETS` tuple |
| `validation.py` | Input checks for date, item, market, price, quantity, family size and budget |
| `price_book.py` | `PriceBook`: add, find, search, update, delete, save, load |
| `analysis.py` | NumPy calculations: statistics, cheapest market, change, buy signal, fair price, estimates |
| `data/prices.json` | 70 sample price records |

## Sample data and estimates

`data/prices.json` holds 70 **sample** records for 8 items at 5 Dhaka markets: every
item at every market on 15 October 2026, plus three earlier weeks for five items. The
prices are realistic examples for demonstration, not official prices.

The monthly family basket uses rough per-person amounts (`MONTHLY_PER_PERSON` in
`analysis.py`). Adjust them to match your family.
