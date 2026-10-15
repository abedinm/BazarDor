"""Input checks.

Each check returns a clean value, or raises ValueError with a message the
user can understand. The interface shows that message in a dialog.
"""

from datetime import date, datetime

from price_record import ITEMS, MARKETS

MAX_PRICE = 2000  # Taka per unit; anything higher is almost certainly a typing mistake
MAX_QUANTITY = 100  # for the shopping list
EARLIEST_YEAR = 2020


def to_number(text):
    """Turn text into a number. Returns None if it isn't one."""
    try:
        return float(text)
    except ValueError:
        return None


def to_date(text):
    """Turn text written as YYYY-MM-DD into a date. Returns None if it isn't a real date."""
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def check_date(text):
    text = text.strip()
    day = to_date(text)
    if day is None:
        raise ValueError("Date must be a real date written like 2026-10-15.")
    if day > date.today():
        raise ValueError("Date can't be in the future.")
    if day.year < EARLIEST_YEAR:
        raise ValueError(f"Date must be in {EARLIEST_YEAR} or later.")
    return text


def check_item(item):
    if item not in ITEMS:
        raise ValueError("Please choose an item from the list.")
    return item


def check_market(market):
    if market not in MARKETS:
        raise ValueError("Please choose a market from the list.")
    return market


def check_price(price_text):
    price = to_number(price_text.strip())
    if price is None:
        raise ValueError("Price must be a number, like 85 or 92.50.")
    if not 0 < price <= MAX_PRICE:
        raise ValueError(f"Price must be more than 0 and at most {MAX_PRICE:,} Tk.")
    return round(price, 2)


def check_quantity(quantity_text):
    quantity = to_number(quantity_text.strip())
    if quantity is None:
        raise ValueError("Quantity must be a number, like 2 or 0.5.")
    if not 0 < quantity <= MAX_QUANTITY:
        raise ValueError(f"Quantity must be more than 0 and at most {MAX_QUANTITY}.")
    return quantity


def check_record(date_text, item, market, price_text):
    """Check every field of a price record. Returns a tuple (date, item, market, price)."""
    return (
        check_date(date_text),
        check_item(item),
        check_market(market),
        check_price(price_text),
    )
