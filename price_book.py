"""PriceBook: the manager class.

It keeps every PriceRecord in a list, stops duplicates with two sets,
and saves and loads the records in a JSON file.
"""

import json
import os
import shutil

from price_record import ITEMS, MARKETS, PriceRecord
from validation import check_record

# The data files live in the "data" folder next to this .py file
DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATA_FILE = os.path.join(DATA_FOLDER, "prices.json")
REPORT_FILE = os.path.join(DATA_FOLDER, "price_report.txt")


class PriceBook:
    def __init__(self, file_name=DATA_FILE):
        self.file_name = file_name
        self.records = []  # list of PriceRecord objects
        self.used_ids = set()  # set of IDs in use, so no ID appears twice
        self.entry_keys = set()  # set of (date, item, market) tuples already recorded
        self.load_message = self.load()

    # ---------- add / find / search / update / delete ----------

    def remember(self, record):
        """Add a record to the list and to both sets."""
        self.records.append(record)
        self.used_ids.add(record.record_id)
        self.entry_keys.add(record.key())

    def add_record(self, date_text, item, market, price_text):
        date, item, market, price = check_record(date_text, item, market, price_text)
        if (date, item, market) in self.entry_keys:
            raise ValueError(
                f"{item} at {market} on {date} is already recorded. Use Update to change it."
            )
        new_id = max(self.used_ids, default=0) + 1
        record = PriceRecord(new_id, date, item, market, price)
        self.remember(record)
        return record

    def find_record(self, record_id):
        """Return the record with this ID, or None if there isn't one."""
        for record in self.records:
            if record.record_id == record_id:
                return record
        return None

    def search(self, item="", market=""):
        """Records for this item and/or market. An empty value means "any"."""
        results = []
        for record in self.records:
            if item and record.item != item:
                continue
            if market and record.market != market:
                continue
            results.append(record)
        return results

    def records_for(self, item):
        return self.search(item=item)

    def newest_first(self, records):
        return sorted(records, key=PriceRecord.sort_key, reverse=True)

    def update_record(self, record_id, date_text, item, market, price_text):
        record = self.find_record(record_id)
        if record is None:
            raise ValueError(f"No record with ID {record_id}.")
        date, item, market, price = check_record(date_text, item, market, price_text)
        new_key = (date, item, market)
        if new_key != record.key() and new_key in self.entry_keys:
            raise ValueError(f"{item} at {market} on {date} is already recorded.")

        self.entry_keys.discard(record.key())  # forget the old key
        record.date, record.item, record.market, record.price = date, item, market, price
        self.entry_keys.add(record.key())
        return record

    def delete_record(self, record_id):
        record = self.find_record(record_id)
        if record is None:
            raise ValueError(f"No record with ID {record_id}.")
        self.records.remove(record)
        self.used_ids.discard(record_id)
        self.entry_keys.discard(record.key())

    # ---------- file handling ----------

    def save(self):
        """Write every record to the JSON file. Returns True if it worked."""
        data = [record.to_dict() for record in self.records]
        try:
            os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
            with open(self.file_name, "w") as file:
                json.dump(data, file, indent=2)
            return True
        except OSError:
            return False

    def load(self):
        """Read records from the JSON file. Returns a message for the user."""
        try:
            with open(self.file_name) as file:
                data = json.load(file)
        except FileNotFoundError:
            return "No saved prices yet - starting with an empty list."
        except json.JSONDecodeError:
            return self.keep_damaged_file()

        skipped = 0
        for entry in data:
            try:
                record = PriceRecord.from_dict(entry)
            except (KeyError, ValueError, TypeError):
                skipped += 1  # a broken record: skip it instead of crashing
                continue
            if not self.is_usable(record):
                skipped += 1  # unknown item or market, bad price, or a duplicate
                continue
            self.remember(record)

        message = f"Loaded {len(self.records)} price records."
        if skipped:
            message += f" Skipped {skipped} broken or duplicate records."
        return message

    def is_usable(self, record):
        """Check a record read from the file before trusting it."""
        if record.item not in ITEMS or record.market not in MARKETS:
            return False
        if record.price <= 0:
            return False
        is_duplicate = record.record_id in self.used_ids or record.key() in self.entry_keys
        return not is_duplicate

    def keep_damaged_file(self):
        """Copy a damaged data file aside, so the next save can't overwrite it."""
        backup = self.file_name.replace(".json", "_damaged.json")
        try:
            shutil.copy(self.file_name, backup)
            note = f" A copy was saved as {os.path.basename(backup)}."
        except OSError:
            note = ""
        return "The data file was damaged, so the app started with an empty list." + note

    def export_report(self, lines, file_name=REPORT_FILE):
        """Write a text report, one line per item. Returns True if it worked."""
        try:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write("\n".join(lines) + "\n")
            return True
        except OSError:
            return False
