"""
ui/main_app.py

Main UI module for Weather Dashboard.

Defines WeatherApp class which:
- Sets up the root Tkinter window and overall layout
- Initializes and manages tabs (History, Statistics, Forecast, etc.)
- Wires up UI components, event handlers, and data-refresh logic
"""

# Guard to prevent this file from being run directly
if __name__ == "__main__":
    print("This file is not meant to be run directly. Please run main.py instead.")

# Tkinter for GUI and threading for background tasks
import tkinter as tk
from tkinter import ttk, messagebox
import os, time, threading

# Logging for developer error tracking
import logging

# Core logic and styling/constants
from db import WeatherDB
from utils import title_case
from styles import HEADER_FONT, NORMAL_FONT, SMALL_FONT, TAB_BG, TAB_FG, ACTIVE_TAB_BG, ACTIVE_TAB_FG
from constants import HISTORY_FOOTER, STATS_FOOTER, FORECAST_FOOTER

# API calls
from api import fetch_weather_by_coords, fetch_5day_forecast_by_coords, search_city_options, APIError

# Feature tabs
from features.history import create_history_tab, refresh_history, treeview_sort_column
from features.stats import create_stats_tab, refresh_stats
from features.forecast import create_forecast_tab, refresh_forecast, update_forecast_units


class WeatherApp:
    def __init__(self, root):
        
        '''
    Initialize the WeatherApp:
    - Configure main Tkinter window (title, size, colors)
    - Initialize suggestion mapping and database connection
    - Set default temperature unit
    - Bind feature-tab methods to this instance
    - Build UI, load last refresh time, and start auto-refresh loop
        '''

        self.root = root
        root.title("Weather Dashboard")
        root.configure(bg="black")
        root.geometry("1900x1100")
        root.minsize(1400, 800)

        # Store city coordinates for selected suggestions
        self.suggestion_coords = {}

        # Connect to SQLite database
        self.db = WeatherDB(os.path.join("data", "weather.db"))

        # Default temperature unit is Celsius
        self.temp_unit = "C"

        # Bind feature tab methods to the class instance
        self.create_history_tab = create_history_tab.__get__(self)
        self.refresh_history = refresh_history.__get__(self)
        self.treeview_sort_column = treeview_sort_column.__get__(self)    # This method is used in the history tab to sort the columns
        self.create_stats_tab = create_stats_tab.__get__(self)
        self.refresh_stats = refresh_stats.__get__(self)
        self.create_forecast_tab = create_forecast_tab.__get__(self)
        self.refresh_forecast = refresh_forecast.__get__(self)
        self.update_forecast_units = update_forecast_units.__get__(self)

        # Set up GUI widgets and tabs by calling the respective methods
        self.create_widgets()
        self.create_history_tab()
        self.create_stats_tab()
        self.create_forecast_tab()

        # Listen for tab switch events
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Suggestions UI and typing delay handling
        self.suggestions_listbox = None
        self.typing_timer = None

        # Load last refresh time from file if it exists
        refresh_path = os.path.join("data", "last_refresh.txt")
        if os.path.exists(refresh_path):
            with open(refresh_path, "r") as f:
                self.last_refresh_time = f.read().strip()
        else:
            self.last_refresh_time = "never"

        # Start auto-refresh timer
        self.start_auto_refresh()


    def create_widgets(self):

        '''
    Build and layout static UI components:
    - Header, input frame, labels, entry field, and buttons
    - Main weather display frame
    - Styled Notebook with Forecast, History, and Stats tabs
    - Keyboard bindings for tab navigation
        '''

        # Header label
        header = tk.Label(self.root, text="What's in Your Sky?", font=HEADER_FONT, fg="#DEAFEE", bg="black")
        header.pack(pady=(24, 20))

        # Input frame for city entry and buttons
        input_frame = tk.Frame(self.root, bg="black")
        input_frame.pack()

        # Helper label for city selection instructions
        self.helper_label = tk.Label(
            self.root,
            text="(Please select from suggestions)",
            font=SMALL_FONT,
            fg="#ccc",
            bg="black"
        )
        self.helper_label.pack(pady=(2, 0))

        # Label showing last refresh time and countdown
        self.refresh_label = tk.Label(self.root, text="Last refreshed: never | Next refresh in: -- s", 
                              font=SMALL_FONT, fg="#ccc", bg="black")
        self.refresh_label.pack(pady=(2, 8))

        # City entry field
        tk.Label(input_frame, text="Enter city:", font=NORMAL_FONT, fg="#fff", bg="black").grid(row=0, column=0, padx=(0, 3))
        self.city_entry = tk.Entry(input_frame, font=NORMAL_FONT, width=20)
        self.city_entry.grid(row=0, column=1, padx=(0, 8))

        # Bind key events for suggestion and enter/return key
        self.city_entry.bind("<KeyRelease>", self.on_typing)
        self.city_entry.bind("<Return>", self.on_enter_key)

        # Button to fetch weather
        get_btn = tk.Button(input_frame, text="Get Weather", font=NORMAL_FONT, command=self.get_weather)
        get_btn.grid(row=0, column=2)

        # Button to toggle temperature unit
        self.unit_btn = tk.Button(
            input_frame, text="Show °F", font=NORMAL_FONT,
            fg="#222", bg="#ffe047", activeforeground="#fff", activebackground="#ffb200",
            bd=1, relief="solid", width=8,
            command=self.toggle_unit
        )
        self.unit_btn.grid(row=0, column=3, padx=(8, 0))

        # Frame to display weather data
        self.weather_info_frame = tk.Frame(self.root, bg="black")
        self.weather_info_frame.pack(pady=(16, 2))

        # Create notebook for tabs
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

        # Add forecast, history, and stats tabs
        self.forecast_frame = tk.Frame(self.tabs, bg="black")
        self.tabs.add(self.forecast_frame, text="Forecast")

        self.history_frame = tk.Frame(self.tabs, bg="black")
        self.tabs.add(self.history_frame, text="History")

        self.stats_frame = tk.Frame(self.tabs, bg="black")
        self.tabs.add(self.stats_frame, text="History Statistics")

        # Pack notebook tabs into root window
        self.tabs.pack(fill="both", expand=True, pady=(8, 0))

        # Bind keyboard tab navigation
        self.root.bind("<Tab>", self.next_tab)
        self.root.bind("<Shift-Tab>", self.prev_tab)


    def toggle_unit(self):

        '''
    Switch between Celsius and Fahrenheit:
    - Flip the temp_unit flag
    - Update toggle button label
    - Refresh displayed weather, forecast, history, and stats
        '''

        # Toggle between Celsius and Fahrenheit
        self.temp_unit = "F" if self.temp_unit == "C" else "C"

        # Update the button text accordingly
        self.unit_btn.config(text=f"Show °{'C' if self.temp_unit == 'F' else 'F'}")

        # Refresh the displayed weather using the selected unit
        city = self.city_entry.get().strip()
        self.refresh_display(city, self.last_weather if hasattr(self, "last_weather") else None)
        self.update_forecast_units()
        self.refresh_history()
        self.refresh_stats()


    def convert_temp(self, temp_c):
        # Convert temperature to Farenheit
        return temp_c if self.temp_unit == "C" else temp_c * 9/5 + 32


    def get_weather(self):

        '''
    Validate city selection, fetch current weather, handle errors,
    save data to the database, and update all UI sections (display,
    history, stats, forecast). Record and display the new refresh time.
        '''

        # Clears the suggestion list if present
        if self.suggestions_listbox:
            self.suggestions_listbox.destroy()
            self.suggestions_listbox = None

        # Get user input city name
        city_disp = self.city_entry.get().strip()
        if not city_disp:
            messagebox.showerror("Error", "Please enter a city name.")
            return

        # Ensures city is selected from suggestions
        if city_disp not in self.suggestion_coords:
            messagebox.showerror("Error", "Please select a valid city from suggestions.")
            return

        # Get coordinates from suggestion mapping
        lat, lon = self.suggestion_coords[city_disp]

        try:
            # Fetch current weather data
            weather = fetch_weather_by_coords(lat, lon)
            self.last_weather = weather
        except APIError:
            # Record the error message and full stack trace in the console for debugging
            logging.exception("Failed to fetch current weather")

            # Show a user-friendly popup in the GUI
            messagebox.showerror(
                "Error",
                "Could not fetch current weather at this time.\n"
                "Please check API status and try again later."
            )
            return

        # Save weather information to database
        self.db.insert_weather(
            city=city_disp,
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

        # Refresh UI tabs with new data
        self.refresh_display(city_disp, weather)
        self.refresh_history()
        self.refresh_stats()
        self.refresh_forecast(city_disp)

        # ✅ Update refresh time and store it
        self.last_refresh_time = time.strftime("%Y-%m-%d %H:%M:%S")

        self.next_refresh_seconds = 60  # reset countdown

        with open(os.path.join("data", "last_refresh.txt"), "w") as f:
            f.write(self.last_refresh_time)

        # Update label with new refresh time
        if hasattr(self, 'refresh_label'):
            self.refresh_label.config(
                text=f"Last refreshed: {self.last_refresh_time}  •••  Next refresh in: {self.next_refresh_seconds} s"
            )


    def refresh_display(self, city, weather):

        '''
    Clear and rebuild the main weather card for a given city:
    - Convert and format temps, visibility, etc.
    - Create a styled frame showing city, temperature,
      condition icon, and detailed metrics.
        '''

        # Clear previous weather card content
        for widget in self.weather_info_frame.winfo_children():
            widget.destroy()

        # Skip if no weather data is available
        if not weather:
            return

        # Convert temperature units
        temp = self.convert_temp(weather['temp'])
        feels_like = self.convert_temp(weather["feels_like"])
        t_unit = "°C" if self.temp_unit == "C" else "°F"

        # Calculate visibility in kilometers
        visibility = weather.get("visibility", "N/A")
        if visibility != "N/A" and isinstance(visibility, (int, float)):
            visibility_km = round(visibility / 1000, 1)
        else:
            visibility_km = "N/A"

        # Main weather display card container
        card = tk.Frame(self.weather_info_frame, bg="#222", bd=3, relief="ridge", padx=20, pady=14)
        card.pack(pady=12)

        # City name
        tk.Label(card, text=title_case(city), font=("Helvetica Neue", 20, "bold"), fg="#ffe047", bg="#222").pack()

        # Temperature line
        tk.Label(card, text=f"{temp:.1f}{t_unit} (Feels like: {feels_like:.1f}{t_unit})", font=("Helvetica Neue", 16), fg="#fff", bg="#222").pack()

        # Weather condition description
        tk.Label(card, text=f"🌤️ {title_case(weather['weather'])}", font=("Helvetica Neue", 16), fg="#fff", bg="#222").pack(pady=(0, 6))

        # Divider line
        tk.Label(card, text="──────────────", font=("Helvetica Neue", 12), fg="#555", bg="#222").pack(pady=4)

        # First row: Humidity, Wind, Visibility
        row1 = tk.Frame(card, bg="#222")
        row1.pack(pady=2)
        tk.Label(row1, text=f"💧 Humidity: {weather['humidity']}%", font=("Helvetica Neue", 14), fg="#bfffa5", bg="#222").grid(row=0, column=0, padx=14, sticky="w")
        tk.Label(row1, text=f"🌬️ Wind: {weather['wind']}", font=("Helvetica Neue", 14), fg="#43fad8", bg="#222").grid(row=0, column=1, padx=14, sticky="w")
        tk.Label(row1, text=f"👁️ Visibility: {visibility_km} km", font=("Helvetica Neue", 14), fg="#a1e3ff", bg="#222").grid(row=0, column=2, padx=14, sticky="w")

        # Second row: Pressure, Sunrise, Sunset
        row2 = tk.Frame(card, bg="#222")
        row2.pack(pady=2)
        tk.Label(row2, text=f"📄 Pressure: {weather['pressure']} hPa", font=("Helvetica Neue", 14), fg="#ffd580", bg="#222").grid(row=0, column=0, padx=14, sticky="w")
        tk.Label(row2, text=f"🌅 Sunrise: {weather['sunrise']}", font=("Helvetica Neue", 14), fg="#ffacac", bg="#222").grid(row=0, column=1, padx=14, sticky="w")
        tk.Label(row2, text=f"🌇 Sunset: {weather['sunset']}", font=("Helvetica Neue", 14), fg="#ffacac", bg="#222").grid(row=0, column=2, padx=14, sticky="w")


    def on_tab_change(self, event):

        '''
    Notebook tab-change handler:
    - Detect selected tab index and trigger appropriate refresh:
      0→forecast, 1→history, 2→stats
        '''

        # Determine which tab is selected by index
        idx = self.tabs.index(self.tabs.select())

        if idx == 0:
            # Forecast tab selected
            self.refresh_forecast(self.city_entry.get().strip())

        elif idx == 1:
            # History tab selected
            self.refresh_history()

        elif idx == 2:
            # Stats tab selected
            self.refresh_stats()
    

    def next_tab(self, event=None):
        
        '''
    Move focus to the next Notebook tab (wraps at end)
    and prevent default widget focus change.
        '''

        # Move to the next tab (loop around if at the end)
        current = self.tabs.index(self.tabs.select())
        next_index = (current + 1) % len(self.tabs.tabs())
        self.tabs.select(next_index)

        return "break"  # Prevent default focus change


    def prev_tab(self, event=None):

        '''
    Move focus to the previous Notebook tab (wraps at start)
    and prevent default widget focus change.
        '''

        # Move to the previous tab (loop around if at the start)
        current = self.tabs.index(self.tabs.select())
        prev_index = (current - 1) % len(self.tabs.tabs())
        self.tabs.select(prev_index)

        return "break"  # Prevent default focus change
    

    def show_suggestions(self, suggestions):

        '''
    Display a Listbox of city suggestions under the entry field:
    - Map display names to lat/lon for selection
    - Configure keyboard/mouse bindings for selection,
      navigation, hover, and dismissal.
        '''

        # Destroy old listbox if it exists
        if self.suggestions_listbox:
            self.suggestions_listbox.destroy()

        # Return early if no suggestions to show
        if not suggestions:
            return

        # Map display strings to their lat/lon values
        self.suggestion_coords = {
            s: (opt["lat"], opt["lon"]) 
            for opt, s in zip(suggestions, [opt["display"] for opt in suggestions])
        }

        # Create and configure the suggestions listbox
        self.suggestions_listbox = tk.Listbox(
            self.root,
            font=("Helvetica Neue", 14),
            bg="#111",
            fg="#fff",
            highlightthickness=2,
            highlightbackground="#DEAFEE",
            selectbackground="#DEAFEE",
            selectforeground="#111",
            relief="solid",
            bd=1,
            height=min(len(suggestions), 6),
            activestyle="none",
            exportselection=False
        )

        # Place it under the city_entry input
        x = self.city_entry.winfo_rootx() - self.root.winfo_rootx()
        y = self.city_entry.winfo_rooty() - self.root.winfo_rooty() + self.city_entry.winfo_height()
        self.suggestions_listbox.place(x=x, y=y, width=self.city_entry.winfo_width())

        # Insert all suggestions into the listbox
        for opt in suggestions:
            self.suggestions_listbox.insert(tk.END, opt["display"])

        # Handle explicit selection via Enter or mouse click
        self.suggestions_listbox.bind("<Return>", lambda e: (self.on_suggestion_selected(e), self.city_entry.focus_set()))
        self.suggestions_listbox.bind("<ButtonRelease-1>", lambda e: (self.on_suggestion_selected(e), self.city_entry.focus_set()))

        # Bind Escape key to close suggestions box when inside as a result of using arrow keys and return focus to entry
        self.suggestions_listbox.bind("<Escape>", lambda e: (self.suggestions_listbox.destroy(), self.city_entry.focus_set()))

        def on_arrow_key(event):

            '''
    (nested) Listbox arrow-key handler:
    - Up/Down to change selection in suggestions
    - Wrap around at ends
    - Prevent default event propagation
            '''

            cur = self.suggestions_listbox.curselection()
            count = self.suggestions_listbox.size()

            if event.keysym == "Down":
                if cur:
                    next_index = (cur[0] + 1) % count
                else:
                    next_index = 0
                self.suggestions_listbox.selection_clear(0, tk.END)
                self.suggestions_listbox.selection_set(next_index)
                return "break"

            elif event.keysym == "Up":
                if cur:
                    prev_index = (cur[0] - 1) % count
                else:
                    prev_index = count - 1
                self.suggestions_listbox.selection_clear(0, tk.END)
                self.suggestions_listbox.selection_set(prev_index)
                return "break"

        self.suggestions_listbox.bind("<Up>", on_arrow_key)
        self.suggestions_listbox.bind("<Down>", on_arrow_key)

        def on_hover(event):

            '''
    (nested) Mouse-motion handler for Listbox:
    - Highlight the item under the cursor
    - Clear highlight when leaving the widget area
            '''

            index = self.suggestions_listbox.nearest(event.y)
            if 0 <= event.y <= self.suggestions_listbox.winfo_height():
                self.suggestions_listbox.selection_clear(0, tk.END)
                self.suggestions_listbox.selection_set(index)
            else:
                self.suggestions_listbox.selection_clear(0, tk.END)

        self.suggestions_listbox.bind("<Motion>", on_hover)
        self.suggestions_listbox.bind("<Leave>", lambda e: self.suggestions_listbox.selection_clear(0, tk.END))
        

    def on_suggestion_selected(self, event):

        '''
    Handle user selection from suggestions Listbox:
    - Retrieve selected city display name
    - Populate entry field and destroy Listbox
        '''

        # If no suggestions listbox exists, exit early
        if not self.suggestions_listbox:
            return
        
        # Get the currently selected item
        selection = self.suggestions_listbox.get(self.suggestions_listbox.curselection())

        # Update the entry field with selected city
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, selection)

        # Remove the suggestions listbox from view
        self.suggestions_listbox.destroy()
        self.suggestions_listbox = None


    def fetch_suggestions(self):

        '''
    Debounced trigger for fetching city suggestions:
    - Skip queries shorter than 2 chars
    - Spawn a background thread to call search_city_options(),
      then schedule show_suggestions via root.after.
        '''

        # Grab the query from the entry field
        query = self.city_entry.get().strip()

        # Do not show suggestions if query is empty or too short
        if not query or len(query) < 2:
            if self.suggestions_listbox:
                self.suggestions_listbox.destroy()
                self.suggestions_listbox = None
            return

        def worker():

            '''
    (nested) Background thread target for fetch_suggestions:
    - Call search_city_options(query)
    - Schedule show_suggestions on the main thread
            '''

            options = search_city_options(query)
            self.root.after(0, lambda: self.show_suggestions(options))
            
        threading.Thread(target=worker, daemon=True).start()


    def on_typing(self, event):

        '''
    Entry-field key handler:
    - Arrow-down focuses suggestions if present
    - Ignore non-character control keys
    - Debounce calls to fetch_suggestions()
        '''

        # Allow Down key to move focus to suggestions listbox
        if event.keysym == "Down":
            return self.focus_suggestions(event)

        # Skip suggestion logic for non-character control keys
        if event.keysym in [
            "Up", "Left", "Right", "Return", "Tab", 
            "Shift_L", "Shift_R", "Control_L", "Control_R", 
            "Alt_L", "Alt_R", "Escape"]:
            return

        # Cancel existing debounce timer if active
        if self.typing_timer:
            self.root.after_cancel(self.typing_timer)

        # Start a new debounce timer to fetch suggestions
        self.typing_timer = self.root.after(300, self.fetch_suggestions)


    def on_enter_key(self, event):
        
        '''
    Return-key handler in entry field:
    - If current text matches a suggestion, call get_weather()
    - Otherwise, prompt the user to select from suggestions
        '''

        # Get city input from entry field
        city_disp = self.city_entry.get().strip()

        # Proceed if city input matches a valid suggestion
        if city_disp in self.suggestion_coords:
            self.get_weather()
            
            # Clear suggestion box if still visible
            if self.suggestions_listbox:
                self.suggestions_listbox.destroy()
                self.suggestions_listbox = None
        else:
            # Display warning message if user input does not match any valid suggestion
            messagebox.showwarning("Selection required", "Please select a city from the suggestions before pressing Enter.")


    def focus_suggestions(self, event):

        '''
    If suggestions Listbox exists, move keyboard focus to it
    and stop further event propagation.
        '''

        # Keyboard navigation: move focus to the suggestions listbox if it exists
        if self.suggestions_listbox:

            self.suggestions_listbox.focus_set()  # Focus the listbox only

            return "break"  # Stop the event from bubbling up to root window
        
        return None


    def start_auto_refresh(self):

        '''
    Kick off two timed loops:
    1) update_timer (every 1s): decrement countdown and update label
    2) refresh (every 60s): re-fetch weather if a city is selected,
       else update refresh timestamp only, then reset countdown.
        '''

        # Start countdown at 60 seconds for auto-refresh
        self.next_refresh_seconds = 60

        # Load last refresh time from file if it exists
        refresh_path = os.path.join("data", "last_refresh.txt")
        if os.path.exists(refresh_path):
            with open(refresh_path, "r") as f:
                self.last_refresh_time = f.read().strip()
        else:
            self.last_refresh_time = "never"

        def update_timer():

            '''
    (nested) Countdown updater:
    - Decrement next_refresh_seconds each second
    - Update refresh_label text
    - Re-schedule itself after 1s
            '''

            if self.next_refresh_seconds > 0:
                self.next_refresh_seconds -= 1

            if hasattr(self, 'refresh_label'):
                self.refresh_label.config(
                    text=f"Last refreshed: {self.last_refresh_time}  •••  Next refresh in: {self.next_refresh_seconds} s"
                )

            # Schedule next 1-second update
            self.root.after(1000, update_timer)

        def refresh():

            '''
    (nested) Auto-refresh loop:
    - Every 60s, fetch new weather if a valid city is selected
      or simply update the timestamp otherwise
    - Write the new timestamp to file and update label
    - Reset countdown and re-schedule itself after 60s
            '''
            
            city_disp = self.city_entry.get().strip()
            if city_disp and city_disp in self.suggestion_coords:
                # Fetch new weather if city selected
                self.get_weather()
            else:
                # Otherwise, update the refresh time at the next interval
                self.last_refresh_time = time.strftime("%Y-%m-%d %H:%M:%S")
                self.next_refresh_seconds = 60

                with open(os.path.join("data", "last_refresh.txt"), "w") as f:
                    f.write(self.last_refresh_time)

                if hasattr(self, 'refresh_label'):
                    self.refresh_label.config(
                        text=f"Last refreshed: {self.last_refresh_time}  •••  Next refresh in: {self.next_refresh_seconds} s"
                    )

            # Restart the 60-second refresh timer
            self.next_refresh_seconds = 60
            self.root.after(60000, refresh)

        # Start both the visual timer and the refresh loop
        self.root.after(1000, update_timer)
        self.root.after(60000, refresh)