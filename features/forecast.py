import tkinter as tk
from styles import SMALL_FONT
from constants import FORECAST_FOOTER
from api import fetch_5day_forecast_by_coords
from utils import title_case


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


def refresh_forecast(self, city=None):
    for widget in self.block_frame.winfo_children():
        widget.destroy()
    self.forecast_blocks.clear()
    city = city or self.city_entry.get().strip()
    if not city:
        self.forecast_header.config(text="Enter a city to view forecast.")
        self.root.update_idletasks()
        return
    city_disp = city or self.city_entry.get().strip()
    if not city_disp or city_disp not in self.suggestion_coords:
        self.forecast_header.config(text="Enter a city to view forecast.")
        self.root.update_idletasks()
        return

    lat, lon = self.suggestion_coords[city_disp]

    try:
        days = fetch_5day_forecast_by_coords(lat, lon)
    except Exception as e:
        self.forecast_header.config(text=f"Could not fetch forecast: {e}")
        return

    self.forecast_header.config(
        text=f"5-Day Forecast for {title_case(city)}:",
        anchor="center", justify="center", font=("Helvetica Neue", 34, "bold")
    )
    for i, day in enumerate(days):
        dayblock = _make_forecast_block(self.block_frame, day, self.convert_temp, self.temp_unit)
        dayblock.grid(row=0, column=i, sticky="nsew", padx=28, ipadx=14, ipady=80)
        self.block_frame.columnconfigure(i, weight=1)
        self.forecast_blocks.append(dayblock)


def _make_forecast_block(parent, day, convert_temp_func, temp_unit):
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

    temp_min = convert_temp_func(day['temp_min'])
    temp_max = convert_temp_func(day['temp_max'])
    t_unit_symbol = "°C" if temp_unit == "C" else "°F"

    f = tk.Frame(parent, bg="#222", bd=3, relief="ridge", padx=14, pady=12)
    content = tk.Frame(f, bg="#222")
    content.pack(expand=True)

    tk.Label(content, text=day['date'], font=("Helvetica Neue", 16, "bold"), fg=color, bg="#222").pack(pady=(2, 0), anchor="center")
    tk.Label(content, text=f"{icon} {title_case(day['weather'])}", font=("Helvetica Neue", 16), fg="#fff", bg="#222").pack(anchor="center")
    tk.Label(content, text="----------------", font=("Helvetica Neue", 12), fg="#555", bg="#222").pack(pady=(4, 4), anchor="center")
    tk.Label(content, text=f"{temp_min:.1f}{t_unit_symbol} - {temp_max:.1f}{t_unit_symbol}", font=("Helvetica Neue", 16, "bold"), fg="#ffe047", bg="#222").pack(pady=(0, 8), anchor="center")
    tk.Label(content, text=f"Humidity: {day['humidity']}%", font=("Helvetica Neue", 15), fg="#bfffa5", bg="#222").pack(anchor="center")
    tk.Label(content, text=f"Wind: {day.get('wind', 'N/A')}", font=("Helvetica Neue", 15), fg="#43fad8", bg="#222").pack(anchor="center")
    tk.Label(content, text=f"Visibility: {day.get('visibility', 'N/A')} km (max 10 km)", font=("Helvetica Neue", 15), fg="#a1e3ff", bg="#222").pack(anchor="center")

    return f