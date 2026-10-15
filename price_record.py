"""PriceRecord: the data model class.

One PriceRecord = the price of one item, at one market, on one day.
"""

# Dictionary: item name -> the unit it is sold in
ITEMS = {
    "Rice (Miniket)": "kg",
    "Rice (Coarse)": "kg",
    "Red Lentil (Masoor)": "kg",
    "Onion (Local)": "kg",
    "Potato": "kg",
    "Soybean Oil (Bottled)": "litre",
    "Egg (Farm)": "dozen",
    "Sugar": "kg",
}

# Tuple: the markets (they never change while the app runs)
MARKETS = (
    "Karwan Bazar",
    "Mohammadpur Krishi Market",
    "Mirpur 1 Kacha Bazar",
    "Neighbourhood Shop",
    "Supershop",
)


class PriceRecord:
    def __init__(self, record_id, date, item, market, price):
        self.record_id = record_id  # int, unique for every record
        self.date = date  # text like "2026-10-15"
        self.item = item  # one of the ITEMS keys
        self.market = market  # one of MARKETS
        self.price = price  # float, Taka per unit

    def unit(self):
        """The unit this item is sold in, for example "kg"."""
        return ITEMS.get(self.item, "unit")

    def key(self):
        """Tuple (date, item, market). No two records may have the same key."""
        return (self.date, self.item, self.market)

    def sort_key(self):
        """Used to sort records by date, then by ID."""
        return (self.date, self.record_id)

    def to_dict(self):
        """Turn the object into a dictionary so it can be saved in the JSON file."""
        return {
            "id": self.record_id,
            "date": self.date,
            "item": self.item,
            "market": self.market,
            "price": self.price,
        }

    @staticmethod
    def from_dict(data):
        """Build a PriceRecord from a dictionary read from the JSON file."""
        return PriceRecord(
            int(data["id"]),
            data["date"],
            data["item"],
            data["market"],
            float(data["price"]),
        )

    def __str__(self):
        price = f"{self.price:.2f} Tk/{self.unit()}"
        return f"#{self.record_id} {self.date} {self.item} at {self.market}: {price}"
