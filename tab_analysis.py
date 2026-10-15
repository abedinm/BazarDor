"""Analysis tab: NumPy results and a bar chart for one item."""

import tkinter as tk
from tkinter import ttk

import analysis
from price_record import ITEMS, MARKETS
from ui import COLORS, FONT, SIGNAL_LOOK, make_card


class AnalysisTab:
    def __init__(self, app, notebook):
        self.app = app  # the main BazarDorApp: gives us app.book
        self.frame = ttk.Frame(notebook, padding=14)
        notebook.add(self.frame, text="Analysis")
        self.build_top()
        self.build_cards()
        self.build_chart_and_details()

    # ---------- building the tab ----------

    def build_top(self):
        top = ttk.Frame(self.frame)
        top.pack(fill="x")
        ttk.Label(top, text="Item", style="Big.TLabel").pack(side="left")
        self.item_box = ttk.Combobox(
            top, values=tuple(ITEMS), state="readonly", width=24, font=(FONT, 13)
        )
        self.item_box.set("Onion (Local)")
        self.item_box.pack(side="left", padx=10)
        self.item_box.bind("<<ComboboxSelected>>", self.refresh)
        self.signal_label = ttk.Label(top, text="", style="Big.TLabel")
        self.signal_label.pack(side="left", padx=18)

    def build_cards(self):
        cards = ttk.Frame(self.frame, padding=(0, 12, 0, 0))
        cards.pack(fill="x")
        # Dictionary: card name -> (value label, caption label)
        self.cards = {}
        for column, name in enumerate(("average", "cheapest", "range", "change")):
            self.cards[name] = make_card(cards, column)

    def build_chart_and_details(self):
        lower = ttk.Frame(self.frame, padding=(0, 12, 0, 0))
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

    # ---------- showing the analysis ----------

    def show_item(self, item):
        self.item_box.set(item)
        self.refresh()

    def refresh(self, event=None):
        item = self.item_box.get()
        unit = ITEMS[item]
        result = analysis.analyse_item(self.app.book.records_for(item))
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
        self.set_card(
            "cheapest",
            f"{result['cheapest_price']:,.2f} Tk",
            f"cheapest, at {result['cheapest_market']}",
        )
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
