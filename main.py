"""BazarDor - Daily Market Price Tracker (main file, Tkinter GUI).

Run:  python main.py

This file builds the window and puts the five tabs together.
Each tab is its own class in its own file (tab_*.py).
"""

import random
import tkinter as tk
from tkinter import messagebox, ttk

from price_book import PriceBook
from tab_analysis import AnalysisTab
from tab_board import BoardTab
from tab_fair_price import FairPriceTab
from tab_prices import PricesTab
from tab_shopping import ShoppingTab
from ui import COLORS, FONT, setup_styles

# Tuple: friendly tips, one is picked at random
TIPS = (
    "Tip: ask the price first, then use Fair Price Check before you pay.",
    "Tip: wholesale markets like Karwan Bazar are often cheapest for rice and vegetables.",
    "Tip: check the Price Board before the weekly bazar.",
    "Tip: buying the whole list at one cheap market saves time and money.",
    "Tip: record prices every week so the trends become meaningful.",
)


class BazarDorApp:
    def __init__(self, window):
        self.window = window
        self.window.title("BazarDor - Daily Market Price Tracker")
        self.window.geometry("1080x800")
        self.window.minsize(1000, 740)
        self.window.configure(bg=COLORS["background"])
        setup_styles(window)

        self.book = PriceBook()  # every tab shares this one PriceBook

        self.build_header()
        self.tabs = ttk.Notebook(self.window)
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(12, 0))
        # Each tab gets this app object, so it can reach the PriceBook and the message bar
        self.prices_tab = PricesTab(self, self.tabs)
        self.fair_tab = FairPriceTab(self, self.tabs)
        self.analysis_tab = AnalysisTab(self, self.tabs)
        self.board_tab = BoardTab(self, self.tabs)
        self.shopping_tab = ShoppingTab(self, self.tabs)
        self.build_message_bar()

        self.refresh_everything()
        self.say(self.book.load_message)

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

    # ---------- things every tab can ask the app to do ----------

    def say(self, text):
        """Show a message at the bottom, highlighted for a few seconds."""
        self.message.config(text=text, foreground=COLORS["primary"])
        self.window.after(3500, self.fade_message)

    def fade_message(self):
        self.message.config(foreground=COLORS["muted"])

    def new_tip(self):
        self.tip_label.config(text=random.choice(TIPS))

    def refresh_everything(self):
        """Redraw the tabs that show records, after the records change."""
        self.prices_tab.refresh()
        self.analysis_tab.refresh()
        self.board_tab.refresh()

    def save_and_refresh(self):
        if not self.book.save():
            messagebox.showwarning("Not saved", "Could not save to the data file.")
        self.refresh_everything()

    def show_item_analysis(self, item):
        """Open the Analysis tab for one item."""
        self.analysis_tab.show_item(item)
        self.tabs.select(self.analysis_tab.frame)


def main():
    window = tk.Tk()
    BazarDorApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
