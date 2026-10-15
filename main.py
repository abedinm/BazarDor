"""BazarDor - Daily Market Price Tracker (main file, Tkinter GUI).

Run:  python main.py
"""

import random
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

import analysis
from price_book import PriceBook
from price_record import ITEMS, MARKETS
from validation import check_quantity

# ---------- look and feel (all in one place, easy to change) ----------

FONT = "Helvetica"

# Dictionary: every colour the app uses
COLORS = {
    "background": "#F4F6F1",
    "card": "#FFFFFF",
    "primary": "#1E7A4C",  # banana-leaf green
    "primary_dark": "#17603C",
    "turmeric": "#A86A12",
    "text": "#1B2620",
    "muted": "#5B6A61",
    "stripe": "#F1F5EF",
    "bar": "#A9D3BA",
}

# Dictionary: button colour name -> (normal colour, colour when the mouse is over it)
BUTTON_COLORS = {
    "Green": ("#1E7A4C", "#17603C"),
    "Turmeric": ("#C98A1B", "#A86A12"),
    "Red": ("#B0442C", "#93361F"),
    "Blue": ("#2F6B8F", "#24546F"),
    "Grey": ("#7A8A80", "#66756C"),
}

# Dictionary: buy signal -> (table tag name, text colour)
SIGNAL_LOOK = {
    "Good time to buy": ("good", "#1E7A4C"),
    "Normal price": ("normal", "#A86A12"),
    "Expensive now": ("high", "#B0442C"),
}

# Tuple: friendly tips, one is picked at random
TIPS = (
    "Tip: wholesale markets like Karwan Bazar are often cheapest for rice and vegetables.",
    "Tip: check the Price Board before the weekly bazar.",
    "Tip: compare at least two markets before buying oil or lentils.",
    "Tip: record prices every week so the trends become meaningful.",
    "Tip: a short shopping list at the right market can save a day's bus fare.",
)

ALL = "All"  # filter choice meaning "don't filter"

# Dictionaries: table column -> width in pixels
PRICE_COLUMNS = {
    "ID": 50,
    "Date": 100,
    "Item": 190,
    "Market": 210,
    "Price (Tk)": 100,
    "Unit": 70,
}
BOARD_COLUMNS = {
    "Item": 180,
    "Average (Tk)": 100,
    "Unit": 60,
    "Cheapest at": 200,
    "Lowest (Tk)": 100,
    "Change": 150,
    "Signal": 140,
}
LIST_COLUMNS = {"Item": 220, "Quantity": 90, "Unit": 70}
ESTIMATE_COLUMNS = {
    "Item": 190,
    "Qty": 60,
    "Cheapest at": 210,
    "Cost there (Tk)": 130,
    "At average (Tk)": 130,
}


def setup_styles(window):
    """Tell ttk which colours and fonts to use for each kind of widget."""
    style = ttk.Style()
    style.theme_use("clam")  # a theme that lets us change colours, also on macOS

    style.configure("TFrame", background=COLORS["background"])
    style.configure("Card.TFrame", background=COLORS["card"])
    style.configure(
        "TLabel", background=COLORS["background"], foreground=COLORS["text"], font=(FONT, 12)
    )
    style.configure("Card.TLabel", background=COLORS["card"], foreground=COLORS["text"])
    style.configure("CardBold.TLabel", background=COLORS["card"], font=(FONT, 12, "bold"))
    style.configure("Muted.TLabel", foreground=COLORS["muted"], font=(FONT, 11))
    style.configure(
        "CardValue.TLabel",
        background=COLORS["card"],
        foreground=COLORS["primary"],
        font=(FONT, 19, "bold"),
    )
    style.configure(
        "CardCaption.TLabel", background=COLORS["card"], foreground=COLORS["muted"], font=(FONT, 11)
    )
    style.configure("Big.TLabel", font=(FONT, 14, "bold"))

    # One button style per colour, for example "Green.TButton"
    for name, (color, hover_color) in BUTTON_COLORS.items():
        style.configure(
            f"{name}.TButton",
            background=color,
            foreground="white",
            font=(FONT, 12, "bold"),
            padding=(12, 6),
            borderwidth=0,
        )
        style.map(f"{name}.TButton", background=[("active", hover_color)])

    style.configure("TNotebook", background=COLORS["background"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        font=(FONT, 12, "bold"),
        padding=(18, 8),
        background="#E2E9E0",
        foreground=COLORS["muted"],
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["card"])],
        foreground=[("selected", COLORS["primary"])],
    )

    style.configure("Treeview", rowheight=28, font=(FONT, 12), fieldbackground=COLORS["card"])
    style.configure(
        "Treeview.Heading",
        background=COLORS["primary"],
        foreground="white",
        font=(FONT, 12, "bold"),
        relief="flat",
    )
    style.map("Treeview.Heading", background=[("active", COLORS["primary_dark"])])
    style.map("Treeview", background=[("selected", COLORS["primary"])])

    # Font of the list that drops down from a combobox
    window.option_add("*TCombobox*Listbox.font", (FONT, 12))


class BazarDorApp:
    def __init__(self, window):
        self.window = window
        self.window.title("BazarDor - Daily Market Price Tracker")
        self.window.geometry("1080x800")
        self.window.minsize(1000, 740)
        self.window.configure(bg=COLORS["background"])
        setup_styles(window)

        self.book = PriceBook()
        self.selected_id = None  # ID of the row clicked in the Prices table
        self.shopping_list = {}  # dictionary: item -> quantity

        self.build_header()
        self.tabs = ttk.Notebook(self.window)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(12, 0))
        self.build_prices_tab()
        self.build_analysis_tab()
        self.build_board_tab()
        self.build_shopping_tab()
        self.build_message_bar()

        self.clear_form()
        self.refresh_everything()
        self.say(self.book.load_message)

    # ---------- small building blocks used by every tab ----------

    def make_button(self, parent, text, color, command):
        return ttk.Button(
            parent, text=text, style=f"{color}.TButton", command=command, cursor="hand2"
        )

    def make_table(self, parent, columns, height):
        """Create a table (Treeview) with a scrollbar. columns: dictionary name -> width."""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=(10, 0))

        table = ttk.Treeview(frame, columns=tuple(columns), show="headings", height=height)
        for name, width in columns.items():
            table.heading(name, text=name)
            table.column(name, width=width, anchor="w")
            if "Tk" in name or name in ("Qty", "Quantity"):
                table.column(name, anchor="e")  # numbers line up on the right

        table.tag_configure("even", background=COLORS["stripe"])
        table.tag_configure("odd", background=COLORS["card"])
        for tag, color in SIGNAL_LOOK.values():
            table.tag_configure(tag, foreground=color)

        table.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=table.yview)
        scrollbar.pack(side="right", fill="y")
        table.configure(yscrollcommand=scrollbar.set)
        return table

    def fill_table(self, table, rows, signals=None):
        """Replace a table's rows. signals (optional) gives each row's buy signal."""
        for row in table.get_children():
            table.delete(row)
        for number, values in enumerate(rows):
            tags = ["even" if number % 2 == 0 else "odd"]
            if signals:
                tags.append(SIGNAL_LOOK[signals[number]][0])
            table.insert("", "end", values=values, tags=tuple(tags))

    def make_card(self, parent, column):
        """A white card with a big value and a small caption. Returns both labels."""
        card = ttk.Frame(parent, style="Card.TFrame", padding=12)
        card.grid(row=0, column=column, padx=5, sticky="nsew")
        parent.columnconfigure(column, weight=1)
        value = ttk.Label(card, text="-", style="CardValue.TLabel")
        value.pack(anchor="w")
        caption = ttk.Label(card, text="", style="CardCaption.TLabel")
        caption.pack(anchor="w")
        return value, caption

    # ---------- header and message bar ----------

    def build_header(self):
        header = tk.Frame(self.window, bg=COLORS["primary"], padx=22, pady=12)
        header.pack(fill="x")
        title_row = tk.Frame(header, bg=COLORS["primary"])
        title_row.pack(anchor="w")
        tk.Label(
            title_row, text="BazarDor", bg=COLORS["primary"], fg="white", font=(FONT, 24, "bold")
        ).pack(side="left")
        tk.Label(
            title_row, text="বাজার দর", bg=COLORS["primary"], fg="#FFE6A8", font=(FONT, 18, "bold")
        ).pack(side="left", padx=(12, 0))
        tk.Label(
            header,
            text="Daily market prices for households in Dhaka. Know the price before you buy.",
            bg=COLORS["primary"],
            fg="#DDEFE4",
            font=(FONT, 13),
        ).pack(anchor="w")
        self.tip_label = tk.Label(
            header,
            text=random.choice(TIPS),
            bg=COLORS["primary"],
            fg="#FFE6A8",
            font=(FONT, 12, "italic"),
        )
        self.tip_label.pack(anchor="w", pady=(4, 0))

    def build_message_bar(self):
        self.message = ttk.Label(self.window, text="", padding=(18, 8), font=(FONT, 12))
        self.message.pack(fill="x")

    def say(self, text):
        """Show a message at the bottom, highlighted for a few seconds."""
        self.message.config(text=text, foreground=COLORS["primary"])
        self.window.after(3500, self.fade_message)

    def fade_message(self):
        self.message.config(foreground=COLORS["muted"])

    # ---------- Prices tab: add, update, delete, search ----------

    def build_prices_tab(self):
        tab = ttk.Frame(self.tabs, padding=14)
        self.tabs.add(tab, text="Prices")

        form = ttk.Frame(tab, style="Card.TFrame", padding=12)
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

        buttons = ttk.Frame(tab, padding=(0, 12, 0, 0))
        buttons.pack(fill="x")
        # Tuple of (button text, colour, function to run when clicked)
        actions = (
            ("+ Add", "Green", self.add_record),
            ("Update", "Turmeric", self.update_record),
            ("Delete", "Red", self.delete_record),
            ("Clear form", "Grey", self.clear_form),
        )
        for text, color, command in actions:
            self.make_button(buttons, text, color, command).pack(side="left", padx=(0, 8))

        filters = ttk.Frame(tab, padding=(0, 12, 0, 0))
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
        self.filter_item.set(ALL)
        self.filter_market.set(ALL)
        self.make_button(filters, "Search", "Blue", self.search_records).pack(side="left", padx=4)
        self.make_button(filters, "Show all", "Grey", self.show_all).pack(side="left", padx=4)

        self.price_table = self.make_table(tab, PRICE_COLUMNS, height=11)
        self.price_table.bind("<<TreeviewSelect>>", self.on_row_click)

    def show_records(self, records):
        rows = []
        for record in self.book.newest_first(records):
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
        self.fill_table(self.price_table, rows)

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
        selected = self.price_table.selection()
        if not selected:
            return
        record_id = int(self.price_table.item(selected[0], "values")[0])
        record = self.book.find_record(record_id)
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
        self.say(f"Selected record #{record_id}. Change it, then click Update or Delete.")

    def save_and_refresh(self):
        if not self.book.save():
            messagebox.showwarning("Not saved", "Could not save to the data file.")
        self.refresh_everything()

    def refresh_everything(self):
        self.filter_item.set(ALL)
        self.filter_market.set(ALL)
        self.show_records(self.book.records)
        self.show_analysis()
        self.show_board()

    def add_record(self, event=None):
        try:
            record = self.book.add_record(
                self.date_entry.get(),
                self.item_box.get(),
                self.market_box.get(),
                self.price_entry.get(),
            )
        except ValueError as error:
            messagebox.showerror("Please check", str(error))
            return
        self.save_and_refresh()
        self.price_entry.delete(0, "end")  # keep date, item and market for the next price
        self.tip_label.config(text=random.choice(TIPS))
        self.say(f"Added {record.item} at {record.market}: {record.price:,.2f} Tk/{record.unit()}.")

    def update_record(self):
        if self.selected_id is None:
            messagebox.showinfo("Pick a row", "Click a row in the table first.")
            return
        try:
            self.book.update_record(
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
        self.save_and_refresh()
        self.clear_form()
        self.say(f"Updated record #{record_id}.")

    def delete_record(self):
        if self.selected_id is None:
            messagebox.showinfo("Pick a row", "Click a row in the table first.")
            return
        record_id = self.selected_id
        if not messagebox.askyesno("Delete?", f"Delete record #{record_id}? This can't be undone."):
            return
        try:
            self.book.delete_record(record_id)
        except ValueError as error:
            messagebox.showerror("Not found", str(error))
            return
        self.save_and_refresh()
        self.clear_form()
        self.say(f"Deleted record #{record_id}.")

    def search_records(self):
        item = self.filter_item.get()
        market = self.filter_market.get()
        # "All" means "don't filter", which PriceBook.search expects as ""
        if item == ALL:
            item = ""
        if market == ALL:
            market = ""
        results = self.book.search(item, market)
        self.show_records(results)
        self.say(f"Found {len(results)} records. Click Show all to see everything again.")

    def show_all(self):
        self.filter_item.set(ALL)
        self.filter_market.set(ALL)
        self.show_records(self.book.records)
        self.say(f"Showing all {len(self.book.records)} records.")

    # ---------- Analysis tab: NumPy results for one item ----------

    def build_analysis_tab(self):
        tab = ttk.Frame(self.tabs, padding=14)
        self.tabs.add(tab, text="Analysis")
        self.analysis_tab = tab

        top = ttk.Frame(tab)
        top.pack(fill="x")
        ttk.Label(top, text="Item", style="Big.TLabel").pack(side="left")
        self.analysis_box = ttk.Combobox(
            top, values=tuple(ITEMS), state="readonly", width=24, font=(FONT, 13)
        )
        self.analysis_box.set("Onion (Local)")
        self.analysis_box.pack(side="left", padx=10)
        self.analysis_box.bind("<<ComboboxSelected>>", self.show_analysis)
        self.signal_label = ttk.Label(top, text="", style="Big.TLabel")
        self.signal_label.pack(side="left", padx=18)

        cards = ttk.Frame(tab, padding=(0, 12, 0, 0))
        cards.pack(fill="x")
        # Dictionary: card name -> (value label, caption label)
        self.cards = {}
        for column, name in enumerate(("average", "cheapest", "range", "change")):
            self.cards[name] = self.make_card(cards, column)

        lower = ttk.Frame(tab, padding=(0, 12, 0, 0))
        lower.pack(fill="both", expand=True)

        chart_box = ttk.Frame(lower, style="Card.TFrame", padding=12)
        chart_box.pack(side="left", fill="both", expand=True)
        ttk.Label(chart_box, text="Latest price at each market", style="CardBold.TLabel").pack(
            anchor="w"
        )
        self.chart = tk.Canvas(chart_box, width=560, height=230, bg=COLORS["card"])
        self.chart.configure(highlightthickness=0)
        self.chart.pack(anchor="w", pady=(8, 0))

        details_box = ttk.Frame(lower, style="Card.TFrame", padding=12)
        details_box.pack(side="left", fill="both", padx=(12, 0))
        ttk.Label(details_box, text="Details", style="CardBold.TLabel").pack(anchor="w")
        self.details = ttk.Label(
            details_box, text="", style="Card.TLabel", justify="left", wraplength=320
        )
        self.details.pack(anchor="w", pady=(8, 0))

    def show_analysis(self, event=None):
        item = self.analysis_box.get()
        unit = ITEMS[item]
        result = analysis.analyse_item(self.book.records_for(item))
        if result is None:
            for value, caption in self.cards.values():
                value.config(text="-")
                caption.config(text="")
            self.signal_label.config(text="")
            self.details.config(
                text=f"No prices recorded for {item} yet. Add some on the Prices tab."
            )
            self.draw_market_chart({}, None, unit)
            return

        stats = result["stats"]
        self.set_card("average", f"{stats['average']:,.2f} Tk", f"average now, per {unit}")
        self.set_card("cheapest", f"{result['cheapest_price']:,.2f} Tk", result["cheapest_market"])
        self.set_card(
            "range", f"{stats['lowest']:,.0f} - {stats['highest']:,.0f} Tk", "lowest - highest now"
        )
        self.set_card(
            "change", analysis.change_text(result["change_percent"]), "since the first record"
        )

        signal = result["signal"]
        self.signal_label.config(text=signal, foreground=SIGNAL_LOOK[signal][1])
        self.details.config(
            text=(
                f"Median price now: {stats['median']:,.2f} Tk\n"
                f"Spread between markets: {stats['spread']:,.2f} Tk ({result['stability']})\n"
                f"Usual price (all {result['record_count']} records): "
                f"{result['usual_average']:,.2f} Tk\n\n"
                f"This week's average is {result['percent_of_usual']:.0f}% of the usual price, "
                f"so the signal is: {signal}."
            )
        )
        self.draw_market_chart(result["current_prices"], result["cheapest_market"], unit)

    def set_card(self, name, value_text, caption_text):
        value, caption = self.cards[name]
        value.config(text=value_text)
        caption.config(text=caption_text)

    def draw_market_chart(self, prices, cheapest, unit):
        """Bar chart on a Canvas: one bar per market, the cheapest one in green."""
        canvas = self.chart
        canvas.delete("all")
        if not prices:
            canvas.create_text(
                10, 20, text="No prices yet.", anchor="w", fill=COLORS["muted"], font=(FONT, 12)
            )
            return

        highest = max(prices.values())
        for row, market in enumerate(MARKETS):
            top = 10 + row * 44
            canvas.create_text(
                0, top + 13, text=market, anchor="w", fill=COLORS["text"], font=(FONT, 12)
            )
            if market not in prices:
                canvas.create_text(
                    210, top + 13, text="no price yet", anchor="w", fill=COLORS["muted"]
                )
                continue
            bar_length = prices[market] / highest * 250
            color = COLORS["primary"] if market == cheapest else COLORS["bar"]
            canvas.create_rectangle(210, top, 210 + bar_length, top + 26, fill=color, width=0)
            canvas.create_text(
                218 + bar_length,
                top + 13,
                text=f"{prices[market]:,.0f} Tk/{unit}",
                anchor="w",
                fill=COLORS["text"],
                font=(FONT, 11),
            )

    # ---------- Price Board tab: every item on one screen ----------

    def build_board_tab(self):
        tab = ttk.Frame(self.tabs, padding=14)
        self.tabs.add(tab, text="Price Board")

        ttk.Label(tab, text="Today's rates at a glance", style="Big.TLabel").pack(anchor="w")
        ttk.Label(
            tab,
            text="Average of the latest price at each market. Double-click an item for details.",
            style="Muted.TLabel",
        ).pack(anchor="w")

        self.board_table = self.make_table(tab, BOARD_COLUMNS, height=10)
        self.board_table.bind("<Double-1>", self.open_in_analysis)

        buttons = ttk.Frame(tab, padding=(0, 12, 0, 0))
        buttons.pack(fill="x")
        self.make_button(buttons, "Open in Analysis", "Blue", self.open_in_analysis).pack(
            side="left", padx=(0, 8)
        )
        self.make_button(buttons, "Export report (.txt)", "Green", self.export_report).pack(
            side="left"
        )

    def show_board(self):
        rows = []
        signals = []
        for row in analysis.item_overview(self.book):
            rows.append(
                (
                    row["item"],
                    f"{row['average']:,.2f}",
                    row["unit"],
                    row["cheapest_market"],
                    f"{row['cheapest_price']:,.2f}",
                    analysis.change_text(row["change_percent"]),
                    row["signal"],
                )
            )
            signals.append(row["signal"])
        self.fill_table(self.board_table, rows, signals)

    def open_in_analysis(self, event=None):
        selected = self.board_table.selection()
        if not selected:
            messagebox.showinfo("Pick a row", "Click an item in the table first.")
            return
        item = self.board_table.item(selected[0], "values")[0]
        self.analysis_box.set(item)
        self.show_analysis()
        self.tabs.select(self.analysis_tab)

    def export_report(self):
        if self.book.export_report(analysis.report_lines(self.book)):
            self.say("Report saved as data/price_report.txt")
        else:
            messagebox.showwarning("Not saved", "Could not write the report file.")

    # ---------- Shopping List tab ----------

    def build_shopping_tab(self):
        tab = ttk.Frame(self.tabs, padding=14)
        self.tabs.add(tab, text="Shopping List")

        form = ttk.Frame(tab, style="Card.TFrame", padding=12)
        form.pack(fill="x")
        ttk.Label(form, text="Item", style="CardBold.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Quantity", style="CardBold.TLabel").grid(
            row=0, column=1, sticky="w", padx=8
        )
        self.shop_item_box = ttk.Combobox(
            form, values=tuple(ITEMS), state="readonly", width=24, font=(FONT, 12)
        )
        self.shop_item_box.set(tuple(ITEMS)[0])
        self.shop_item_box.grid(row=1, column=0, pady=(4, 0))
        self.quantity_entry = ttk.Entry(form, width=8, font=(FONT, 12))
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.grid(row=1, column=1, padx=8, pady=(4, 0))
        self.quantity_entry.bind("<Return>", self.add_to_list)
        self.make_button(form, "+ Add to list", "Green", self.add_to_list).grid(
            row=1, column=2, padx=(8, 0), pady=(4, 0)
        )

        self.list_table = self.make_table(tab, LIST_COLUMNS, height=5)

        buttons = ttk.Frame(tab, padding=(0, 10, 0, 0))
        buttons.pack(fill="x")
        actions = (
            ("Estimate cost", "Blue", self.estimate),
            ("Remove item", "Red", self.remove_from_list),
            ("Clear list", "Grey", self.clear_list),
        )
        for text, color, command in actions:
            self.make_button(buttons, text, color, command).pack(side="left", padx=(0, 8))

        self.estimate_table = self.make_table(tab, ESTIMATE_COLUMNS, height=5)
        self.totals_label = ttk.Label(
            tab, text="Add items, then click Estimate cost.", style="Big.TLabel"
        )
        self.totals_label.pack(anchor="w", pady=(10, 0))

    def show_shopping_list(self):
        rows = []
        for item, quantity in self.shopping_list.items():
            rows.append((item, f"{quantity:g}", ITEMS[item]))
        self.fill_table(self.list_table, rows)
        self.fill_table(self.estimate_table, [])
        self.totals_label.config(text="Click Estimate cost to see the totals.")

    def add_to_list(self, event=None):
        item = self.shop_item_box.get()
        try:
            quantity = check_quantity(self.quantity_entry.get())
        except ValueError as error:
            messagebox.showerror("Please check", str(error))
            return
        already_listed = item in self.shopping_list
        self.shopping_list[item] = quantity
        self.show_shopping_list()
        if already_listed:
            self.say(f"Changed {item} to {quantity:g} {ITEMS[item]}.")
        else:
            self.say(f"Added {quantity:g} {ITEMS[item]} of {item} to the list.")

    def remove_from_list(self):
        selected = self.list_table.selection()
        if not selected:
            messagebox.showinfo("Pick a row", "Click an item in the shopping list first.")
            return
        item = self.list_table.item(selected[0], "values")[0]
        del self.shopping_list[item]
        self.show_shopping_list()
        self.say(f"Removed {item} from the list.")

    def clear_list(self):
        self.shopping_list.clear()
        self.show_shopping_list()
        self.say("Shopping list cleared.")

    def estimate(self):
        if not self.shopping_list:
            messagebox.showinfo("Shopping list", "Add at least one item first.")
            return
        result = analysis.shopping_estimate(self.book, self.shopping_list)
        rows = []
        for line in result["lines"]:
            rows.append(
                (
                    line["item"],
                    f"{line['quantity']:g}",
                    line["market"],
                    f"{line['cheapest_cost']:,.2f}",
                    f"{line['average_cost']:,.2f}",
                )
            )
        self.fill_table(self.estimate_table, rows)
        self.totals_label.config(
            text=(
                f"Cheapest markets: {result['total_cheapest']:,.2f} Tk     "
                f"At average prices: {result['total_average']:,.2f} Tk     "
                f"You save {result['saving']:,.2f} Tk"
            ),
            foreground=COLORS["primary"],
        )
        if result["missing"]:
            self.say("No prices yet for: " + ", ".join(result["missing"]))
        else:
            self.say(f"Buying at the cheapest markets saves {result['saving']:,.2f} Tk.")


def main():
    window = tk.Tk()
    BazarDorApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
