'''
features/tea_selector.py

Provides tea recommendations based on current weather conditions,
using pre-defined CSV files for different weather categories.
'''

import os                                                       # Used for building paths to locate tea CSV files
import random                                                   # Used for randomly selecting a tea from matching suggestions
import pandas as pd                                             # Used for reading CSV files into DataFrames
from styles import HEADER_FONT, NORMAL_FONT, TAB_BG, TAB_FG     # Import shared styles for fonts and colors
from constants import TEA_SELECTOR_FOOTER                       # Footer text constant for the Tea Selector tab
import tkinter as tk                                            # GUI widgets including label, frame
from tkinter import ttk                                         # Theme widgets for notebook tab only
from PIL import Image, ImageTk                                  # Use Pillow for JPEG compatibility


# Directory where tea CSV files are located
CSV_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Maps general weather conditions to corresponding tea CSV filenames
WEATHER_TO_FILE = {
    "Clear": "clear_weather_teas.csv",
    "Clouds": "cloudy_weather_teas.csv",
    "Rain": "rainy_weather_teas.csv",
    "Drizzle": "rainy_weather_teas.csv",
    "Snow": "cold_weather_teas.csv",
    "Mist": "cloudy_weather_teas.csv",
    "Fog": "cloudy_weather_teas.csv",
    "Thunderstorm": "rainy_weather_teas.csv"
}

# In-memory cache to avoid reloading CSV files on every request
loaded_tea_data = {}

# List of tea image filenames to cycle through (tea1.jpg to tea10.jpg)
TEA_IMAGES = [f"tea{i}.jpg" for i in range(1, 11)]


def load_tea_data(filename):

    """
    Load tea data from a given CSV file if not already cached.

    Parameters:
        filename (str): The name of the CSV file to load

    Returns:
        pd.DataFrame: DataFrame containing tea options
    """

    if filename not in loaded_tea_data:
        try:
            filepath = os.path.join(CSV_DIR, filename)
            df = pd.read_csv(filepath)
            loaded_tea_data[filename] = df
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return pd.DataFrame()
    return loaded_tea_data[filename]


def get_tea_recommendation(weather_main: str) -> str:

    """
    Return a tea recommendation string based on the main weather description.

    Parameters:
        weather_main (str): Main weather condition from API (e.g., "Rain", "Clear")

    Returns:
        str: Tea recommendation message
    """

    # Normalize the weather condition for comparison
    weather_main = weather_main.lower()

    # Match partial strings to known weather types
    matched_key = None
    for key in WEATHER_TO_FILE:
        if key.lower() in weather_main:
            matched_key = key
            break

    # Fallback if no match found
    filename = WEATHER_TO_FILE.get(matched_key)
    if not filename:
        return "English Breakfast – A classic choice for any weather."

    # Load the corresponding tea data
    df = load_tea_data(filename)
    if df.empty:
        return "English Breakfast – A classic choice for any weather."

    # Randomly select one tea suggestion
    suggestion = df.sample(n=1).iloc[0]
    return f"{suggestion['tea_name']} – {suggestion['description']}"


def get_available_weather_types():

    """
    Return a list of all known weather types for which tea CSVs exist.

    Returns:
        List[str]: Supported weather keys from WEATHER_TO_FILE
    """

    return list(WEATHER_TO_FILE.keys())


def add_tea_selector_tab(notebook, weather_data):

    """
    Add a new tab to the notebook widget with tea recommendations.

    Parameters:
        notebook (ttk.Notebook): The notebook to add the tab to
        weather_data (dict): Full weather data with 'weather' key as string
    """
    
    tea_tab = tk.Frame(notebook, bg="black")
    notebook.add(tea_tab, text="Tea Selector")

    tea_tab.columnconfigure(0, weight=1)
    tea_tab.rowconfigure(4, weight=1)

    try:
        weather_main = weather_data['weather']
    except (KeyError, IndexError):
        weather_main = ""

    suggestion = get_tea_recommendation(weather_main)

    header = tk.Label(
        tea_tab,
        text="Your Weather-Based Tea Suggestion:",
        font=HEADER_FONT,
        bg="black",
        fg="#DEAFEE"
    )
    header.grid(row=0, column=0, pady=(20, 10), sticky="n")

    message = tk.Label(
        tea_tab,
        text=suggestion,
        wraplength=400,
        font=NORMAL_FONT,
        bg="black",
        fg=TAB_FG
    )
    message.grid(row=1, column=0, pady=(0, 10), sticky="n")

    # Load a random tea image from data folder
    try:
        selected_image = random.choice(TEA_IMAGES)
        image_path = os.path.join(CSV_DIR, selected_image)
        pil_image = Image.open(image_path)
        pil_image = pil_image.resize((400, 400), Image.Resampling.LANCZOS)
        tea_icon = ImageTk.PhotoImage(pil_image)
        tea_label = tk.Label(tea_tab, image=tea_icon, bg="black")
        tea_label.image = tea_icon 
        tea_label.grid(row=2, column=0, pady=(20, 10))
    except Exception as e:
        print(f"Unable to load tea icon: {e}")

    footer = tk.Label(
        tea_tab,
        text=TEA_SELECTOR_FOOTER,
        font=NORMAL_FONT,
        wraplength=1000,
        justify="center",
        bg="black",
        fg=TAB_FG
    )
    footer.grid(row=5, column=0, pady=(10, 20), sticky="s")
