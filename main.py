import tkinter as tk
from tkinter import ttk, messagebox
from api import fetch_weather, fetch_5day_forecast
from db import WeatherDB
import os

HEADER_FONT = ("Helvetica Neue", 18, "bold")
NORMAL_FONT = ("Helvetica Neue", 12)
SMALL_FONT = ("Helvetica Neue", 10)
TITLE_COLOR = "#00e0ff"

TAB_BG = "#222"  # darker so yellow stands out
TAB_FG = "#fff"
ACTIVE_TAB_BG = "#0ff3c3"
ACTIVE_TAB_FG = "#111"
HISTORY_FOOTER = "This tab shows all your previous weather history entries."
STATS_FOOTER = "This tab summarizes your weather history with key statistics and records, calculated using SQL."
FORECAST_FOOTER = "This tab displays predictive forecasts for the city you entered."

def title_case(s):
    return ' '.join([w.capitalize() for w in s.split()])

class WeatherApp:
    def __init__(self, root):
        self.root = root
        root.title("Weather Dashboard")
        root.configure(bg="black")
        root.geometry("1100x800")
        root.minsize(900, 600)

        self.db = WeatherDB(os.path.join("data", "weather.db"))
        self.temp_unit = "C"  # default: Celsius

        self.create_widgets()
        self.create_forecast_tab()
        self.create_history_tab()
        self.create_stats_tab()
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.refresh_forecast()

    def create_widgets(self):
        header = tk.Label(self.root, text="Welcome to the Weather Dashboard!", font=HEADER_FONT, fg="#fff", bg="black")
        header.pack(pady=(24, 5))

        input_frame = tk.Frame(self.root, bg="black")
        input_frame.pack()
        tk.Label(input_frame, text="Enter city:", font=NORMAL_FONT, fg="#fff", bg="black").grid(row=0, column=0, padx=(0, 3))
        self.city_entry = tk.Entry(input_frame, font=NORMAL_FONT, width=20)
        self.city_entry.grid(row=0, column=1, padx=(0, 8))
        get_btn = tk.Button(input_frame, text="Get Weather", font=NORMAL_FONT, command=self.get_weather)
        get_btn.grid(row=0, column=2)

        # Unit toggle
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
            weather=title_case(weather["weather"]),
            humidity=weather["humidity"],
            pressure=weather["pressure"],
            wind=weather["wind"]
        )
        self.refresh_display(city, weather)
        self.refresh_history()
        self.refresh_stats()
        self.refresh_forecast(city)

    def refresh_display(self, city, weather):
        if not weather:
            self.weather_display.config(text="")
            return
        temp = self.convert_temp(weather['temp'])
        t_unit = "°C" if self.temp_unit == "C" else "°F"
        info = (
            f"{title_case(city)}\n"
            "-----------------------------\n"
            f"Temp:   {temp:.2f}{t_unit}\n"
            f"Weather: {title_case(weather['weather'])}\n"
            f"Humidity: {weather['humidity']}%\n"
            f"Pressure: {weather['pressure']} hPa\n"
            f"Wind:   {weather['wind']}"
        )
        self.weather_display.config(text=info)

    ### -------- FORECAST TAB -------- ###
    def create_forecast_tab(self):
        self.forecast_inner = tk.Frame(self.forecast_frame, bg="black")
        self.forecast_inner.pack(fill="both", expand=True, padx=0, pady=0)
        self.forecast_blocks = []
        self.forecast_header = tk.Label(self.forecast_inner, text="", font=NORMAL_FONT, fg="#ffe047", bg="black")
        self.forecast_header.pack(pady=(18, 14))
        # Horizontal container for forecast cards
        self.block_frame = tk.Frame(self.forecast_inner, bg="black")
        self.block_frame.pack(fill="x", expand=True)
        # Footer (always visible)
        self.forecast_footer = tk.Label(self.forecast_frame, text=FORECAST_FOOTER, font=SMALL_FONT, fg="#fff", bg="black")
        self.forecast_footer.pack(side="bottom", pady=(0, 12))

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
            anchor="center", justify="center"
        )
        # Responsive block layout
        for i, day in enumerate(days):
            dayblock = self._make_forecast_block(self.block_frame, day)
            dayblock.grid(row=0, column=i, sticky="nsew", padx=28, ipadx=6, ipady=12)
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
        f = tk.Frame(parent, bg="#222", bd=2, relief="ridge", padx=10, pady=9)
        tk.Label(f, text=day['date'], font=("Helvetica Neue", 12, "bold"), fg=color, bg="#222").pack(pady=(2, 0))
        tk.Label(f, text=f"{icon} {title_case(day['weather'])}", font=("Helvetica Neue", 12), fg="#fff", bg="#222").pack()
        tk.Label(f, text=f"{temp_min:.1f}{t_unit} - {temp_max:.1f}{t_unit}", font=("Helvetica Neue", 12, "bold"), fg="#ffe047", bg="#222").pack(pady=(6, 0))
        tk.Label(f, text=f"Humidity: {day['humidity']}%", font=("Helvetica Neue", 11), fg="#bfffa5", bg="#222").pack()
        return f

    ### -------- HISTORY TAB -------- ###
    def create_history_tab(self):
        # Treeview table (always aligned)
        columns = ("timestamp", "city", "temp", "weather", "humidity", "pressure", "wind")
        self.tree = ttk.Treeview(self.history_frame, columns=columns, show="headings", height=18)
        self.tree.pack(fill="both", expand=True, padx=12, pady=(14, 0))
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica Neue", 11, "bold"), background="#222")
        style.configure("Treeview", font=NORMAL_FONT, rowheight=26, background="black", fieldbackground="black", foreground="white")
        self.tree.tag_configure('centered', anchor='center')
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, anchor="center", width=110)
        self.history_footer = tk.Label(self.history_frame, text=HISTORY_FOOTER, font=SMALL_FONT, fg="#fff", bg="black")
        self.history_footer.pack(side="bottom", pady=(0, 12))

    def refresh_history(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        entries = self.db.get_all_history()
        if not entries:
            self.tree.insert("", "end", values=["No history found."] + [""] * 6)
            return
        for entry in entries:
            temp = self.convert_temp(entry[2])
            t_unit = "°C" if self.temp_unit == "C" else "°F"
            row = (
                entry[0], entry[1], f"{temp:.2f}{t_unit}", entry[3],
                entry[4], entry[5], entry[6]
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
        stats = self.db.get_stats()
        if not stats:
            tk.Label(self.stats_frame_inner, text="No statistics available yet. Search for a city first!", font=NORMAL_FONT, fg="#fff", bg="black").pack(pady=24)
            return
        
        # Hottest
        if stats['hottest_raw'] is not None:
            hottest_temp = stats['hottest_raw']
            if self.temp_unit == "F":
                hottest_temp = hottest_temp * 9 / 5 + 32
            hottest_str = f"{hottest_temp:.2f}°{self.temp_unit} in {stats['hottest_city']} ({stats['hottest_time']})"
        else:
            hottest_str = "N/A"

        # Coldest
        if stats['coldest_raw'] is not None:
            coldest_temp = stats['coldest_raw']
            if self.temp_unit == "F":
                coldest_temp = coldest_temp * 9 / 5 + 32
            coldest_str = f"{coldest_temp:.2f}°{self.temp_unit} in {stats['coldest_city']} ({stats['coldest_time']})"
        else:
            coldest_str = "N/A"

        # Top: icons, centered
        iconrow = tk.Frame(self.stats_frame_inner, bg="black")
        iconrow.pack(anchor="center", pady=(0, 16))
        tk.Label(iconrow, text=f"🔥 Hottest: {hottest_str}", fg="#ffe047", font=NORMAL_FONT, bg="black").pack(side="left", padx=18)
        tk.Label(iconrow, text=f"❄️ Coldest: {coldest_str}", fg="#bfffa5", font=NORMAL_FONT, bg="black").pack(side="left", padx=18)
        tk.Label(iconrow, text=f"⛅ Strongest Wind: {stats['strongest_wind']}", fg="#79ff6b", font=NORMAL_FONT, bg="black").pack(side="left", padx=18)
        tk.Label(iconrow, text=f"💧 Most Humid: {stats['most_humid']}", fg="#43c0fa", font=NORMAL_FONT, bg="black").pack(side="left", padx=18)

        # Stats, centered vertically
        grid = tk.Frame(self.stats_frame_inner, bg="black")
        grid.pack(anchor="center", pady=(4, 0))
        avg_temp = stats['avg_temp']
        t_unit = "°C"
        if self.temp_unit == "F":
            avg_temp = avg_temp * 9 / 5 + 32
            t_unit = "°F"
        avg_temp_text = f"{avg_temp:.1f}{t_unit}"

        rows = [
            ("Total logs:", stats['log_count'], "#ffe047"),
            ("Most searched city:", stats['most_searched'], "#00e0ff"),
            ("Average temperature:", avg_temp_text, "#ffe047"),
            ("Average humidity:", f"{stats['avg_humidity']}%", "#ffe047"),
            ("Average pressure:", f"{stats['avg_pressure']} hPa", "#ffe047"),
            ("Average wind speed:", f"{stats['avg_wind']:.2f} m/s", "#79ff6b"),
        ]
        for i, (k, v, color) in enumerate(rows):
            tk.Label(grid, text=k, font=NORMAL_FONT, fg=color, bg="black", anchor="e", width=20).grid(row=i, column=0, sticky="e", pady=1, padx=(24, 8))
            tk.Label(grid, text=v, font=NORMAL_FONT, fg="#fff", bg="black", anchor="w", width=32).grid(row=i, column=1, sticky="w", pady=1)

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
