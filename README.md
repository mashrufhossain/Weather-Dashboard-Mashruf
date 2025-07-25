# 🌤️ Weather Dashboard — What's In Your Sky?

Welcome to the **Weather Dashboard**, a sleek, modular, and personalized desktop weather app built with Python and Tkinter.  
Developed as a capstone project, it blends real-time weather data, statistical insight, UI polish, and creative enhancements like mood-based tea recommendations.

---

## 🚀 Features

- **Live Weather Fetching**  
  - Search any city to instantly see temperature, humidity, pressure, wind (with direction), visibility, sunrise/sunset, and conditions.  
  - Supports °C/°F toggle without refetching data.

- **5-Day Forecast**  
  - Shows future weather in a horizontal card layout.  
  - Displays min/max temps, humidity, wind, and weather emojis/icons.

- **Weather History**  
  - Automatically logs each day’s weather into a SQLite3 database file.  
  - View a scrollable history of past entries.

- **History Statistics**  
  - Extracts trends from your local history.  
  - Tracks min/max temperatures, average values, and weather frequency.

- **Tea Recommendation System ☕**  
  - Suggests a matching tea based on weather and mood.  
  - Pulls from 4 CSV datasets (clear, cloudy, rainy, cold) and includes images for a cozy UX.

---

## 🎨 Visual & Interaction Enhancements

- **Dark Theme UI**  
  - Black background with rich highlight colors (gold, aqua, purple).  
  - Defined in `styles.py`.

- **Automatic Forecast Refresh**  
  - Forecast data and current weather are automatically refreshed every minute.  
  - A visible countdown timer indicates the next refresh cycle.

- **Predictive City Search**  
  - Intelligent geocoding-based autocomplete helps users quickly find valid cities.

- **Error Handling**  
  - Friendly error messages for API/network issues or invalid cities.

---

## 🗂️ File Structure

```text
Weather-Dashboard-Mashruf/
├── .venv/                             # Virtual environment (gitignored)
├── data/                              # Local assets and logs
│   ├── cold_weather_teas.csv
│   ├── cloudy_weather_teas.csv
│   ├── clear_weather_teas.csv
│   ├── rainy_weather_teas.csv
│   ├── tea1.jpg ... tea10.jpg
│   ├── weather.db
│   └── weather_history.csv
├── features/                          # Core weather features
│   ├── forecast.py
│   ├── history.py
│   ├── stats.py
│   └── tea_selector.py
├── gui/                               # UI management
│   └── main_app.py
├── api.py                             # OpenWeatherMap API logic
├── constants.py                       # Shared constants & settings
├── db.py                              # SQLite logic
├── main.py                            # App entry point
├── styles.py                          # Colors and fonts
├── utils.py                           # Helpers: unit conversion, direction, etc.
├── .env                               # API key (gitignored)
├── .gitignore                         # Venv, .env, and cache files
├── requirements.txt                   # Project dependencies
└── README.md                          # This file
```

---

## 💻 Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/Weather-Dashboard-Mashruf.git
   cd Weather-Dashboard-Mashruf
   ```

2. **Set up the virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your API key**  
   Create a `.env` file in the root with this content:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

5. **Run the app**
   ```bash
   python main.py
   ```

---

## ⚙️ Tech Stack

- **Python 3.9+**
- **Tkinter** – GUI
- **OpenWeatherMap API** – Real-time weather
- **CSV** – Local data logging + tea logic
- **dotenv** – Secure API key management
- **requests** – API calls

---

## 🔮 Future Enhancements

- Add Matplotlib graphs for weather trends
- Achievement badges for consistent usage
- Animated weather mascots
- Sound cues for rain, wind, sunshine

---

## ❤️ Credits

Special thanks to:

- **JTC Fellows @ Columbia University** for the capstone structure and support.
- All classmates and mentors who gave feedback and tested the early builds!

---

## 💬 Contribute

Pull requests, issues, and feature ideas are welcome.  
Let's make weather apps a little more fun.🌦️