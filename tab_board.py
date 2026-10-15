"""Price Board tab: every item on one screen, with price alerts."""

from tkinter import messagebox, ttk

import analysis
from ui import fill_table, make_button, make_table, selected_value

# Dictionary: table column -> width in pixels
COLUMNS = {
    "Item": 180,
    "Average (Tk)": 100,
    "Unit": 60,
    "Cheapest at": 200,
    "Lowest (Tk)": 100,
    "Change": 150,
    "Signal": 140,
}


class BoardTab:
    def __init__(self, app, notebook):
        self.app = app  # the main BazarDorApp: gives us app.book and app.say()
        self.frame = ttk.Frame(notebook, padding=14)
        notebook.add(self.frame, text="Price Board")

        ttk.Label(self.frame, text="Today's rates at a glance", style="Big.TLabel").pack(anchor="w")
        self.alert_label = ttk.Label(self.frame, text="", style="Alert.TLabel", wraplength=980)
        self.alert_label.pack(anchor="w", pady=(4, 0))
        self.good_label = ttk.Label(self.frame, text="", wraplength=980)
        self.good_label.pack(anchor="w")
        ttk.Label(
            self.frame,
            text="Average of the latest price at each market. Double-click an item for details.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        self.table = make_table(self.frame, COLUMNS, height=9)
        self.table.bind("<Double-1>", self.open_in_analysis)

        buttons = ttk.Frame(self.frame, padding=(0, 12, 0, 0))
        buttons.pack(fill="x")
        make_button(buttons, "Open in Analysis", "Blue", self.open_in_analysis).pack(
            side="left", padx=(0, 8)
        )
        make_button(buttons, "Export report (.txt)", "Green", self.export_report).pack(side="left")

    def refresh(self):
        rows = []
        signals = []
        for row in analysis.item_overview(self.app.book):
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
        fill_table(self.table, rows, signals)
        self.show_alerts()

    def show_alerts(self):
        alerts = analysis.price_alerts(self.app.book)
        if alerts:
            parts = []
            for item, change in alerts:
                parts.append(f"{item} is up {change:.1f}%")
            self.alert_label.config(text="Price alert: " + "; ".join(parts) + ".")
        else:
            self.alert_label.config(text="No big price rises right now.")

        good = analysis.good_buys(self.app.book)
        if good:
            self.good_label.config(text="Good time to buy: " + ", ".join(good) + ".")
        else:
            self.good_label.config(text="")

    def open_in_analysis(self, event=None):
        item = selected_value(self.table)
        if item is None:
            messagebox.showinfo("Pick a row", "Click an item in the table first.")
            return
        self.app.show_item_analysis(item)

    def export_report(self):
        if self.app.book.export_report(analysis.report_lines(self.app.book)):
            self.app.say("Report saved as data/price_report.txt")
        else:
            messagebox.showwarning("Not saved", "Could not write the report file.")
