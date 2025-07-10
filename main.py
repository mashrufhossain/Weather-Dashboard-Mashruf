import tkinter as tk
from ui.main_app import WeatherApp

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
