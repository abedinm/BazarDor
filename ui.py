"""Look and feel, plus small helpers every tab uses to build its widgets.

Colours and fonts live here in one place, so changing the look is easy.
"""

from tkinter import ttk

FONT = "Helvetica"

# Dictionary: every colour the app uses
COLORS = {
    "background": "#F4F6F1",
    "card": "#FFFFFF",
    "primary": "#1E7A4C",  # banana-leaf green
    "primary_dark": "#17603C",
    "turmeric": "#A86A12",
    "red": "#B0442C",
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
    "Good time to buy": ("good", COLORS["primary"]),
    "Normal price": ("normal", COLORS["turmeric"]),
    "Expensive now": ("high", COLORS["red"]),
}

# Dictionary: fair-price verdict -> text colour
VERDICT_COLORS = {
    "Fair price": COLORS["primary"],
    "A little high": COLORS["turmeric"],
    "Overpriced": COLORS["red"],
}

ALL = "All"  # filter choice meaning "don't filter"


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
    style.configure(
        "CardMuted.TLabel", background=COLORS["card"], foreground=COLORS["muted"], font=(FONT, 11)
    )
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
    style.configure("Verdict.TLabel", background=COLORS["card"], font=(FONT, 24, "bold"))
    style.configure("Alert.TLabel", foreground=COLORS["red"], font=(FONT, 12, "bold"))

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
        padding=(16, 8),
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


def make_button(parent, text, color, command):
    return ttk.Button(parent, text=text, style=f"{color}.TButton", command=command, cursor="hand2")


def make_table(parent, columns, height):
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


def fill_table(table, rows, signals=None):
    """Replace a table's rows. signals (optional) gives each row's buy signal."""
    for row in table.get_children():
        table.delete(row)
    for number, values in enumerate(rows):
        tags = ["even" if number % 2 == 0 else "odd"]
        if signals:
            tags.append(SIGNAL_LOOK[signals[number]][0])
        table.insert("", "end", values=values, tags=tuple(tags))


def make_card(parent, column):
    """A white card with a big value and a small caption. Returns both labels."""
    card = ttk.Frame(parent, style="Card.TFrame", padding=12)
    card.grid(row=0, column=column, padx=5, sticky="nsew")
    parent.columnconfigure(column, weight=1)
    value = ttk.Label(card, text="-", style="CardValue.TLabel")
    value.pack(anchor="w")
    caption = ttk.Label(card, text="", style="CardCaption.TLabel")
    caption.pack(anchor="w")
    return value, caption


def selected_value(table, column=0):
    """The value in one column of the selected table row, or None if no row is selected."""
    selected = table.selection()
    if not selected:
        return None
    return table.item(selected[0], "values")[column]
