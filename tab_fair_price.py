"""Fair Price Check tab: is the price a seller asks fair?

The shopper picks an item and types the price the seller asks. The app
compares it with what markets charge now and shows a clear verdict.
"""

import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

import analysis
from price_record import ITEMS, MARKETS
from ui import COLORS, FONT, VERDICT_COLORS, make_button
from validation import check_price

RULER_WIDTH = 620  # width of the price ruler drawing, in pixels


class FairPriceTab:
    def __init__(self, app, notebook):
        self.app = app  # the main BazarDorApp: gives us app.book and app.say()
        self.frame = ttk.Frame(notebook, padding=14)
        notebook.add(self.frame, text="Fair Price Check")
        self.build_form()
        self.build_result()

    # ---------- building the tab ----------

    def build_form(self):
        ttk.Label(self.frame, text="Is this price fair?", style="Big.TLabel").pack(anchor="w")
        ttk.Label(
            self.frame,
            text="Before you pay, type the price the seller asks. "
            "BazarDor compares it with what markets charge now.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        form = ttk.Frame(self.frame, style="Card.TFrame", padding=12)
        form.pack(fill="x")
        titles = ("Item", "Market you are at", "Price asked (Tk)")
        for column, text in enumerate(titles):
            ttk.Label(form, text=text, style="CardBold.TLabel").grid(
                row=0, column=column, sticky="w", padx=6
            )
        self.item_box = ttk.Combobox(
            form, values=tuple(ITEMS), state="readonly", width=22, font=(FONT, 12)
        )
        self.item_box.set("Onion (Local)")
        self.market_box = ttk.Combobox(
            form, values=MARKETS, state="readonly", width=25, font=(FONT, 12)
        )
        self.market_box.set("Neighbourhood Shop")
        self.price_entry = ttk.Entry(form, width=10, font=(FONT, 12))
        inputs = (self.item_box, self.market_box, self.price_entry)
        for column, widget in enumerate(inputs):
            widget.grid(row=1, column=column, padx=6, pady=(4, 0), sticky="w")
        self.unit_label = ttk.Label(form, text="Tk per kg", style="Card.TLabel")
        self.unit_label.grid(row=1, column=3, sticky="w")

        self.item_box.bind("<<ComboboxSelected>>", self.update_unit_label)
        self.price_entry.bind("<Return>", self.check)  # Enter checks the price

        buttons = ttk.Frame(self.frame, padding=(0, 12, 0, 0))
        buttons.pack(fill="x")
        make_button(buttons, "Check price", "Blue", self.check).pack(side="left", padx=(0, 8))
        make_button(buttons, "Save this price to my records", "Green", self.save_price).pack(
            side="left"
        )

    def build_result(self):
        result = ttk.Frame(self.frame, style="Card.TFrame", padding=16)
        result.pack(fill="both", expand=True, pady=(14, 0))
        self.verdict_label = ttk.Label(result, text="", style="Verdict.TLabel")
        self.verdict_label.pack(anchor="w")
        self.details_label = ttk.Label(
            result,
            text="Choose an item, type the price you were asked, then click Check price.",
            style="Card.TLabel",
            justify="left",
            wraplength=900,
        )
        self.details_label.pack(anchor="w", pady=(6, 10))
        self.ruler = tk.Canvas(result, width=RULER_WIDTH + 40, height=90, bg=COLORS["card"])
        self.ruler.configure(highlightthickness=0)
        self.ruler.pack(anchor="w")
        ttk.Label(
            result,
            text="Based only on prices recorded in BazarDor. Saving the price keeps "
            "your records up to date.",
            style="CardMuted.TLabel",
        ).pack(anchor="w", pady=(8, 0))

    # ---------- actions ----------

    def update_unit_label(self, event=None):
        unit = ITEMS.get(self.item_box.get(), "")
        self.unit_label.config(text=f"Tk per {unit}")

    def check(self, event=None):
        item = self.item_box.get()
        unit = ITEMS[item]
        try:
            asked = check_price(self.price_entry.get())
        except ValueError as error:
            messagebox.showerror("Please check", str(error))
            return

        result = analysis.fair_price_check(self.app.book.records_for(item), asked)
        if result is None:
            self.verdict_label.config(text="No prices yet", foreground=COLORS["muted"])
            self.details_label.config(
                text=f"There are no prices for {item} yet. Add some on the Prices tab first."
            )
            self.ruler.delete("all")
            return

        verdict = result["verdict"]
        difference = asked - result["average"]
        if difference > 0:
            compared = f"{difference:,.2f} Tk ({result['percent'] - 100:.0f}%) more than"
        else:
            compared = f"{-difference:,.2f} Tk ({100 - result['percent']:.0f}%) less than"
        saving = asked - result["cheapest_price"]

        lines = [
            f"The seller asks {asked:,.2f} Tk per {unit} for {item}.",
            f"That is {compared} the average of {result['average']:,.2f} Tk "
            "that markets charge now.",
        ]
        if saving > 0:
            lines.append(
                f"Cheapest now: {result['cheapest_price']:,.2f} Tk at "
                f"{result['cheapest_market']}, which would save {saving:,.2f} Tk per {unit}."
            )
        else:
            lines.append("This is as cheap as any market we know of right now.")

        self.verdict_label.config(text=verdict, foreground=VERDICT_COLORS[verdict])
        self.details_label.config(text="\n".join(lines))
        self.draw_ruler(result, asked, verdict)
        self.app.say(f"{item} at {asked:,.2f} Tk: {verdict}.")

    def draw_ruler(self, result, asked, verdict):
        """A line from the lowest to the highest price, with a marker for the asked price."""
        canvas = self.ruler
        canvas.delete("all")
        low = min(result["lowest"], asked)
        high = max(result["highest"], asked)
        if high == low:
            high = low + 1  # avoid dividing by zero when every price is the same

        canvas.create_line(20, 50, 20 + RULER_WIDTH, 50, fill=COLORS["bar"], width=8)
        # Tuple of (label, price, colour) for the fixed points on the ruler
        marks = (
            ("cheapest", result["cheapest_price"], COLORS["primary"]),
            ("average", result["average"], COLORS["turmeric"]),
            ("highest", result["highest"], COLORS["muted"]),
        )
        for label, price, color in marks:
            x = self.price_to_x(price, low, high)
            canvas.create_line(x, 40, x, 60, fill=color, width=3)
            canvas.create_text(x, 75, text=f"{label} {price:,.0f}", fill=color, font=(FONT, 10))

        x = self.price_to_x(asked, low, high)
        color = VERDICT_COLORS[verdict]
        canvas.create_polygon(x - 8, 18, x + 8, 18, x, 36, fill=color)
        canvas.create_text(x, 9, text=f"asked {asked:,.0f}", fill=color, font=(FONT, 11, "bold"))

    def price_to_x(self, price, low, high):
        """Where a price sits on the ruler: low is the left end, high is the right end."""
        return 20 + (price - low) / (high - low) * RULER_WIDTH

    def save_price(self):
        try:
            record = self.app.book.add_record(
                date.today().isoformat(),
                self.item_box.get(),
                self.market_box.get(),
                self.price_entry.get(),
            )
        except ValueError as error:
            messagebox.showerror("Please check", str(error))
            return
        self.app.save_and_refresh()
        self.app.say(
            f"Saved {record.item} at {record.market}: {record.price:,.2f} Tk/{record.unit()}."
        )
