# 🌤️ Weather Dashboard — Mashruf Edition

Welcome to the **Weather Dashboard**, a beautiful, data-rich desktop weather application built in Python using Tkinter and SQLite.  
This app was created as part of a capstone project to showcase strong software design, data visualization, and creative UI flair — all in one weather-focused experience!

---

## 🚀 Features

### Core Features

- **Current Weather Viewer**
  - Get up-to-date weather data for any city worldwide.
  - Includes temperature, feels like, condition, humidity, wind (with direction), pressure, visibility, sunrise, and sunset times.
  - Supports both Celsius and Fahrenheit.

- **5-Day Forecast**
  - See a visually organized 5-day forecast with weather icons, date, min/max temps, humidity, wind, and visibility.
  - Cleanly designed "cards" with consistent styling and clear separation.

- **Temperature Unit Toggle**
  - Switch easily between °C and °F on the fly.

- **History Tracking**
  - Saves all searched weather data into a local SQLite database.
  - View all past searches in a sortable table.

- **SQL-based Statistics**
  - Displays hottest and coldest recorded temps.
  - Tracks strongest wind, most humid condition, average temperature, average humidity, and more.
  - Stats update live as more cities are searched.

### Visual & Interactive Enhancements

- Modern dark theme with carefully chosen highlight colors (yellow, aqua, purple).
- Weather condition icons and emoji for instant visual cues.
- Forecast header and cards dynamically update and center beautifully.
- Detailed error handling and user-friendly messages.

---

## 🗂️ Project Structure
Weather-Dashboard-Mashruf/
├── assets/ # (Optional) Images, icons
├── data/ # Local SQLite database and CSV logs
├── docs/ # Documentation files
├── tests/ # Future: Unit tests
├── api.py # Weather API logic (OpenWeatherMap)
├── db.py # Database (SQLite) logic
├── main.py # Main Tkinter app entry point
├── history.py # Weather history logic
├── graph.py # Graph plotting code (matplotlib, future use)
├── stats.py # SQL statistics logic
├── mascot.py # Mascot visuals and personality (future option)
├── requirements.txt # Python dependencies
└── README.md # This file

---

## 💻 Installation

1. Clone this repo:
'''
git clone https://github.com/yourusername/Weather-Dashboard-Mashruf.git
cd Weather-Dashboard-Mashruf
'''

2. Create and activate a virtual environment:
'''
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
'''

3. Install requirements:
'''
pip install -r requirements.txt
'''

4. Add your OpenWeatherMap API key to a .env file:
'''
OPENWEATHER_API_KEY=your_api_key_here
'''

5. Run the app:
'''
python main.py
'''

---

## ⚙️ Technologies

Python 3.9+
Tkinter (for GUI)
SQLite (local data storage)
OpenWeatherMap API (real-time weather data)
Matplotlib (future: graphs and trends)

---

## ✨ Future Ideas

Add achievement badges for using the app multiple days.
Animated mascots or weather personality.
Interactive activity suggestions based on current weather.
Local sound effects for different weather types.
Enhanced trend detection and graph overlays.

---

## ❤️ Acknowledgements

Thanks to the JTC Fellows at Columbia University and the supportive community for inspiration and feedback.

---

## 💬 Feedback

Pull requests, issues, and suggestions are always welcome!

Enjoy exploring the skies with your own personal weather companion! ☀️🌧️❄️