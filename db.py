import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.join("data", "weather.db")

class WeatherDB:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            timestamp TEXT,
            city TEXT,
            temp REAL,
            weather TEXT,
            humidity INTEGER,
            pressure INTEGER,
            wind REAL
        )
        """)
        self.conn.commit()

    def insert_weather(self, city, temp, weather, humidity, pressure, wind):
        cur = self.conn.cursor()
        cur.execute("""
        INSERT INTO weather (timestamp, city, temp, weather, humidity, pressure, wind)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            city, temp, weather, humidity, pressure, wind
        ))
        self.conn.commit()

    def get_all_history(self):
        cur = self.conn.cursor()
        cur.execute("SELECT timestamp, city, temp, weather, humidity, pressure, wind FROM weather ORDER BY timestamp DESC LIMIT 50")
        return cur.fetchall()

    def get_stats(self):
        cur = self.conn.cursor()

        # Hottest
        cur.execute("SELECT temp, city, timestamp FROM weather ORDER BY temp DESC LIMIT 1")
        h = cur.fetchone()
        if h:
            hottest_raw = h[0]
            hottest_city = h[1]
            hottest_time = h[2]
        else:
            hottest_raw = None
            hottest_city = ""
            hottest_time = ""

        # Coldest
        cur.execute("SELECT temp, city, timestamp FROM weather ORDER BY temp ASC LIMIT 1")
        c = cur.fetchone()
        if c:
            coldest_raw = c[0]
            coldest_city = c[1]
            coldest_time = c[2]
        else:
            coldest_raw = None
            coldest_city = ""
            coldest_time = ""

        # Most humid
        cur.execute("SELECT humidity, city, timestamp FROM weather ORDER BY humidity DESC LIMIT 1")
        h2 = cur.fetchone()
        most_humid = f"{h2[0]}% in {h2[1]} ({h2[2]})" if h2 else "N/A"

        # Strongest wind (parse float from stored string)
        cur.execute("SELECT wind, city, timestamp FROM weather")
        entries = cur.fetchall()
        max_speed = 0.0
        wind_entry = None
        wind_dir = None

        for e in entries:
            wind_str = e[0]
            if wind_str:
                try:
                    # Extract speed and direction
                    speed_part = wind_str.split()[0]
                    dir_part = wind_str.split(",")[1].strip() if "," in wind_str else "0°"
                    speed = float(speed_part)
                    if speed > max_speed:
                        max_speed = speed
                        wind_entry = e
                        wind_dir = dir_part
                except:
                    continue

        if wind_entry:
            strongest_wind = f"{max_speed:.2f} m/s, {wind_dir} in {wind_entry[1]} ({wind_entry[2]})"
        else:
            strongest_wind = "N/A"

        # Averages and most searched city
        cur.execute("SELECT COUNT(*), AVG(temp), AVG(humidity), AVG(pressure), AVG(wind) FROM weather")
        row = cur.fetchone()
        log_count = row[0] or 0
        avg_temp = row[1] or 0
        avg_humidity = int(row[2]) if row[2] else 0
        avg_pressure = int(row[3]) if row[3] else 0
        avg_wind = row[4] or 0

        cur.execute("SELECT city, COUNT(*) FROM weather GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1")
        city = cur.fetchone()
        most_searched = f"{city[0]} ({city[1]} times)" if city else "N/A"

        return {
            "hottest_raw": hottest_raw,
            "hottest_city": hottest_city,
            "hottest_time": hottest_time,
            "coldest_raw": coldest_raw,
            "coldest_city": coldest_city,
            "coldest_time": coldest_time,
            "strongest_wind": strongest_wind,
            "most_humid": most_humid,
            "log_count": log_count,
            "avg_temp": avg_temp,
            "avg_humidity": avg_humidity,
            "avg_pressure": avg_pressure,
            "avg_wind": avg_wind,
            "most_searched": most_searched
        }

