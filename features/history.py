"""
history.py

History UI module for Weather Dashboard.

Provides functions to:
- treeview_sort_column: Sort a Treeview column numerically or lexically when its header is clicked.
- create_history_tab: Initialize and style the history tab with a Treeview and footer label.
- refresh_history: Load weather history entries from the database and populate the Treeview rows.
"""

import tkinter as tk                                   # Core Tkinter library for GUI components
from tkinter import ttk                                # Themed widgets: Treeview and Style support
from constants import HISTORY_FOOTER                   # Footer text constant for the history tab
from styles import NORMAL_FONT, SMALL_FONT             # Standard font configuration for text elements


def treeview_sort_column(self, tv, col, reverse):
    
    """
    Sort a given Treeview column when its header is clicked.

    Attempts to parse and sort values numerically by stripping common unit suffixes.
    Falls back to lexicographical sort on failure. Toggles sort order and updates
    the column header to display an arrow indicator.

    Args:
        self: Reference to the WeatherApp instance.
        tv (ttk.Treeview): The Treeview widget to sort.
        col (str): Column identifier to sort by.
        reverse (bool): True for descending sort, False for ascending.
    """

    # Build a list of tuples: (cell_text, row_id) for all rows
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    
    try:
        # Numeric sort: strip units then convert to float
        l.sort(
            key=lambda t: float(t[0].split()[0].replace("°C", "").replace("°F", "")
                            .replace("%", "").replace("m/s", "").replace("hPa", "")),
            reverse=reverse
        )
    except ValueError:
        # Fall back to simple string sort if conversion fails (e.g., 'N/A')
        l.sort(reverse=reverse)

    # Reorder each row in the Treeview according to sorted list
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    # Reset all column headers to default text and sort callback
    for c in tv["columns"]:
        base_text = c.replace("_", " ").title()
        tv.heading(c, text=base_text, command=lambda _col=c: self.treeview_sort_column(tv, _col, False))

    # Add arrow indicator to the active column header
    arrow = " ▲" if not reverse else " ▼"
    tv.heading(col, text=col.replace("_", " ").title() + arrow,
            command=lambda: self.treeview_sort_column(tv, col, not reverse))
        
        
def create_history_tab(self):

    """
    Initialize the History tab:
    - Create and pack a Treeview with columns matching the data schema.
    - Apply visual styles to headings and rows.
    - Configure click handlers for sorting on each column.
    - Add a footer label with guidance text.
    """

    # Define columns in the order they should appear
    columns = ("timestamp", "city", "temp", "feels_like", "weather", "humidity", "pressure",
            "visibility", "wind", "sea_level", "grnd_level", "sunrise", "sunset")
    
    # Instantiate the Treeview widget in the history_frame
    self.tree = ttk.Treeview(self.history_frame, columns=columns, show="headings", height=18)
    self.tree.pack(fill="both", expand=True, padx=12, pady=(14, 0))

    # Configure styling for headings and rows
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview.Heading", font=("Helvetica Neue", 14, "bold"), background="#444", foreground="#DEAFEE")
    style.configure("Treeview", font=NORMAL_FONT, rowheight=26, background="black", fieldbackground="black", foreground="white")
    style.map("Treeview", background=[('selected', '#555')], foreground=[('selected', '#fff')])

    # Center-align text in rows tagged 'centered'
    self.tree.tag_configure('centered', anchor='center')

    # Setup each column's width, header text, and bind sorting callback
    for col in columns:

        # Convert snake_case to Title Case
        display_text = col.replace("_", " ").title()

        if col == "timestamp":
            self.tree.column(col, anchor="center", width=200)
        elif col == "city":
            self.tree.column(col, anchor="center", width=250)
        else:
            self.tree.column(col, anchor="center", width=120)

        self.tree.heading(col,
            text=display_text,
            command=lambda _col=col: treeview_sort_column(self, self.tree, _col, False))

    # Footer label with descriptive text at bottom of tab
    self.history_footer = tk.Label(self.history_frame, text=HISTORY_FOOTER, font=SMALL_FONT, fg="#fff", bg="black")
    self.history_footer.pack(side="bottom", pady=(0, 12))


def refresh_history(self):

    """
    Refresh the displayed history records:
    - Clear existing rows in the Treeview.
    - Fetch history entries from the database.
    - Format temperatures and handle missing data gracefully.
    - Insert each row into the Treeview with centered alignment.
    """

    # Clear all current rows
    for i in self.tree.get_children():
        self.tree.delete(i)

    # Retrieve entries from the database
    entries = self.db.get_all_history()
    if not entries:
        self.tree.insert("", "end", values=["No history found."] + [""] * 13)
        return
    
    # Determine the unit symbol based on user preference
    t_unit = "°C" if self.temp_unit == "C" else "°F"

    # Loop through each database entry and format for display
    for entry in entries:
        # Safely parse and format temperature
        try:
            temp = float(entry[2]) if entry[2] is not None else None
            temp_str = f"{self.convert_temp(temp):.2f}{t_unit}" if temp is not None else "N/A"
        except (ValueError, TypeError):
            temp_str = "N/A"

        # Safely parse and format 'feels like'
        try:
            feels_like = float(entry[3]) if entry[3] is not None else None
            feels_like_str = f"{self.convert_temp(feels_like):.2f}{t_unit}" if feels_like is not None else "N/A"
        except (ValueError, TypeError):
            feels_like_str = "N/A"

        # Assemble row tuple, defaulting to "N/A" for missing fields
        row = (
            entry[0], entry[1],         # timestamp, city
            temp_str,                   # temperature
            feels_like_str,             # feels like
            entry[4] or "N/A",          # weather description
            entry[5] or "N/A",          # humidity
            entry[6] or "N/A",          # pressure
            entry[7] or "N/A",          # visibility
            entry[8] or "N/A",          # wind
            entry[9] or "N/A",          # sea level
            entry[10] or "N/A",         # ground level
            entry[11] or "N/A",         # sunrise
            entry[12] or "N/A"          # sunset
        )

        # Insert row with a centered tag
        self.tree.insert("", "end", values=row, tags=('centered',))
        
    # Refresh UI to ensure updates are shown
    self.root.update_idletasks()