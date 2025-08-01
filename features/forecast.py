"""
features/forecast.py

Forecast UI module for Weather Dashboard.

Defines functions to:
- create_forecast_tab(self): Set up the forecast tab layout, including header, content blocks, and footer.
- refresh_forecast(self, city=None): Clear old forecast, validate city input, fetch new forecast data, and populate blocks.
- make_forecast_block(parent, day, convert_temp_func, temp_unit): Build and return a styled frame for a single day's forecast.
"""

import tkinter as tk                             # Tkinter for GUI widgets
import tkinter.messagebox as messagebox          # Show user alerts
from styles import SMALL_FONT                    # Consistent small font definition
from constants import FORECAST_FOOTER            # Footer text for forecast tab
from api import fetch_5day_forecast_by_coords    # Function to retrieve 5-day forecast data
from api import APIError                         # Class for handling API errors
from utils import title_case                     # Helper to title-case weather descriptions
import threading                                 # Run background tasks
import logging                                   # Logging for developer error tracking


def create_forecast_tab(self):

    '''
    Initialize and layout the Forecast tab components within the main application.
    '''

    # Container for all forecast content, with black background
    self.forecast_inner = tk.Frame(self.forecast_frame, bg="black")
    self.forecast_inner.pack(fill="both", expand=True, padx=0, pady=0)

    # List to keep references to each day's block for future updates
    self.forecast_blocks = []

    # Header label (initially empty) for dynamic title like "5-Day Forecast for City"
    self.forecast_header = tk.Label(
        self.forecast_inner,
        text="",                                 # Will be set on refresh
        font=("Helvetica Neue", 34, "bold"),     # Large, bold font
        fg="#ffe047",                          # Yellow accent color
        bg="black",
        anchor="center",
        justify="center"
    )
    self.forecast_header.pack(pady=(20, 18))     # Vertical padding above and below

    # Frame to hold day blocks in a horizontal row
    self.block_frame = tk.Frame(self.forecast_inner, bg="black")
    self.block_frame.pack(fill="x", expand=True)

    # Footer label displayed at bottom of the tab
    self.forecast_footer = tk.Label(
        self.forecast_frame,
        text=FORECAST_FOOTER,                    # Descriptive footer text
        font=SMALL_FONT,                         # Use consistent small font
        fg="#fff",                               # White text
        bg="black"
    )
    self.forecast_footer.pack(side="bottom", pady=(0, 12))


def refresh_forecast(self, city=None):

    '''
    Fetch new forecast data for the given city, then rebuild the forecast blocks.
    If no city is provided or invalid, display a prompt instead.
    '''

    # Remove existing day blocks
    for widget in self.block_frame.winfo_children():
        widget.destroy()
    self.forecast_blocks.clear()

    # Determine city name from argument or entry widget
    city = city or self.city_entry.get().strip()

    # If city is empty, prompt user and exit
    if not city:
        self.forecast_header.config(text="Enter a city to view forecast.")
        self.root.update_idletasks()
        return
    
    # Validate against stored suggestions (to ensure correct coordinates exist)
    city_disp = city or self.city_entry.get().strip()
    if not city_disp or city_disp not in self.suggestion_coords:
        self.forecast_header.config(text="Enter a city to view forecast.")
        self.root.update_idletasks()
        return

    # Look up lat/lon from suggestions mapping
    lat, lon = self.suggestion_coords[city_disp]

    # Start background fetch to avoid blocking the UI
    def _worker():
        # Attempt API call
        try:
            days = fetch_5day_forecast_by_coords(lat, lon)

        except APIError:
            logging.exception("Failed to fetch 5-day forecast")

            # Show a user-friendly popup (title first, then message)
            self.root.after(0, lambda: messagebox.showerror(
                "Forecast Error",
                "Could not fetch 5-day forecast at this time.\n"
                "Please check API status and try again later."
            ))
            return

        # Update header with formatted city name
        self.root.after(0, lambda: self.forecast_header.config(
            text=f"5-Day Forecast for {title_case(city_disp)}:",
            anchor="center", justify="center", font=("Helvetica Neue", 34, "bold")
        ))

        # Create and grid each day's forecast block
        def _populate():
            for i, day in enumerate(days):
                dayblock = make_forecast_block(
                    self.block_frame, day, self.convert_temp, self.temp_unit
                )
                dayblock.grid(
                    row=0, column=i, sticky="nsew", padx=28, ipadx=14, ipady=80
                )
                self.block_frame.columnconfigure(i, weight=1)
                self.forecast_blocks.append(dayblock)
        self.root.after(0, _populate)

    threading.Thread(target=_worker, daemon=True).start()


def make_forecast_block(parent, day, convert_temp_func, temp_unit):

    '''
    Helper to build a styled Frame for one day's forecast data.

    Args:
        parent: Tkinter parent widget
        day (dict): Forecast data for the day
        convert_temp_func (callable): Function to convert temp to current unit
        temp_unit (str): 'C' or 'F'

    Returns:
        Frame: Configured Tkinter Frame containing labels for the day's forecast
    '''

    # Accent color for headers and borders
    color = "#ffe047"

    # Determine emoji icon based on weather description
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

    # Convert temperatures and choose unit symbol
    temp_min = convert_temp_func(day['temp_min'])
    temp_max = convert_temp_func(day['temp_max'])
    t_unit_symbol = "°C" if temp_unit == "C" else "°F"

    # Outer frame with ridge border
    f = tk.Frame(parent, bg="#222", bd=3, relief="ridge", padx=14, pady=12)
    content = tk.Frame(f, bg="#222")
    content.pack(expand=True)

    # Date label
    tk.Label(content, text=day['date'], font=("Helvetica Neue", 16, "bold"), fg=color, bg="#222").pack(pady=(2, 0), anchor="center")

    # Weather description with icon
    tk.Label(content, text=f"{icon} {title_case(day['weather'])}", font=("Helvetica Neue", 16), fg="#fff", bg="#222").pack(anchor="center")

    # Divider
    tk.Label(content, text="----------------", font=("Helvetica Neue", 12), fg="#555", bg="#222").pack(pady=(4, 4), anchor="center")

    # Temperature range
    temp_label = tk.Label(content, text=f"{temp_min:.1f}{t_unit_symbol} - {temp_max:.1f}{t_unit_symbol}", font=("Helvetica Neue", 16, "bold"), fg="#ffe047", bg="#222")
    temp_label.pack(pady=(0, 8), anchor="center")
    f.temp_label = temp_label
    f.day_data    = day

    # Humidity
    tk.Label(content, text=f"Humidity: {day['humidity']}%", font=("Helvetica Neue", 15), fg="#bfffa5", bg="#222").pack(anchor="center")

    # Wind
    tk.Label(content, text=f"Wind: {day.get('wind', 'N/A')}", font=("Helvetica Neue", 15), fg="#43fad8", bg="#222").pack(anchor="center")

    # Visibility
    tk.Label(content, text=f"Visibility: {day.get('visibility', 'N/A')} km (max 10 km)", font=("Helvetica Neue", 15), fg="#a1e3ff", bg="#222").pack(anchor="center")

    return f     # Return the completed day block frame


def update_forecast_units(self):

    """
    In‐place update of temperature labels for all 5-day forecast blocks,
    toggling between Celsius and Fahrenheit without re-fetching data.
    """
    
    # Select the appropriate unit symbol based on current setting
    unit_symbol = "°C" if self.temp_unit == "C" else "°F"

    # Loop over each existing forecast block frame
    for block in self.forecast_blocks:
        # Retrieve the original forecast data dict attached during block creation
        forecast_data = block.day_data

        # Convert the stored minimum and maximum temperatures to the new unit
        converted_min = self.convert_temp(forecast_data['temp_min'])
        converted_max = self.convert_temp(forecast_data['temp_max'])

        # Update the label text directly on the widget to reflect new values
        block.temp_label.config(
            text=f"{converted_min:.1f}{unit_symbol} - {converted_max:.1f}{unit_symbol}"
        )
