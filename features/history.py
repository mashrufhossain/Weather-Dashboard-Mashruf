import tkinter as tk
from tkinter import ttk
from constants import HISTORY_FOOTER
from styles import NORMAL_FONT


def treeview_sort_column(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        try:
            l.sort(
                key=lambda t: float(t[0].split()[0].replace("°C", "").replace("°F", "")
                                .replace("%", "").replace("m/s", "").replace("hPa", "")),
                reverse=reverse
            )
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        for c in tv["columns"]:
            base_text = c.replace("_", " ").title()
            tv.heading(c, text=base_text, command=lambda _col=c: self.treeview_sort_column(tv, _col, False))

        arrow = " ▲" if not reverse else " ▼"
        tv.heading(col, text=col.replace("_", " ").title() + arrow,
                command=lambda: self.treeview_sort_column(tv, col, not reverse))
        
        
def create_history_tab(self):
    columns = ("timestamp", "city", "temp", "feels_like", "weather", "humidity", "pressure",
            "visibility", "wind", "sea_level", "grnd_level", "sunrise", "sunset")
    self.tree = ttk.Treeview(self.history_frame, columns=columns, show="headings", height=18)
    self.tree.pack(fill="both", expand=True, padx=12, pady=(14, 0))

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview.Heading", font=("Helvetica Neue", 14, "bold"), background="#444", foreground="#DEAFEE")
    style.configure("Treeview", font=NORMAL_FONT, rowheight=26, background="black", fieldbackground="black", foreground="white")
    style.map("Treeview", background=[('selected', '#555')], foreground=[('selected', '#fff')])

    self.tree.tag_configure('centered', anchor='center')

    for col in columns:
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

    self.history_footer = tk.Label(self.history_frame, text=HISTORY_FOOTER, font=NORMAL_FONT, fg="#fff", bg="black")
    self.history_footer.pack(side="bottom", pady=(0, 12))


def refresh_history(self):
    for i in self.tree.get_children():
        self.tree.delete(i)
    entries = self.db.get_all_history()
    if not entries:
        self.tree.insert("", "end", values=["No history found."] + [""] * 13)
        return

    t_unit = "°C" if self.temp_unit == "C" else "°F"

    for entry in entries:
        try:
            temp = float(entry[2]) if entry[2] is not None else None
            temp_str = f"{self.convert_temp(temp):.2f}{t_unit}" if temp is not None else "N/A"
        except (ValueError, TypeError):
            temp_str = "N/A"

        try:
            feels_like = float(entry[3]) if entry[3] is not None else None
            feels_like_str = f"{self.convert_temp(feels_like):.2f}{t_unit}" if feels_like is not None else "N/A"
        except (ValueError, TypeError):
            feels_like_str = "N/A"

        row = (
            entry[0], entry[1],
            temp_str,
            feels_like_str,
            entry[4] or "N/A",
            entry[5] or "N/A",
            entry[6] or "N/A",
            entry[7] or "N/A",
            entry[8] or "N/A",
            entry[9] or "N/A",
            entry[10] or "N/A",
            entry[11] or "N/A",
            entry[12] or "N/A"
        )
        self.tree.insert("", "end", values=row, tags=('centered',))
    self.root.update_idletasks()