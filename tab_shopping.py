"""Shopping List tab: plan the bazar, check it against a budget, and find
the cheapest way to buy it."""

from tkinter import messagebox, ttk

import analysis
from price_record import ITEMS
from ui import COLORS, FONT, fill_table, make_button, make_table, selected_value
from validation import check_budget, check_family_size, check_quantity

# Dictionaries: table column -> width in pixels
LIST_COLUMNS = {"Item": 220, "Quantity": 90, "Unit": 70}
ESTIMATE_COLUMNS = {
    "Item": 190,
    "Qty": 60,
    "Cheapest at": 210,
    "Cost there (Tk)": 130,
    "At average (Tk)": 130,
}


class ShoppingTab:
    def __init__(self, app, notebook):
        self.app = app  # the main BazarDorApp: gives us app.book and app.say()
        self.shopping_list = {}  # dictionary: item -> quantity
        self.frame = ttk.Frame(notebook, padding=14)
        notebook.add(self.frame, text="Shopping List")
        self.build_form()
        self.list_table = make_table(self.frame, LIST_COLUMNS, height=4)
        self.build_buttons()
        self.estimate_table = make_table(self.frame, ESTIMATE_COLUMNS, height=4)
        self.result_label = ttk.Label(
            self.frame,
            text="Add items or load a family basket, then click Estimate cost.",
            justify="left",
            font=(FONT, 12, "bold"),
            wraplength=1000,
        )
        self.result_label.pack(anchor="w", pady=(10, 0))

    # ---------- building the tab ----------

    def build_form(self):
        form = ttk.Frame(self.frame, style="Card.TFrame", padding=12)
        form.pack(fill="x")

        # Row 1: add one item
        ttk.Label(form, text="Item", style="CardBold.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Quantity", style="CardBold.TLabel").grid(
            row=0, column=1, sticky="w", padx=8
        )
        self.item_box = ttk.Combobox(
            form, values=tuple(ITEMS), state="readonly", width=24, font=(FONT, 12)
        )
        self.item_box.set(tuple(ITEMS)[0])
        self.item_box.grid(row=1, column=0, pady=(4, 0), sticky="w")
        self.quantity_entry = ttk.Entry(form, width=8, font=(FONT, 12))
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.grid(row=1, column=1, padx=8, pady=(4, 0), sticky="w")
        self.quantity_entry.bind("<Return>", self.add_to_list)
        make_button(form, "+ Add to list", "Green", self.add_to_list).grid(
            row=1, column=2, pady=(4, 0), sticky="w"
        )

        # Row 2: family basket and budget
        ttk.Label(form, text="Family size", style="CardBold.TLabel").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )
        ttk.Label(form, text="Monthly budget (Tk)", style="CardBold.TLabel").grid(
            row=2, column=3, sticky="w", padx=(24, 0), pady=(10, 0)
        )
        basket_row = ttk.Frame(form, style="Card.TFrame")
        basket_row.grid(row=3, column=0, columnspan=3, sticky="w", pady=(4, 0))
        self.family_entry = ttk.Entry(basket_row, width=5, font=(FONT, 12))
        self.family_entry.insert(0, "4")
        self.family_entry.pack(side="left")
        make_button(basket_row, "Load monthly family basket", "Turmeric", self.load_basket).pack(
            side="left", padx=8
        )
        self.budget_entry = ttk.Entry(form, width=12, font=(FONT, 12))
        self.budget_entry.grid(row=3, column=3, padx=(24, 0), pady=(4, 0), sticky="w")

    def build_buttons(self):
        buttons = ttk.Frame(self.frame, padding=(0, 10, 0, 0))
        buttons.pack(fill="x")
        actions = (
            ("Estimate cost", "Blue", self.estimate),
            ("Remove item", "Red", self.remove_from_list),
            ("Clear list", "Grey", self.clear_list),
        )
        for text, color, command in actions:
            make_button(buttons, text, color, command).pack(side="left", padx=(0, 8))

    # ---------- the list ----------

    def show_list(self):
        rows = []
        for item, quantity in self.shopping_list.items():
            rows.append((item, f"{quantity:g}", ITEMS[item]))
        fill_table(self.list_table, rows)
        fill_table(self.estimate_table, [])
        self.result_label.config(
            text="Click Estimate cost to see the totals.", foreground=COLORS["text"]
        )

    def add_to_list(self, event=None):
        item = self.item_box.get()
        try:
            quantity = check_quantity(self.quantity_entry.get())
        except ValueError as error:
            messagebox.showerror("Please check", str(error))
            return
        already_listed = item in self.shopping_list
        self.shopping_list[item] = quantity
        self.show_list()
        if already_listed:
            self.app.say(f"Changed {item} to {quantity:g} {ITEMS[item]}.")
        else:
            self.app.say(f"Added {quantity:g} {ITEMS[item]} of {item} to the list.")

    def load_basket(self):
        try:
            family_size = check_family_size(self.family_entry.get())
        except ValueError as error:
            messagebox.showerror("Please check", str(error))
            return
        self.shopping_list = analysis.family_basket(family_size)
        self.show_list()
        self.app.say(
            f"Loaded a typical month of essentials for {family_size} people. "
            "Change any quantity by adding the item again."
        )

    def remove_from_list(self):
        item = selected_value(self.list_table)
        if item is None:
            messagebox.showinfo("Pick a row", "Click an item in the shopping list first.")
            return
        del self.shopping_list[item]
        self.show_list()
        self.app.say(f"Removed {item} from the list.")

    def clear_list(self):
        self.shopping_list.clear()
        self.show_list()
        self.app.say("Shopping list cleared.")

    # ---------- the estimate ----------

    def estimate(self):
        if not self.shopping_list:
            messagebox.showinfo("Shopping list", "Add at least one item first.")
            return
        try:
            budget = check_budget(self.budget_entry.get())
        except ValueError as error:
            messagebox.showerror("Please check", str(error))
            return

        result = analysis.shopping_estimate(self.app.book, self.shopping_list)
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
        fill_table(self.estimate_table, rows)

        lines = [
            f"Each item at its cheapest market: {result['total_cheapest']:,.2f} Tk "
            f"(at average prices {result['total_average']:,.2f} Tk, "
            f"so you save {result['saving']:,.2f} Tk)."
        ]

        # Most people buy everything in one place, so also find the best single market
        market_totals = analysis.cost_by_market(self.app.book, self.shopping_list)
        if market_totals:
            best_market, best_total = analysis.cheapest_market(market_totals)
            worst_total = max(market_totals.values())
            lines.append(
                f"Everything at one market: {best_market} is cheapest at {best_total:,.2f} Tk, "
                f"{worst_total - best_total:,.2f} Tk less than the most expensive market."
            )
            plan_total = best_total
        else:
            plan_total = result["total_cheapest"]

        color = COLORS["primary"]
        if budget is not None:
            if plan_total <= budget:
                lines.append(
                    f"Within your {budget:,.0f} Tk budget: {budget - plan_total:,.2f} Tk left."
                )
            else:
                lines.append(
                    f"Over your {budget:,.0f} Tk budget by {plan_total - budget:,.2f} Tk. "
                    "Reduce some quantities or remove an item."
                )
                color = COLORS["red"]
        if result["missing"]:
            lines.append("No prices yet for: " + ", ".join(result["missing"]) + ".")

        self.result_label.config(text="\n".join(lines), foreground=color)
        self.app.say(f"Estimated {len(self.shopping_list)} items.")
