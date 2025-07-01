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
        cur.execute("SELECT temp, city, timestamp FROM weather ORDER BY temp DESC LIMIT 1")
        h = cur.fetchone()
        hottest = f"{h[0]:.2f}°C in {h[1]} ({h[2]})" if h else "N/A"
        cur.execute("SELECT temp, city, timestamp FROM weather ORDER BY temp ASC LIMIT 1")
        c = cur.fetchone()
        coldest = f"{c[0]:.2f}°C in {c[1]} ({c[2]})" if c else "N/A"
        cur.execute("SELECT wind, city, timestamp FROM weather ORDER BY wind DESC LIMIT 1")
        w = cur.fetchone()
        strongest_wind = f"{w[0]:.2f} m/s in {w[1]} ({w[2]})" if w else "N/A"
        cur.execute("SELECT humidity, city, timestamp FROM weather ORDER BY humidity DESC LIMIT 1")
        h2 = cur.fetchone()
        most_humid = f"{h2[0]}% in {h2[1]} ({h2[2]})" if h2 else "N/A"
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
            "hottest": hottest,
            "coldest": coldest,
            "strongest_wind": strongest_wind,
            "most_humid": most_humid,
            "log_count": log_count,
            "avg_temp": avg_temp,
            "avg_humidity": avg_humidity,
            "avg_pressure": avg_pressure,
            "avg_wind": avg_wind,
            "most_searched": most_searched
        }
