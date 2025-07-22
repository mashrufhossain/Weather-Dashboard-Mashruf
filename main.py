"""
main.py

Entry point for the Weather Dashboard.
Creates the root Tk window, initializes WeatherApp, and starts the main loop.
"""

import tkinter as tk                    # GUI toolkit for Python
from gui.main_app import WeatherApp     # Main application class
import logging                          # Python’s built-in logging module


# Configure the logging system once at startup:
logging.basicConfig(
    level=logging.ERROR,                                # Only log ERROR and above (suppress DEBUG/INFO)
    format="%(asctime)s %(levelname)s %(message)s",     # Log timestamp, level, and message
    datefmt="%H:%M:%S"                                  # Timestamp format (hours:minutes:seconds)
)


if __name__ == "__main__":
    # Create the main Tkinter window
    root = tk.Tk()

    # Initialize your WeatherApp with the root window
    app = WeatherApp(root)
    
    # Start the Tkinter event loop (blocks until window is closed)
    root.mainloop()