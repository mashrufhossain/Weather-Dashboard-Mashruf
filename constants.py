"""
constants.py

UI footer text constants for the Weather Dashboard application.

Contains descriptive strings displayed at the bottom of each tab:
- HISTORY_FOOTER: Guidance for the History tab (recent entries)
- STATS_FOOTER: Explanation for the Statistics tab (summary data)
- FORECAST_FOOTER: Note for the Forecast tab (predictive outlook)
"""

# Footer displayed in the History tab explaining its contents and sorting behavior
HISTORY_FOOTER = (
    "This tab shows the 50 most recent weather history entries. "
    "Columns can be sorted by clicking their headers."
)

# Footer displayed in the Statistics tab summarizing how data is aggregated
STATS_FOOTER = (
    "This tab summarizes all weather history with key statistics and records, "
    "calculated using SQL."
)

# Footer displayed in the Forecast tab describing predictive data
FORECAST_FOOTER = (
    "This tab displays a 5-day predictive forecast for the city entered."
)