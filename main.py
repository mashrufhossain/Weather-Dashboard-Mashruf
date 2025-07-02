import tkinter as tk
from tkinter import ttk, messagebox
from api import fetch_weather, fetch_5day_forecast
from db import WeatherDB
import os

HEADER_FONT = ("Helvetica Neue", 34, "bold")
NORMAL_FONT = ("Helvetica Neue", 16)
SMALL_FONT = ("Helvetica Neue", 14)

TAB_BG = "#222"
TAB_FG = "#fff"
ACTIVE_TAB_BG = "#DEAFEE"
ACTIVE_TAB_FG = "#111"
HISTORY_FOOTER = "This tab shows all previous weather history entries. Columns can be sorted by clicking their headers."
STATS_FOOTER = "This tab summarizes weather history with key statistics and records, calculated using SQL."
FORECAST_FOOTER = "This tab displays predictive forecasts for the city entered."

def title_case(s):
    return ' '.join([w.capitalize() for w in s.split()])

class WeatherApp:
    def __init__(self, root):
        self.root = root
        root.title("Weather Dashboard")
        root.configure(bg="black")
        root.geometry("1900x1025")
        root.minsize(1400, 800)

        self.db = WeatherDB(os.path.join("data", "weather.db"))
        self.temp_unit = "C"

        self.create_widgets()
        self.create_history_tab()
        self.create_stats_tab()
        self.create_forecast_tab()
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def create_widgets(self):
        header = tk.Label(self.root, text="What's in Your Sky?", font=HEADER_FONT, fg="#DEAFEE", bg="black")
        header.pack(pady=(24, 20))

        input_frame = tk.Frame(self.root, bg="black")
        input_frame.pack()
        tk.Label(input_frame, text="Enter city:", font=NORMAL_FONT, fg="#fff", bg="black").grid(row=0, column=0, padx=(0, 3))

        self.city_entry = tk.Entry(input_frame, font=NORMAL_FONT, width=20)
        self.city_entry.grid(row=0, column=1, padx=(0, 8))

        # 🔥 Bind Enter key to get_weather
        self.city_entry.bind("<Return>", lambda event: self.get_weather())

        get_btn = tk.Button(input_frame, text="Get Weather", font=NORMAL_FONT, command=self.get_weather)
        get_btn.grid(row=0, column=2)

        self.unit_btn = tk.Button(
            input_frame, text="Show °F", font=NORMAL_FONT,
            fg="#222", bg="#ffe047", activeforeground="#fff", activebackground="#ffb200",
            bd=1, relief="solid", width=8,
            command=self.toggle_unit
        )
        self.unit_btn.grid(row=0, column=3, padx=(8, 0))

        self.weather_info_frame = tk.Frame(self.root, bg="black")
        self.weather_info_frame.pack(pady=(16, 2))

        self.tabs = ttk.Notebook(self.root)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', background=TAB_BG, foreground=TAB_FG, font=NORMAL_FONT, padding=[8, 4])
        style.map('TNotebook.Tab', background=[('selected', ACTIVE_TAB_BG)], foreground=[('selected', ACTIVE_TAB_FG)])

        # Remove focus highlight from tabs
        style.layout("TNotebook.Tab", [
            ('Notebook.tab', {'sticky': 'nswe', 'children': [
                ('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [
                    ('Notebook.label', {'side': 'top', 'sticky': ''})
                ]})
            ]})
        ])

        self.forecast_frame = tk.Frame(self.tabs, bg="black")
        self.tabs.add(self.forecast_frame, text="Forecast")
        self.history_frame = tk.Frame(self.tabs, bg="black")
        self.tabs.add(self.history_frame, text="History")
        self.stats_frame = tk.Frame(self.tabs, bg="black")
        self.tabs.add(self.stats_frame, text="History Statistics")
        self.tabs.pack(fill="both", expand=True, pady=(8, 0))

    def create_forecast_tab(self):
        self.forecast_inner = tk.Frame(self.forecast_frame, bg="black")
        self.forecast_inner.pack(fill="both", expand=True, padx=0, pady=0)
        self.forecast_blocks = []
        self.forecast_header = tk.Label(
            self.forecast_inner,
            text="",
            font=("Helvetica Neue", 34, "bold"),
            fg="#ffe047",
            bg="black",
            anchor="center",
            justify="center"
        )
        self.forecast_header.pack(pady=(20, 18))
        self.block_frame = tk.Frame(self.forecast_inner, bg="black")
        self.block_frame.pack(fill="x", expand=True)
        self.forecast_footer = tk.Label(self.forecast_frame, text=FORECAST_FOOTER, font=SMALL_FONT, fg="#fff", bg="black")
        self.forecast_footer.pack(side="bottom", pady=(0, 12))

    def toggle_unit(self):
        self.temp_unit = "F" if self.temp_unit == "C" else "C"
        self.unit_btn.config(text=f"Show °{'C' if self.temp_unit == 'F' else 'F'}")
        city = self.city_entry.get().strip()
        self.refresh_display(city, self.last_weather if hasattr(self, "last_weather") else None)
        self.refresh_forecast(city)
        self.refresh_history()
        self.refresh_stats()

    def convert_temp(self, temp_c):
        return temp_c if self.temp_unit == "C" else temp_c * 9/5 + 32

    def get_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name.")
            return
        try:
            weather = fetch_weather(city)
            self.last_weather = weather
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch weather: {e}")
            return

        self.db.insert_weather(
            city=title_case(city),
            temp=weather["temp"],
            feels_like=weather["feels_like"],
            weather=title_case(weather["weather"]),
            humidity=weather["humidity"],
            pressure=weather["pressure"],
            visibility=weather["visibility"],
            wind=weather["wind"],
            sea_level=weather["sea_level"],
            grnd_level=weather["grnd_level"],
            sunrise=weather["sunrise"],
            sunset=weather["sunset"]
        )

        self.refresh_display(city, weather)
        self.refresh_history()
        self.refresh_stats()
        self.refresh_forecast(city)

    def refresh_display(self, city, weather):
        # Clear previous content
        for widget in self.weather_info_frame.winfo_children():
            widget.destroy()

        if not weather:
            return

        temp = self.convert_temp(weather['temp'])
        feels_like = self.convert_temp(weather["feels_like"])
        t_unit = "°C" if self.temp_unit == "C" else "°F"

        visibility = weather.get("visibility", "N/A")
        if visibility != "N/A" and isinstance(visibility, (int, float)):
            visibility_km = round(visibility / 1000, 1)
        else:
            visibility_km = "N/A"

        # Outer "card"
        card = tk.Frame(self.weather_info_frame, bg="#222", bd=3, relief="ridge", padx=20, pady=14)
        card.pack(pady=12)

        # City name
        tk.Label(card, text=title_case(city), font=("Helvetica Neue", 20, "bold"), fg="#ffe047", bg="#222").pack()

        # Temp line
        tk.Label(card, text=f"{temp:.1f}{t_unit} (Feels like: {feels_like:.1f}{t_unit})", font=("Helvetica Neue", 16), fg="#fff", bg="#222").pack()

        # Condition
        tk.Label(card, text=f"🌤️ {title_case(weather['weather'])}", font=("Helvetica Neue", 16), fg="#fff", bg="#222").pack(pady=(0, 6))

        # Divider
        tk.Label(card, text="──────────────", font=("Helvetica Neue", 12), fg="#555", bg="#222").pack(pady=4)

        # First metrics row
        row1 = tk.Frame(card, bg="#222")
        row1.pack(pady=2)
        tk.Label(row1, text=f"💧 Humidity: {weather['humidity']}%", font=("Helvetica Neue", 14), fg="#bfffa5", bg="#222").grid(row=0, column=0, padx=14, sticky="w")
        tk.Label(row1, text=f"🌬️ Wind: {weather['wind']}", font=("Helvetica Neue", 14), fg="#43fad8", bg="#222").grid(row=0, column=1, padx=14, sticky="w")
        tk.Label(row1, text=f"👁️ Visibility: {visibility_km} km", font=("Helvetica Neue", 14), fg="#a1e3ff", bg="#222").grid(row=0, column=2, padx=14, sticky="w")

        # Second metrics row
        row2 = tk.Frame(card, bg="#222")
        row2.pack(pady=2)
        tk.Label(row2, text=f"📄 Pressure: {weather['pressure']} hPa", font=("Helvetica Neue", 14), fg="#ffd580", bg="#222").grid(row=0, column=0, padx=14, sticky="w")
        tk.Label(row2, text=f"🌅 Sunrise: {weather['sunrise']}", font=("Helvetica Neue", 14), fg="#ffacac", bg="#222").grid(row=0, column=1, padx=14, sticky="w")
        tk.Label(row2, text=f"🌇 Sunset: {weather['sunset']}", font=("Helvetica Neue", 14), fg="#ffacac", bg="#222").grid(row=0, column=2, padx=14, sticky="w")

    def refresh_forecast(self, city=None):
        for widget in self.block_frame.winfo_children():
            widget.destroy()
        self.forecast_blocks.clear()
        city = city or self.city_entry.get().strip()
        if not city:
            self.forecast_header.config(text="Enter a city to view forecast.")
            self.root.update_idletasks()
            return
        try:
            days = fetch_5day_forecast(city)
        except Exception as e:
            self.forecast_header.config(text=f"Could not fetch forecast: {e}")
            return
        self.forecast_header.config(
            text=f"5-Day Forecast for {title_case(city)}:",
            anchor="center", justify="center", font=("Helvetica Neue", 34, "bold")
        )
        for i, day in enumerate(days):
            dayblock = self._make_forecast_block(self.block_frame, day)
            dayblock.grid(row=0, column=i, sticky="nsew", padx=28, ipadx=14, ipady=80)
            self.block_frame.columnconfigure(i, weight=1)
            self.forecast_blocks.append(dayblock)
        self.root.update_idletasks()

    def _make_forecast_block(self, parent, day):
        color = "#ffe047"
        weather_main = day['weather'].lower()
        if "clear" in weather_main:
            icon = "☀️"
        elif "cloud" in weather_main:
            icon = "⛅"
        elif "rain" in weather_main:
            icon = "🌧️"
        elif "storm" in weather_main or "thunder" in weather_main:
            icon = "⛈️"
        elif "snow" in weather_main:
            icon = "❄️"
        elif "haze" in weather_main:
            icon = "🌫️"
        else:
            icon = "🌡️"

        temp_min = self.convert_temp(day['temp_min'])
        temp_max = self.convert_temp(day['temp_max'])
        t_unit = "°C" if self.temp_unit == "C" else "°F"

        f = tk.Frame(parent, bg="#222", bd=3, relief="ridge", padx=14, pady=12)

        content = tk.Frame(f, bg="#222")
        content.pack(expand=True)

        tk.Label(content, text=day['date'], font=("Helvetica Neue", 16, "bold"), fg=color, bg="#222").pack(pady=(2, 0), anchor="center")
        tk.Label(content, text=f"{icon} {title_case(day['weather'])}", font=("Helvetica Neue", 16), fg="#fff", bg="#222").pack(anchor="center")
        tk.Label(content, text="----------------", font=("Helvetica Neue", 12), fg="#555", bg="#222").pack(pady=(4, 4), anchor="center")
        tk.Label(content, text=f"{temp_min:.1f}{t_unit} - {temp_max:.1f}{t_unit}", font=("Helvetica Neue", 16, "bold"), fg="#ffe047", bg="#222").pack(pady=(0, 8), anchor="center")
        tk.Label(content, text=f"Humidity: {day['humidity']}%", font=("Helvetica Neue", 15), fg="#bfffa5", bg="#222").pack(anchor="center")
        tk.Label(content, text=f"Wind: {day.get('wind', 'N/A')}", font=("Helvetica Neue", 15), fg="#43fad8", bg="#222").pack(anchor="center")
        tk.Label(content, text=f"Visibility: {day.get('visibility', 'N/A')} km (max 10 km)", font=("Helvetica Neue", 15), fg="#a1e3ff", bg="#222").pack(anchor="center")

        return f

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
            else:
                self.tree.column(col, anchor="center", width=120)
            self.tree.heading(col, text=display_text, command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False))

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

    def create_stats_tab(self):
        self.stats_frame_inner = tk.Frame(self.stats_frame, bg="black")
        self.stats_frame_inner.pack(expand=True, fill="both", pady=(14, 0))
        self.stats_footer = tk.Label(self.stats_frame, text=STATS_FOOTER, font=SMALL_FONT, fg="#fff", bg="black")
        self.stats_footer.pack(side="bottom", pady=(0, 12))

    def refresh_stats(self):
        for w in self.stats_frame_inner.winfo_children():
            w.destroy()

        header_label = tk.Label(self.stats_frame_inner, text="SQL Statistics of Weather History", font=HEADER_FONT, fg="#ffe047", bg="black")
        header_label.pack(pady=(10, 20))

        stats = self.db.get_stats()
        if not stats:
            tk.Label(self.stats_frame_inner, text="No statistics available yet. Search for a city first!", font=NORMAL_FONT, fg="#fff", bg="black").pack(pady=24)
            return

        hottest_temp = stats['hottest_raw']
        coldest_temp = stats['coldest_raw']
        if self.temp_unit == "F":
            hottest_temp = hottest_temp * 9 / 5 + 32
            coldest_temp = coldest_temp * 9 / 5 + 32

        summary_grid = tk.Frame(self.stats_frame_inner, bg="black")
        summary_grid.pack(anchor="center", pady=(4, 18))

        summary_rows = [
            ("🔥 Hottest", f"{hottest_temp:.2f}°{self.temp_unit}", stats['hottest_city'], stats['hottest_time']),
            ("❄️ Coldest", f"{coldest_temp:.2f}°{self.temp_unit}", stats['coldest_city'], stats['coldest_time']),
            ("⛅ Strongest Wind", stats['strongest_wind'], stats['strongest_wind_city'], stats['strongest_wind_time']),
            ("💧 Most Humid", stats['most_humid'], stats['most_humid_city'], stats['most_humid_time']),
        ]

        for i, (label, value, city, time) in enumerate(summary_rows):
            tk.Label(summary_grid, text=label, font=NORMAL_FONT, fg="#fff", bg="black", anchor="w", width=16).grid(row=i, column=0, sticky="w", padx=(12, 8), pady=2)
            tk.Label(summary_grid, text=value, font=NORMAL_FONT, fg="#ffe047", bg="black", anchor="w", width=10).grid(row=i, column=1, sticky="w", padx=8, pady=2)
            tk.Label(summary_grid, text=city, font=NORMAL_FONT, fg="#43fad8", bg="black", anchor="w", width=18).grid(row=i, column=2, sticky="w", padx=8, pady=2)
            tk.Label(summary_grid, text=time, font=NORMAL_FONT, fg="#ccc", bg="black", anchor="w", width=20).grid(row=i, column=3, sticky="w", padx=8, pady=2)

        avg_temp = stats['avg_temp']
        t_unit = "°C"
        if self.temp_unit == "F":
            avg_temp = avg_temp * 9 / 5 + 32
            t_unit = "°F"
        avg_temp_text = f"{avg_temp:.1f}{t_unit}"

        grid = tk.Frame(self.stats_frame_inner, bg="black")
        grid.pack(anchor="n", pady=(4, 0))

        rows = [
            ("Total logs:", stats['log_count']),
            ("Most searched city:", stats['most_searched']),
            ("Average temperature:", avg_temp_text),
            ("Average humidity:", f"{stats['avg_humidity']}%"),
            ("Average pressure:", f"{stats['avg_pressure']} hPa"),
            ("Average wind speed:", f"{stats['avg_wind']:.2f} m/s"),
        ]
        rows.extend([
            ("Average sea level pressure:", f"{stats['avg_sea_level']} hPa"),
            ("Highest sea level:", f"{stats['highest_sea_value']} in {stats['highest_sea_city']} at {stats['highest_sea_time']}"),
            ("Average ground level pressure:", f"{stats['avg_ground_level']} hPa"),
            ("Lowest ground level:", f"{stats['lowest_ground_value']} in {stats['lowest_ground_city']} at {stats['lowest_ground_time']}"),
            ("Earliest sunrise:", f"{stats['earliest_sunrise_time']} in {stats['earliest_sunrise_city']}"),
            ("Latest sunset:", f"{stats['latest_sunset_time']} in {stats['latest_sunset_city']}"),
        ])

        for i, (k, v) in enumerate(rows):
            tk.Label(grid, text=k, font=NORMAL_FONT, fg="#ccc", bg="black", anchor="e").grid(row=i, column=0, sticky="e", pady=1, padx=(24, 8))
            tk.Label(grid, text=v, font=NORMAL_FONT, fg="#fff", bg="black", anchor="w").grid(row=i, column=1, sticky="w", pady=1)

    def on_tab_change(self, event):
        idx = self.tabs.index(self.tabs.select())
        if idx == 0:
            self.refresh_forecast(self.city_entry.get().strip())
        elif idx == 1:
            self.refresh_history()
        elif idx == 2:
            self.refresh_stats()

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()