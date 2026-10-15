"""Prices tab: add, update, delete and search price records."""

from datetime import date
from tkinter import messagebox, ttk

from price_record import ITEMS, MARKETS
from ui import ALL, FONT, fill_table, make_button, make_table

# Dictionary: table column -> width in pixels
COLUMNS = {
    "ID": 50,
    "Date": 100,
    "Item": 190,
    "Market": 210,
    "Price (Tk)": 100,
    "Unit": 70,
}


class PricesTab:
    def __init__(self, app, notebook):
        self.app = app  # the main BazarDorApp: gives us app.book and app.say()
        self.selected_id = None  # ID of the row clicked in the table
        self.frame = ttk.Frame(notebook, padding=14)
        notebook.add(self.frame, text="Prices")
        self.build_form()
        self.build_buttons()
        self.build_filters()
        self.table = make_table(self.frame, COLUMNS, height=11)
        self.table.bind("<<TreeviewSelect>>", self.on_row_click)
        self.clear_form()

    # ---------- building the tab ----------

    def build_form(self):
        form = ttk.Frame(self.frame, style="Card.TFrame", padding=12)
        form.pack(fill="x")
        titles = ("Date (YYYY-MM-DD)", "Item", "Market", "Price (Tk)")
        for column, text in enumerate(titles):
            ttk.Label(form, text=text, style="CardBold.TLabel").grid(
                row=0, column=column, sticky="w", padx=6
            )
        self.date_entry = ttk.Entry(form, width=13, font=(FONT, 12))
        self.item_box = ttk.Combobox(
            form, values=tuple(ITEMS), state="readonly", width=22, font=(FONT, 12)
        )
        self.market_box = ttk.Combobox(
            form, values=MARKETS, state="readonly", width=25, font=(FONT, 12)
        )
        self.price_entry = ttk.Entry(form, width=10, font=(FONT, 12))
        inputs = (self.date_entry, self.item_box, self.market_box, self.price_entry)
        for column, widget in enumerate(inputs):
            widget.grid(row=1, column=column, padx=6, pady=(4, 0), sticky="w")
        self.unit_label = ttk.Label(form, text="", style="Card.TLabel")
        self.unit_label.grid(row=1, column=4, sticky="w")

        self.item_box.bind("<<ComboboxSelected>>", self.update_unit_label)
        self.price_entry.bind("<Return>", self.add_record)  # Enter adds the record

    def build_buttons(self):
        buttons = ttk.Frame(self.frame, padding=(0, 12, 0, 0))
        buttons.pack(fill="x")
        # Tuple of (button text, colour, function to run when clicked)
        actions = (
            ("+ Add", "Green", self.add_record),
            ("Update", "Turmeric", self.update_record),
            ("Delete", "Red", self.delete_record),
            ("Clear form", "Grey", self.clear_form),
        )
        for text, color, command in actions:
            make_button(buttons, text, color, command).pack(side="left", padx=(0, 8))

    def build_filters(self):
        filters = ttk.Frame(self.frame, padding=(0, 12, 0, 0))
        filters.pack(fill="x")
        ttk.Label(filters, text="Show item").pack(side="left")
        self.filter_item = ttk.Combobox(
            filters, values=(ALL,) + tuple(ITEMS), state="readonly", width=22, font=(FONT, 12)
        )
        self.filter_item.pack(side="left", padx=(6, 14))
        ttk.Label(filters, text="at market").pack(side="left")
        self.filter_market = ttk.Combobox(
            filters, values=(ALL,) + MARKETS, state="readonly", width=25, font=(FONT, 12)
        )
        self.filter_market.pack(side="left", padx=(6, 14))
        make_button(filters, "Search", "Blue", self.search_records).pack(side="left", padx=4)
        make_button(filters, "Show all", "Grey", self.show_all).pack(side="left", padx=4)

    # ---------- showing records ----------

    def refresh(self):
        self.filter_item.set(ALL)
        self.filter_market.set(ALL)
        self.show_records(self.app.book.records)

    def show_records(self, records):
        rows = []
        for record in self.app.book.newest_first(records):
            rows.append(
                (
                    record.record_id,
                    record.date,
                    record.item,
                    record.market,
                    f"{record.price:,.2f}",
                    record.unit(),
                )
            )
        fill_table(self.table, rows)

    def update_unit_label(self, event=None):
        unit = ITEMS.get(self.item_box.get(), "")
        self.unit_label.config(text=f"Tk per {unit}")

    def clear_form(self):
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date.today().isoformat())
        self.item_box.set(tuple(ITEMS)[0])
        self.market_box.set(MARKETS[0])
        self.price_entry.delete(0, "end")
        self.selected_id = None
        self.update_unit_label()

    def on_row_click(self, event):
        selected = self.table.selection()
        if not selected:
            return
        record_id = int(self.table.item(selected[0], "values")[0])
        record = self.app.book.find_record(record_id)
        if record is None:
            return
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, record.date)
        self.item_box.set(record.item)
        self.market_box.set(record.market)
        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, f"{record.price:.2f}")
        self.update_unit_label()
        self.selected_id = record_id
        self.app.say(f"Selected record #{record_id}. Change it, then click Update or Delete.")

    # ---------- button actions ----------

    def add_record(self, event=None):
        try:
            record = self.app.book.add_record(
                self.date_entry.get(),
                self.item_box.get(),
                self.market_box.get(),
                self.price_entry.get(),
            )
        except ValueError as error:
            messagebox.showerror("Please check", str(error))
            return
        self.app.save_and_refresh()
        self.price_entry.delete(0, "end")  # keep date, item and market for the next price
        self.app.new_tip()
        self.app.say(
            f"Added {record.item} at {record.market}: {record.price:,.2f} Tk/{record.unit()}."
        )

    def update_record(self):
        if self.selected_id is None:
            messagebox.showinfo("Pick a row", "Click a row in the table first.")
            return
        try:
            self.app.book.update_record(
                self.selected_id,
                self.date_entry.get(),
                self.item_box.get(),
                self.market_box.get(),
                self.price_entry.get(),
            )
        except ValueError as error:
            messagebox.showerror("Please check", str(error))
            return
        record_id = self.selected_id
        self.app.save_and_refresh()
        self.clear_form()
        self.app.say(f"Updated record #{record_id}.")

    def delete_record(self):
        if self.selected_id is None:
            messagebox.showinfo("Pick a row", "Click a row in the table first.")
            return
        record_id = self.selected_id
        if not messagebox.askyesno("Delete?", f"Delete record #{record_id}? This can't be undone."):
            return
        try:
            self.app.book.delete_record(record_id)
        except ValueError as error:
            messagebox.showerror("Not found", str(error))
            return
        self.app.save_and_refresh()
        self.clear_form()
        self.app.say(f"Deleted record #{record_id}.")

    def search_records(self):
        item = self.filter_item.get()
        market = self.filter_market.get()
        # "All" means "don't filter", which PriceBook.search expects as ""
        if item == ALL:
            item = ""
        if market == ALL:
            market = ""
        results = self.app.book.search(item, market)
        self.show_records(results)
        self.app.say(f"Found {len(results)} records. Click Show all to see everything again.")

    def show_all(self):
        self.refresh()
        self.app.say(f"Showing all {len(self.app.book.records)} records.")
