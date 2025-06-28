import tkinter as tk
from tkinter import ttk
from api import get_weather
from utils import save_to_csv
import csv
from datetime import datetime

def save_to_csv(city, temp, description):
    """Save weather data to history.csv with timestamp."""
    with open('history.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), city, temp, description])

def fetch_and_display_weather(city_entry, weather_label):
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

def main():
    root = tk.Tk()
    root.title("Weather Dashboard")
    root.geometry("800x600")

    # Header label
    label = tk.Label(root, text="Welcome to the Weather Dashboard!", font=("Helvetica", 16))
    label.pack(pady=10)

    # City entry
    entry_frame = tk.Frame(root)
    entry_frame.pack(pady=10)

    tk.Label(entry_frame, text="Enter city:").pack(side=tk.LEFT)
    city_entry = tk.Entry(entry_frame)
    city_entry.pack(side=tk.LEFT, padx=5)

    weather_label = tk.Label(root, text="", font=("Helvetica", 14))
    weather_label.pack(pady=5)

    fetch_button = tk.Button(
        root, text="Get Weather",
        command=lambda: fetch_and_display_weather(city_entry, weather_label)
    )
    fetch_button.pack()

    # Notebook tabs (keep these as placeholders for future features)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', pady=20)

    frame1 = tk.Frame(notebook)
    frame2 = tk.Frame(notebook)

    tk.Label(frame1, text="Feature 1 here!").pack(padx=10, pady=10)
    tk.Label(frame2, text="Feature 2 here!").pack(padx=10, pady=10)

    notebook.add(frame1, text="History")
    notebook.add(frame2, text="Graph")

    root.mainloop()

if __name__ == "__main__":
    main()