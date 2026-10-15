# BazarDor (বাজার দর)

**Daily Market Price Tracker for Households**
CSC 4162 Programming in Python, Fall 2026–27, mid-term group project

BazarDor helps families in Dhaka record what essentials cost at nearby markets, see
where each item is cheapest right now, and know whether this week's price is a good
deal compared with the usual price.

## Team

| Student ID | Name | Main part |
|------------|------|-----------|
| 21-44625-1 | Minhazul Abedin | `main.py` (interface), integration |
| | | `price_record.py`, `validation.py`, sample data |
| | | `price_book.py` (records manager, files) |
| | | `analysis.py` (NumPy calculations) |

## How to run

You need Python 3.12 or newer. Tkinter comes with Python on Windows and macOS.

```bash
pip install -r requirements.txt
python main.py
```

`main.py` is the file to run.

## Features

- **Prices tab:** add, update and delete price records; filter by item and market.
- **Analysis tab:** for one item, the average, median, lowest and highest price now,
  the cheapest market, the change since the first record, how stable prices are, a buy
  signal, and a bar chart of the latest price at each market.
- **Price Board tab:** every item on one screen with its buy signal; export a `.txt` report.
- **Shopping List tab:** estimate the cost of a list at the cheapest markets and at
  average prices, and see the saving.
- Records are saved to `data/prices.json` after every change and loaded at start.

## Files

| File | What it contains |
|------|------------------|
| `main.py` | `BazarDorApp` class: the Tkinter window and its four tabs |
| `price_record.py` | `PriceRecord` class, the `ITEMS` dictionary and the `MARKETS` tuple |
| `validation.py` | Input checks for date, item, market, price and quantity |
| `price_book.py` | `PriceBook` class: add, find, search, update, delete, save, load |
| `analysis.py` | NumPy calculations: statistics, cheapest market, change, buy signal, estimate |
| `data/prices.json` | 70 sample price records |

## Sample data

`data/prices.json` holds 70 **sample** records for 8 items at 5 Dhaka markets: every
item at every market on 15 October 2026, plus three earlier weeks for five items. The
prices are realistic examples for demonstration, not official prices.
