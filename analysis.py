"""Price calculations.

NumPy does the arithmetic on lists of prices. Plain Python decides what the
numbers mean (cheapest market, buy signal, how stable a price is).
"""

from datetime import date

import numpy as np

from price_record import ITEMS, MARKETS

GOOD_DEAL_PERCENT = 95  # this week's price at or below 95% of the usual price
NORMAL_LIMIT_PERCENT = 105  # up to 105% still counts as normal
STABLE_PERCENT = 5  # spread under 5% of the average price = stable
MODERATE_PERCENT = 15  # spread under 15% = moderate, above that = volatile
FAIR_LIMIT_PERCENT = 105  # a seller asking up to 5% above today's average is fair
HIGH_LIMIT_PERCENT = 115  # up to 15% above is "a little high"; more is overpriced
ALERT_PERCENT = 10  # items that rose more than 10% appear in the price alert

# Dictionary: item -> rough amount one person uses in a month.
# A starting point for the family basket; change it to match your family.
MONTHLY_PER_PERSON = {
    "Rice (Coarse)": 11,
    "Red Lentil (Masoor)": 0.5,
    "Onion (Local)": 1,
    "Potato": 2,
    "Soybean Oil (Bottled)": 1,
    "Egg (Farm)": 0.75,
    "Sugar": 0.5,
}


def price_stats(prices):
    """Average, median, lowest, highest and spread of a list of prices."""
    values = np.array(prices)
    return {
        "average": float(np.mean(values)),
        "median": float(np.median(values)),
        "lowest": float(np.min(values)),
        "highest": float(np.max(values)),
        "spread": float(np.std(values)),
    }


def latest_price_by_market(records):
    """Dictionary: market -> the newest price we know at that market."""
    newest = {}  # market -> newest record seen so far
    for record in records:
        known = newest.get(record.market)
        # Dates are written YYYY-MM-DD, so comparing the text compares the dates
        if known is None or record.date > known.date:
            newest[record.market] = record

    prices = {}
    for market, record in newest.items():
        prices[market] = record.price
    return prices


def average_by_date(records):
    """Dictionary: date -> average price on that date."""
    prices_by_date = {}
    for record in records:
        if record.date not in prices_by_date:
            prices_by_date[record.date] = []
        prices_by_date[record.date].append(record.price)

    averages = {}
    for day, prices in prices_by_date.items():
        averages[day] = float(np.mean(prices))
    return averages


def cheapest_market(prices):
    """Tuple (market, price) with the lowest price."""
    best_market = None
    best_price = None
    for market, price in prices.items():
        if best_price is None or price < best_price:
            best_market = market
            best_price = price
    return best_market, best_price


def price_change_percent(records):
    """Change from the first date's average price to the latest date's.

    Returns None when there is only one date, because there is nothing to compare.
    """
    averages = average_by_date(records)
    if len(averages) < 2:
        return None
    dates = sorted(averages)
    first = averages[dates[0]]
    latest = averages[dates[-1]]
    return (latest - first) / first * 100


def buy_signal(current_average, usual_average):
    """Compare this week's price with the usual price for the item."""
    percent = current_average / usual_average * 100
    if percent <= GOOD_DEAL_PERCENT:
        return "Good time to buy"
    elif percent <= NORMAL_LIMIT_PERCENT:
        return "Normal price"
    else:
        return "Expensive now"


def stability(spread, average):
    """Describe how much prices differ between markets."""
    percent = spread / average * 100
    if percent < STABLE_PERCENT:
        return "Stable"
    elif percent < MODERATE_PERCENT:
        return "Moderate"
    else:
        return "Volatile"


def analyse_item(records):
    """Everything the Analysis tab shows for one item. None if there are no records."""
    if not records:
        return None

    current_prices = latest_price_by_market(records)
    stats = price_stats(list(current_prices.values()))
    usual_average = float(np.mean([record.price for record in records]))
    market, price = cheapest_market(current_prices)

    return {
        "current_prices": current_prices,
        "stats": stats,
        "usual_average": usual_average,
        "cheapest_market": market,
        "cheapest_price": price,
        "change_percent": price_change_percent(records),
        "percent_of_usual": stats["average"] / usual_average * 100,
        "signal": buy_signal(stats["average"], usual_average),
        "stability": stability(stats["spread"], stats["average"]),
        "record_count": len(records),
    }


def item_overview(book):
    """One row per item that has prices: the data for the Price Board tab."""
    rows = []
    for item, unit in ITEMS.items():
        result = analyse_item(book.records_for(item))
        if result is None:
            continue
        rows.append(
            {
                "item": item,
                "unit": unit,
                "average": result["stats"]["average"],
                "cheapest_market": result["cheapest_market"],
                "cheapest_price": result["cheapest_price"],
                "change_percent": result["change_percent"],
                "signal": result["signal"],
            }
        )
    return rows


def shopping_estimate(book, shopping_list):
    """Cost of a shopping list at the cheapest markets vs at average prices.

    shopping_list is a dictionary: item -> quantity.
    """
    lines = []
    missing = []  # items we have no prices for
    quantities = []
    cheapest_prices = []
    average_prices = []

    for item, quantity in shopping_list.items():
        current_prices = latest_price_by_market(book.records_for(item))
        if not current_prices:
            missing.append(item)
            continue
        market, low_price = cheapest_market(current_prices)
        average_price = float(np.mean(list(current_prices.values())))
        quantities.append(quantity)
        cheapest_prices.append(low_price)
        average_prices.append(average_price)
        lines.append(
            {
                "item": item,
                "quantity": quantity,
                "market": market,
                "cheapest_cost": quantity * low_price,
                "average_cost": quantity * average_price,
            }
        )

    # NumPy multiplies the lists element by element, then adds the results
    total_cheapest = float(np.sum(np.array(quantities) * np.array(cheapest_prices)))
    total_average = float(np.sum(np.array(quantities) * np.array(average_prices)))
    return {
        "lines": lines,
        "missing": missing,
        "total_cheapest": total_cheapest,
        "total_average": total_average,
        "saving": total_average - total_cheapest,
    }


def change_text(change_percent):
    """Turn a change like 18.75 into text like "up 18.8%"."""
    if change_percent is None:
        return "not enough history"
    if change_percent > 0.5:
        return f"up {change_percent:.1f}%"
    elif change_percent < -0.5:
        return f"down {abs(change_percent):.1f}%"
    else:
        return "no change"


def report_lines(book):
    """The text for the exported price report."""
    lines = [
        "BazarDor price report",
        f"Generated on {date.today().isoformat()} from {len(book.records)} price records",
        "",
    ]
    for row in item_overview(book):
        lines.append(
            f"{row['item']:<24} average {row['average']:8.2f} Tk/{row['unit']:<6}"
            f" cheapest {row['cheapest_price']:8.2f} at {row['cheapest_market']:<26}"
            f" {change_text(row['change_percent']):<20} {row['signal']}"
        )
    return lines


# ---------- features for everyday shoppers ----------


def fair_price_check(records, asked_price):
    """Compare the price a seller asks with what markets charge now.

    Returns a dictionary with the verdict, or None if the item has no records.
    """
    if not records:
        return None
    current_prices = latest_price_by_market(records)
    stats = price_stats(list(current_prices.values()))
    market, cheapest = cheapest_market(current_prices)
    percent = asked_price / stats["average"] * 100

    if percent <= FAIR_LIMIT_PERCENT:
        verdict = "Fair price"
    elif percent <= HIGH_LIMIT_PERCENT:
        verdict = "A little high"
    else:
        verdict = "Overpriced"

    return {
        "verdict": verdict,
        "percent": percent,
        "average": stats["average"],
        "lowest": stats["lowest"],
        "highest": stats["highest"],
        "cheapest_market": market,
        "cheapest_price": cheapest,
        "record_count": len(records),
    }


def price_alerts(book):
    """List of (item, change percent) for items that rose more than ALERT_PERCENT."""
    alerts = []
    for row in item_overview(book):
        change = row["change_percent"]
        if change is not None and change > ALERT_PERCENT:
            alerts.append((row["item"], change))
    return alerts


def good_buys(book):
    """Items whose buy signal is "Good time to buy" right now."""
    items = []
    for row in item_overview(book):
        if row["signal"] == "Good time to buy":
            items.append(row["item"])
    return items


def cost_by_market(book, shopping_list):
    """Dictionary: market -> cost of the whole list if everything is bought there.

    A market is left out if it has no price for one of the items.
    """
    totals = {}
    for market in MARKETS:
        quantities = []
        prices = []
        has_every_item = True
        for item, quantity in shopping_list.items():
            current_prices = latest_price_by_market(book.records_for(item))
            if market not in current_prices:
                has_every_item = False
                break
            quantities.append(quantity)
            prices.append(current_prices[market])
        if has_every_item and prices:
            totals[market] = float(np.sum(np.array(quantities) * np.array(prices)))
    return totals


def family_basket(family_size):
    """Dictionary: item -> amount a family of this size uses in a month (to the nearest 0.5)."""
    basket = {}
    for item, amount in MONTHLY_PER_PERSON.items():
        basket[item] = round(amount * family_size * 2) / 2
    return basket
