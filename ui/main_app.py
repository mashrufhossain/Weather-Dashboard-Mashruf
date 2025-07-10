"""
Main Tkinter UI class for Weather Dashboard.
Do not run this file directly; use main.py as the entry point.
"""

if __name__ == "__main__":
    print("This file is not meant to be run directly. Please run main.py instead.")

import tkinter as tk
from tkinter import ttk, messagebox
import os
import time
import threading
from db import WeatherDB
from utils import title_case
from styles import HEADER_FONT, NORMAL_FONT, SMALL_FONT, TAB_BG, TAB_FG, ACTIVE_TAB_BG, ACTIVE_TAB_FG
from constants import HISTORY_FOOTER, STATS_FOOTER, FORECAST_FOOTER
from api import fetch_weather_by_coords, fetch_5day_forecast_by_coords, search_city_options
from features.history import create_history_tab, refresh_history
from features.stats import create_stats_tab, refresh_stats
from features.forecast import create_forecast_tab, refresh_forecast


class WeatherApp:
    def __init__(self, root):
        self.root = root
        root.title("Weather Dashboard")
        root.configure(bg="black")
        root.geometry("1900x1025")
        root.minsize(1400, 800)
        self.suggestion_coords = {}
        self.db = WeatherDB(os.path.join("data", "weather.db"))
        self.temp_unit = "C"

        # ✅ First: bind functions
        self.create_history_tab = create_history_tab.__get__(self)
        self.refresh_history = refresh_history.__get__(self)
        self.create_stats_tab = create_stats_tab.__get__(self)
        self.refresh_stats = refresh_stats.__get__(self)
        self.create_forecast_tab = create_forecast_tab.__get__(self)
        self.refresh_forecast = refresh_forecast.__get__(self)

        # ✅ Then: call them
        self.create_widgets()
        self.create_history_tab()
        self.create_stats_tab()
        self.create_forecast_tab()

        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)
        self.suggestions_listbox = None
        self.typing_timer = None

        refresh_path = os.path.join("data", "last_refresh.txt")
        if os.path.exists(refresh_path):
            with open(refresh_path, "r") as f:
                self.last_refresh_time = f.read().strip()
        else:
            self.last_refresh_time = "never"

        self.start_auto_refresh()


    def create_widgets(self):
        header = tk.Label(self.root, text="What's in Your Sky?", font=HEADER_FONT, fg="#DEAFEE", bg="black")
        header.pack(pady=(24, 20))

        input_frame = tk.Frame(self.root, bg="black")
        input_frame.pack()
        self.helper_label = tk.Label(
            self.root,
            text="(Please select from suggestions)",
            font=SMALL_FONT,
            fg="#ccc",
            bg="black"
        )
        self.helper_label.pack(pady=(2, 0))
        self.refresh_label = tk.Label(self.root, text="Last refreshed: never | Next refresh in: -- s", 
                              font=SMALL_FONT, fg="#ccc", bg="black")
        self.refresh_label.pack(pady=(2, 8))

        tk.Label(input_frame, text="Enter city:", font=NORMAL_FONT, fg="#fff", bg="black").grid(row=0, column=0, padx=(0, 3))

        self.city_entry = tk.Entry(input_frame, font=NORMAL_FONT, width=20)
        self.city_entry.grid(row=0, column=1, padx=(0, 8))

        # 🔥 Bind Enter key to get_weather
        self.city_entry.bind("<KeyRelease>", self.on_typing)
        self.city_entry.bind("<Return>", self.on_enter_key)

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
        self.root.bind("<Tab>", self.next_tab)
        self.root.bind("<Shift-Tab>", self.prev_tab)


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
        # Always destroy suggestions listbox if it exists
        if self.suggestions_listbox:
            self.suggestions_listbox.destroy()
            self.suggestions_listbox = None

        city_disp = self.city_entry.get().strip()
        if not city_disp:
            messagebox.showerror("Error", "Please enter a city name.")
            return

        if city_disp not in self.suggestion_coords:
            messagebox.showerror("Error", "Please select a valid city from suggestions.")
            return

        lat, lon = self.suggestion_coords[city_disp]

        try:
            weather = fetch_weather_by_coords(lat, lon)
            self.last_weather = weather
        except Exception as e:
            messagebox.showerror("Error", f"Could not fetch weather: {e}")
            return

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

        self.refresh_display(city_disp, weather)
        self.refresh_history()
        self.refresh_stats()
        self.refresh_forecast(city_disp)

        # ✅ Update refresh time and file
        self.last_refresh_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.next_refresh_seconds = 60  # reset countdown

        with open(os.path.join("data", "last_refresh.txt"), "w") as f:
            f.write(self.last_refresh_time)

        if hasattr(self, 'refresh_label'):
            self.refresh_label.config(
                text=f"Last refreshed: {self.last_refresh_time}  •••  Next refresh in: {self.next_refresh_seconds} s"
            )


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


    def on_tab_change(self, event):
        idx = self.tabs.index(self.tabs.select())
        if idx == 0:
            self.refresh_forecast(self.city_entry.get().strip())
        elif idx == 1:
            self.refresh_history()
        elif idx == 2:
            self.refresh_stats()
    

    def next_tab(self, event=None):
        current = self.tabs.index(self.tabs.select())
        next_index = (current + 1) % len(self.tabs.tabs())
        self.tabs.select(next_index)
        return "break"  # Prevent default focus change


    def prev_tab(self, event=None):
        current = self.tabs.index(self.tabs.select())
        prev_index = (current - 1) % len(self.tabs.tabs())
        self.tabs.select(prev_index)
        return "break"  # Prevent default focus change


    def ask_user_to_choose_location(self, options):
        """
        Show a popup window to let the user choose a location option.
        Returns the chosen string.
        """
        popup = tk.Toplevel(self.root)
        popup.title("Select Location")
        popup.configure(bg="black")
        tk.Label(popup, text="Did you mean:", font=NORMAL_FONT, fg="#fff", bg="black").pack(pady=(10, 5))

        choice_var = tk.StringVar(value=options[0])

        for opt in options:
            tk.Radiobutton(popup, text=opt, variable=choice_var, value=opt,
                        font=SMALL_FONT, fg="#fff", bg="black",
                        selectcolor="#444", activebackground="black").pack(anchor="w", padx=20)

        def on_select():
            popup.destroy()

        tk.Button(popup, text="OK", font=NORMAL_FONT, command=on_select).pack(pady=(8, 10))
        popup.grab_set()  # Make it modal
        popup.wait_window()

        return choice_var.get()


    def show_suggestions(self, suggestions):
        if self.suggestions_listbox:
            self.suggestions_listbox.destroy()

        if not suggestions:
            return

        self.suggestion_coords = {s: (opt["lat"], opt["lon"]) for opt, s in zip(suggestions, [opt["display"] for opt in suggestions])}

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
            activestyle="none"
        )

        x = self.city_entry.winfo_rootx() - self.root.winfo_rootx()
        y = self.city_entry.winfo_rooty() - self.root.winfo_rooty() + self.city_entry.winfo_height()
        self.suggestions_listbox.place(x=x, y=y, width=self.city_entry.winfo_width())

        for opt in suggestions:
            self.suggestions_listbox.insert(tk.END, opt["display"])

        self.suggestions_listbox.bind("<<ListboxSelect>>", self.on_suggestion_selected)
        

    def on_suggestion_selected(self, event):
        if not self.suggestions_listbox:
            return
        selection = self.suggestions_listbox.get(self.suggestions_listbox.curselection())
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, selection)
        self.suggestions_listbox.destroy()
        self.suggestions_listbox = None


    def fetch_suggestions(self):
        query = self.city_entry.get().strip()
        if not query or len(query) < 2:
            if self.suggestions_listbox:
                self.suggestions_listbox.destroy()
                self.suggestions_listbox = None
            return

        def worker():
            options = search_city_options(query)
            self.root.after(0, lambda: self.show_suggestions(options))
            
        threading.Thread(target=worker, daemon=True).start()


    def on_typing(self, event):
        if event.keysym in ["Up", "Down", "Left", "Right", "Return", "Tab", 
                            "Shift_L", "Shift_R", "Control_L", "Control_R", 
                            "Alt_L", "Alt_R", "Escape"]:
            return

        if self.typing_timer:
            self.root.after_cancel(self.typing_timer)
        self.typing_timer = self.root.after(300, self.fetch_suggestions)


    def on_enter_key(self, event):
        city_disp = self.city_entry.get().strip()
        # Check if it matches one of the valid suggestions
        if city_disp in self.suggestion_coords:
            self.get_weather()
            # Also destroy the suggestion box if still visible
            if self.suggestions_listbox:
                self.suggestions_listbox.destroy()
                self.suggestions_listbox = None
        else:
            messagebox.showwarning("Selection required", "Please select a city from the suggestions before pressing Enter.")


    def focus_suggestions(self, event):
        if self.suggestions_listbox:
            self.suggestions_listbox.selection_clear(0, tk.END)
            self.suggestions_listbox.selection_set(0)
            return "break"  # Stop Entry from moving cursor


    def start_auto_refresh(self):
        self.next_refresh_seconds = 60

        # Load from file if exists (do this at startup)
        refresh_path = os.path.join("data", "last_refresh.txt")
        if os.path.exists(refresh_path):
            with open(refresh_path, "r") as f:
                self.last_refresh_time = f.read().strip()
        else:
            self.last_refresh_time = "never"

        def update_timer():
            if self.next_refresh_seconds > 0:
                self.next_refresh_seconds -= 1

            if hasattr(self, 'refresh_label'):
                self.refresh_label.config(
                    text=f"Last refreshed: {self.last_refresh_time}  •••  Next refresh in: {self.next_refresh_seconds} s"
                )

            self.root.after(1000, update_timer)

        def refresh():
            city_disp = self.city_entry.get().strip()
            if city_disp and city_disp in self.suggestion_coords:
                self.get_weather()
            else:
                # Even if no city selected, update time to show that background ran
                self.last_refresh_time = time.strftime("%Y-%m-%d %H:%M:%S")
                self.next_refresh_seconds = 60

                with open(os.path.join("data", "last_refresh.txt"), "w") as f:
                    f.write(self.last_refresh_time)

                if hasattr(self, 'refresh_label'):
                    self.refresh_label.config(
                        text=f"Last refreshed: {self.last_refresh_time}  •••  Next refresh in: {self.next_refresh_seconds} s"
                    )

            # Reset countdown
            self.next_refresh_seconds = 60
            self.root.after(60000, refresh)

        # Start both loops
        self.root.after(1000, update_timer)
        self.root.after(60000, refresh)