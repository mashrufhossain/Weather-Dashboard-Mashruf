"""
stats.py

Statistics UI module for Weather Dashboard.

Provides functions to:
- create_stats_tab: Initialize the Statistics tab layout and footer.
- refresh_stats: Query aggregated metrics from the database and display them in labeled grids.
"""

import tkinter as tk                                       # Core Tkinter library for GUI components
from constants import STATS_FOOTER                         # Footer text constant for the history statistics tab
from styles import HEADER_FONT, NORMAL_FONT, SMALL_FONT    # Font styles for headings and labels


def create_stats_tab(self):

    """
    Initialize the Statistics tab UI:
    - Create an inner frame for layout.
    - Pack the footer label at the bottom of the tab.
    """

    # Container inside stats_frame for all stats content
    self.stats_frame_inner = tk.Frame(self.stats_frame, bg="black")
    self.stats_frame_inner.pack(expand=True, fill="both", pady=(14, 0))

    # Footer label with explanatory text, using small font
    self.stats_footer = tk.Label(self.stats_frame, text=STATS_FOOTER, font=SMALL_FONT, fg="#fff", bg="black")
    self.stats_footer.pack(side="bottom", pady=(0, 12))


def refresh_stats(self):

    """
    Refresh and display database statistics:
    - Clear previous widgets.
    - Fetch stats dict from database.
    - Display a header and key summary grid for top metrics.
    - Display a secondary grid for detailed averages and records.
    """

    # Remove any existing children in the inner frame
    for w in self.stats_frame_inner.winfo_children():
        w.destroy()

    # Header label for the stats section
    header_label = tk.Label(self.stats_frame_inner, text="SQL Statistics of Weather History", font=HEADER_FONT, fg="#ffe047", bg="black")
    header_label.pack(pady=(10, 20))


    # Retrieve aggregated statistics from the database
    stats = self.db.get_stats()
    if not stats:
        tk.Label(self.stats_frame_inner, text="No statistics available yet. Search for a city first!", font=NORMAL_FONT, fg="#fff", bg="black").pack(pady=24)
        return


    # Extract raw hottest and coldest temperatures
    hottest_temp = stats['hottest_raw']
    coldest_temp = stats['coldest_raw']

    # Convert to Fahrenheit if needed
    if self.temp_unit == "F":
        hottest_temp = hottest_temp * 9 / 5 + 32
        coldest_temp = coldest_temp * 9 / 5 + 32

    # Create a grid frame for top summary metrics
    summary_grid = tk.Frame(self.stats_frame_inner, bg="black")
    summary_grid.pack(anchor="center", pady=(4, 18))

    # Define rows: label, value, city, timestamp
    summary_rows = [
        ("🔥 Hottest", f"{hottest_temp:.2f}°{self.temp_unit}", stats['hottest_city'], stats['hottest_time']),
        ("❄️ Coldest", f"{coldest_temp:.2f}°{self.temp_unit}", stats['coldest_city'], stats['coldest_time']),
        ("⛅ Strongest Wind", stats['strongest_wind'], stats['strongest_wind_city'], stats['strongest_wind_time']),
        ("💧 Most Humid", stats['most_humid'], stats['most_humid_city'], stats['most_humid_time']),
    ]

    # Populate summary grid rows
    for i, (label, value, city, time) in enumerate(summary_rows):
        tk.Label(summary_grid, text=label, font=NORMAL_FONT, fg="#fff", bg="black", anchor="w", width=18).grid(row=i, column=0, sticky="w", padx=(12, 8), pady=2)
        tk.Label(summary_grid, text=value, font=NORMAL_FONT, fg="#ffe047", bg="black", anchor="w", width=12).grid(row=i, column=1, sticky="w", padx=8, pady=2)
        tk.Label(summary_grid, text=city, font=NORMAL_FONT, fg="#43fad8", bg="black", anchor="w", width=22).grid(row=i, column=2, sticky="w", padx=8, pady=2)
        tk.Label(summary_grid, text=time, font=NORMAL_FONT, fg="#ccc", bg="black", anchor="w", width=20).grid(row=i, column=3, sticky="w", padx=8, pady=2)

    # Calculate average temperature display text
    avg_temp = stats['avg_temp']
    t_unit = "°C"
    if self.temp_unit == "F":
        avg_temp = avg_temp * 9 / 5 + 32
        t_unit = "°F"
    avg_temp_text = f"{avg_temp:.1f}{t_unit}"

    grid = tk.Frame(self.stats_frame_inner, bg="black")
    grid.pack(anchor="n", pady=(4, 0))

    # Secondary grid for additional detailed metrics
    rows = [
        ("Total logs:", stats['log_count']),
        ("Most searched city:", stats['most_searched']),
        ("Average temperature:", avg_temp_text),
        ("Average humidity:", f"{stats['avg_humidity']}%"),
        ("Average pressure:", f"{stats['avg_pressure']} hPa"),
        ("Average wind speed:", f"{stats['avg_wind']:.2f} m/s"),
    ]

    # Extend with sea level, ground level, and daylight extremes
    rows.extend([
        ("Average sea level pressure:", f"{stats['avg_sea_level']} hPa"),
        ("Highest sea level:", f"{stats['highest_sea_value']} in {stats['highest_sea_city']} at {stats['highest_sea_time']}"),
        ("Average ground level pressure:", f"{stats['avg_ground_level']} hPa"),
        ("Lowest ground level:", f"{stats['lowest_ground_value']} in {stats['lowest_ground_city']} at {stats['lowest_ground_time']}"),
        ("Earliest sunrise:", f"{stats['earliest_sunrise_time']} in {stats['earliest_sunrise_city']}"),
        ("Latest sunset:", f"{stats['latest_sunset_time']} in {stats['latest_sunset_city']}"),
    ])

    # Populate detailed metrics grid
    for i, (k, v) in enumerate(rows):
        tk.Label(grid, text=k, font=NORMAL_FONT, fg="#ccc", bg="black", anchor="e").grid(row=i, column=0, sticky="e", pady=1, padx=(24, 8))
        tk.Label(grid, text=v, font=NORMAL_FONT, fg="#fff", bg="black", anchor="w").grid(row=i, column=1, sticky="w", pady=1)