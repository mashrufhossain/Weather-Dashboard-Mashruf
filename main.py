import tkinter as tk
from tkinter import ttk, messagebox
from api import fetch_weather, fetch_5day_forecast
from db import WeatherDB
import os

HEADER_FONT = ("Helvetica Neue", 32, "bold")
NORMAL_FONT = ("Helvetica Neue", 16)
SMALL_FONT = ("Helvetica Neue", 14)

TAB_BG = "#222"  # darker so yellow stands out
TAB_FG = "#fff"
ACTIVE_TAB_BG = "#0ff3c3"
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
        self.temp_unit = "C"  # default: Celsius

        self.create_widgets()
        self.create_history_tab()
        self.create_stats_tab()
        self.create_forecast_tab()
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.refresh_forecast()

    def create_widgets(self):
        header = tk.Label(self.root, text="What's in Your Sky?", font=HEADER_FONT, fg="#7360ac", bg="black")
        header.pack(pady=(24, 5))

        input_frame = tk.Frame(self.root, bg="black")
        input_frame.pack()
        tk.Label(input_frame, text="Enter city:", font=NORMAL_FONT, fg="#fff", bg="black").grid(row=0, column=0, padx=(0, 3))
        self.city_entry = tk.Entry(input_frame, font=NORMAL_FONT, width=20)
        self.city_entry.grid(row=0, column=1, padx=(0, 8))
        get_btn = tk.Button(input_frame, text="Get Weather", font=NORMAL_FONT, command=self.get_weather)
        get_btn.grid(row=0, column=2)

        self.unit_btn = tk.Button(
            input_frame, text="Show °F", font=NORMAL_FONT,
            fg="#222", bg="#ffe047", activeforeground="#fff", activebackground="#ffb200",
            bd=1, relief="solid", width=8,
            command=self.toggle_unit)
        self.unit_btn.grid(row=0, column=3, padx=(8, 0))

        self.weather_display = tk.Label(self.root, text="", font=NORMAL_FONT, fg="#fff", bg="black", justify="left")
        self.weather_display.pack(pady=(16, 2))

        # Tabs (Forecast, History, History Stats)
        self.tabs = ttk.Notebook(self.root)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', background=TAB_BG, foreground=TAB_FG, font=NORMAL_FONT, padding=[8, 4])
        style.map('TNotebook.Tab', background=[('selected', ACTIVE_TAB_BG)], foreground=[('selected', ACTIVE_TAB_FG)])

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
        self.forecast_header = tk.Label(self.forecast_inner, text="", font=NORMAL_FONT, fg="#ffe047", bg="black")
        self.forecast_header.pack(pady=(18, 14))
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
            self.last_weather = weather  # Save for unit switch
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch weather: {e}")
            return
        # Save to DB
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
        # Refresh all displays
        self.refresh_display(city, weather)
        self.refresh_history()
        self.refresh_stats()
        self.refresh_forecast(city)

    def refresh_display(self, city, weather):
        if not weather:
            self.weather_display.config(text="")
            return

        temp = self.convert_temp(weather['temp'])
        feels_like = self.convert_temp(weather["feels_like"])
        t_unit = "°C" if self.temp_unit == "C" else "°F"

        visibility = weather.get("visibility", "N/A")
        wind_gust = weather.get("wind_gust", "N/A")
        sea_level = weather.get("sea_level", "N/A")
        grnd_level = weather.get("grnd_level", "N/A")
        sunrise = weather.get("sunrise", "N/A")
        sunset = weather.get("sunset", "N/A")

        # Convert visibility to km if numeric
        if visibility != "N/A" and isinstance(visibility, (int, float)):
            visibility_km = round(visibility / 1000, 1)
        else:
            visibility_km = "N/A"

        info = (
            f"{title_case(city)}\n"
            "-----------------------------\n"
            f"Temp: {temp:.2f}{t_unit}\n"
            f"Feels like: {feels_like:.2f}{t_unit}\n"
            f"Weather: {title_case(weather['weather'])}\n"
            f"Humidity: {weather['humidity']}%\n"
            f"Pressure: {weather['pressure']} hPa\n"
            f"Visibility: {visibility_km} km\n"
            f"Wind: {weather['wind']}\n"
            f"Sea level: {sea_level} hPa\n"
            f"Ground level: {grnd_level} hPa\n"
            f"Sunrise: {sunrise}\n"
            f"Sunset: {sunset}"
        )

        self.weather_display.config(text=info)

    def refresh_forecast(self, city=None):
        # Clear previous blocks
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
            font=HEADER_FONT,
            anchor="center", justify="center"
        )
        # Responsive block layout
        for i, day in enumerate(days):
            dayblock = self._make_forecast_block(self.block_frame, day)
            dayblock.grid(row=0, column=i, sticky="nsew", padx=28, ipadx=14, ipady=20)
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

        f = tk.Frame(parent, bg="#222", bd=3, relief="ridge", padx=14, pady=80)

        tk.Label(f, text=day['date'], font=("Helvetica Neue", 18, "bold"), fg=color, bg="#222").pack(pady=(4, 2))
        tk.Label(f, text=f"{icon} {title_case(day['weather'])}", font=("Helvetica Neue", 18), fg="#fff", bg="#222").pack()
        tk.Label(f, text=f"{temp_min:.1f}{t_unit} - {temp_max:.1f}{t_unit}", font=("Helvetica Neue", 20, "bold"), fg="#ffe047", bg="#222").pack(pady=(8, 4))
        tk.Label(f, text=f"Humidity: {day['humidity']}%", font=("Helvetica Neue", 16), fg="#bfffa5", bg="#222").pack()
        tk.Label(f, text=f"Wind: {day.get('wind', 'N/A')}", font=("Helvetica Neue", 15), fg="#43fad8", bg="#222").pack()
        tk.Label(f, text=f"Visibility: {day.get('visibility', 'N/A')} km", font=("Helvetica Neue", 15), fg="#a1e3ff", bg="#222").pack()
        return f

    ### -------- HISTORY TAB -------- ###
    def treeview_sort_column(self, tv, col, reverse):
        # Get values and row IDs
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        try:
            l.sort(
                key=lambda t: float(t[0].split()[0].replace("°C", "").replace("°F", "")
                                .replace("%", "").replace("m/s", "").replace("hPa", "")),
                reverse=reverse
            )
        except ValueError:
            l.sort(reverse=reverse)

        # Reorder rows
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # Reset all headers to base text (no arrow)
        for c in tv["columns"]:
            base_text = c.replace("_", " ").title()
            tv.heading(c, text=base_text, command=lambda _col=c: self.treeview_sort_column(tv, _col, False))

        # Add arrow to active column
        arrow = " ▲" if not reverse else " ▼"
        tv.heading(col, text=col.replace("_", " ").title() + arrow,
                command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def create_history_tab(self):
        # Treeview table (always aligned)
        columns = ("timestamp", "city", "temp", "feels_like", "weather", "humidity", "pressure",
           "visibility", "wind", "sea_level", "grnd_level", "sunrise", "sunset")
        self.tree = ttk.Treeview(self.history_frame, columns=columns, show="headings", height=18)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(14, 0))
        
        # Create style
        style = ttk.Style()
        style.theme_use("default")
        
        # Header style
        style.configure("Treeview.Heading", 
            font=("Helvetica Neue", 14, "bold"), 
            background="#444",     # Lighter header background
            foreground="#2ECBB4"      # White header text
        )
        
        # Row style
        style.configure("Treeview", 
            font=NORMAL_FONT, 
            rowheight=26, 
            background="black", 
            fieldbackground="black", 
            foreground="white"
        )

        style.map("Treeview",
            background=[('selected', '#555')],
            foreground=[('selected', '#fff')]
        )
        
        self.tree.tag_configure('centered', anchor='center')
        
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title(), command=lambda _col=col: self.treeview_sort_column(self.tree, _col, False))
            if col == "timestamp":
                self.tree.column(col, anchor="center", width=180)  # wider for timestamp
            elif col == "weather":
                self.tree.column(col, anchor="center", width=150)  # slightly wider for weather
            else:
                self.tree.column(col, anchor="center", width=110)

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

    ### -------- HISTORY STATS TAB -------- ###
    def create_stats_tab(self):
        self.stats_frame_inner = tk.Frame(self.stats_frame, bg="black")
        self.stats_frame_inner.pack(expand=True, fill="both", pady=(14, 0))
        self.stats_rows = []
        self.stats_footer = tk.Label(self.stats_frame, text=STATS_FOOTER, font=SMALL_FONT, fg="#fff", bg="black")
        self.stats_footer.pack(side="bottom", pady=(0, 12))

    def refresh_stats(self):
        for w in self.stats_frame_inner.winfo_children():
            w.destroy()

        header_label = tk.Label(self.stats_frame_inner, text="SQL Statistics of Weather History", font=HEADER_FONT, fg="#7360ac", bg="black")
        header_label.pack(pady=(10, 20))

        # Get stats
        stats = self.db.get_stats()
        if not stats:
            tk.Label(self.stats_frame_inner, text="No statistics available yet. Search for a city first!", font=NORMAL_FONT, fg="#fff", bg="black").pack(pady=24)
            return

        # Hottest
        if stats['hottest_raw'] is not None:
            hottest_temp = stats['hottest_raw']
            if self.temp_unit == "F":
                hottest_temp = hottest_temp * 9 / 5 + 32
        else:
            hottest_temp = 0

        # Coldest
        if stats['coldest_raw'] is not None:
            coldest_temp = stats['coldest_raw']
            if self.temp_unit == "F":
                coldest_temp = coldest_temp * 9 / 5 + 32
        else:
            coldest_temp = 0

        # Prepare wind value with unit
        wind_value = stats['strongest_wind'].split(",")[0]

        # Create summary grid
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

        # Average temp formatting
        avg_temp = stats['avg_temp']
        t_unit = "°C"
        if self.temp_unit == "F":
            avg_temp = avg_temp * 9 / 5 + 32
            t_unit = "°F"
        avg_temp_text = f"{avg_temp:.1f}{t_unit}"

        # Detailed stats grid
        grid = tk.Frame(self.stats_frame_inner, bg="black")
        grid.pack(anchor="center", pady=(4, 0))

        rows = [
            ("Total logs:", stats['log_count']),
            ("Most searched city:", stats['most_searched']),
            ("Average temperature:", avg_temp_text),
            ("Average humidity:", f"{stats['avg_humidity']}%"),
            ("Average pressure:", f"{stats['avg_pressure']} hPa"),
            ("Average wind speed:", f"{stats['avg_wind']:.2f} m/s"),
        ]

        for i, (k, v) in enumerate(rows):
            tk.Label(grid, text=k, font=NORMAL_FONT, fg="#ccc", bg="black", anchor="e", width=22).grid(row=i, column=0, sticky="e", pady=1, padx=(24, 8))
            tk.Label(grid, text=v, font=NORMAL_FONT, fg="#fff", bg="black", anchor="w", width=24).grid(row=i, column=1, sticky="w", pady=1)



    ### -------- TAB SWITCH -------- ###
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
