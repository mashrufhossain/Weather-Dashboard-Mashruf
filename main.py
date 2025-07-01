import tkinter as tk
from tkinter import ttk
from api import get_weather
from utils import save_to_csv
from history import read_all_entries
from stats import calculate_stats
from comparison import compare_cities
import csv
from datetime import datetime

def save_to_csv(city, temp, description, file_path='history.csv'):
    """Save weather data to CSV file with timestamp."""
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), city, temp, description])

def fetch_and_display_weather(city_entry, weather_label, history_frame=None):
    city = city_entry.get()
    if not city:
        weather_label.config(text="Please enter a city.")
        return
    data = get_weather(city)
    if data.get("cod") != 200:
        weather_label.config(text=f"Error: {data.get('message', 'City not found')}")
    else:
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"].capitalize()
        weather_label.config(text=f"{city.title()}: {temp}°C, {description}")
        save_to_csv(city, temp, description)
        if history_frame:
            update_history(history_frame)

def update_history(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    entries = read_all_entries()
    if not entries:
        tk.Label(scrollable_frame, text="No history found.").pack(padx=10, pady=10)
    else:
        for row in reversed(entries):  # newest at the top!
            if len(row) < 4:
                row += ["No description"]
            timestamp, city, temp, desc = row
            desc = desc.capitalize() if desc else "No description"
            text = f"{timestamp} — {city.title()}: {temp}°C, {desc}"
            tk.Label(scrollable_frame, text=text, anchor='w').pack(fill='x', padx=5, pady=2)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def show_stats(frame):
    for widget in frame.winfo_children():
        widget.destroy()

    stats = calculate_stats()
    if not stats:
        tk.Label(frame, text="No data available for statistics.").pack(padx=10, pady=10)
        return

    tk.Label(frame, text=f"Min Temp: {stats['min']}°C").pack(padx=10, pady=5)
    tk.Label(frame, text=f"Max Temp: {stats['max']}°C").pack(padx=10, pady=5)
    tk.Label(frame, text="Weather Counts:").pack(padx=10, pady=5)

    for desc, count in stats["counts"].items():
        tk.Label(frame, text=f"{desc.capitalize()}: {count}").pack(padx=10, anchor='w')

def compare_cities_ui(frame, city1_entry, city2_entry, result_label):
    city1 = city1_entry.get()
    city2 = city2_entry.get()

    if not city1 or not city2:
        result_label.config(text="Please enter both cities.")
        return

    data1, data2 = compare_cities(city1, city2)

    if not data1 or not data2:
        result_label.config(text="Error fetching data for one or both cities.")
        return

    text = (
        f"{data1['city']}: {data1['temp']}°C, {data1['desc']}    "
        f"{data2['city']}: {data2['temp']}°C, {data2['desc']}"
    )
    result_label.config(text=text)

def main():
    root = tk.Tk()
    root.title("Weather Dashboard")
    root.geometry("900x700")

    label = tk.Label(root, text="Welcome to the Weather Dashboard!", font=("Helvetica", 16))
    label.pack(pady=(10, 4))  # less space under main title

    entry_frame = tk.Frame(root)
    entry_frame.pack(pady=(0, 4))  # less space below city row

    tk.Label(entry_frame, text="Enter city:").pack(side=tk.LEFT)
    city_entry = tk.Entry(entry_frame)
    city_entry.pack(side=tk.LEFT, padx=5)

    fetch_button = tk.Button(entry_frame, text="Get Weather", command=lambda: fetch_and_display_weather(city_entry, weather_label, history_content_frame))
    fetch_button.pack(side=tk.LEFT, padx=5)

    weather_label = tk.Label(root, text="", font=("Helvetica", 14))
    weather_label.pack(pady=(0, 6))  # less space below current weather

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', pady=(5, 10))  # tighter above, still enough space below

    # History tab
    frame1 = tk.Frame(notebook)
    tk.Label(
        frame1,
        text="This tab shows all your previous weather history entries.",
        font=("Helvetica", 14, "bold")
    ).pack(pady=(10, 18))  # More space under header

    history_content_frame = tk.Frame(frame1)
    history_content_frame.pack(fill="both", expand=True)
    update_history(history_content_frame)

    # History Statistics tab
    frame2 = tk.Frame(notebook)
    tk.Label(
        frame2,
        text="These statistics are calculated from your previous city weather searches.",
        font=("Helvetica", 14, "bold")
    ).pack(pady=(10, 18))

    stats_content_frame = tk.Frame(frame2)
    stats_content_frame.pack(fill="both", expand=True)
    show_stats_button = tk.Button(frame2, text="Show Statistics", command=lambda: show_stats(stats_content_frame))
    show_stats_button.pack(pady=5)

    # Compare Cities tab
    frame3 = tk.Frame(notebook)
    tk.Label(
        frame3,
        text="Compare the current weather between two cities.",
        font=("Helvetica", 14, "bold")
    ).pack(pady=(10, 18))

    tk.Label(frame3, text="City 1:").pack()
    city1_entry = tk.Entry(frame3)
    city1_entry.pack()
    tk.Label(frame3, text="City 2:").pack()
    city2_entry = tk.Entry(frame3)
    city2_entry.pack()
    result_label = tk.Label(frame3, text="", font=("Helvetica", 12))
    result_label.pack(pady=10)
    compare_button = tk.Button(frame3, text="Compare Cities", command=lambda: compare_cities_ui(frame3, city1_entry, city2_entry, result_label))
    compare_button.pack(pady=5)

    notebook.add(frame1, text="History")
    notebook.add(frame2, text="History Statistics")
    notebook.add(frame3, text="Compare Cities")

    root.mainloop()

if __name__ == "__main__":
    main()
