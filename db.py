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
                feels_like REAL,
                weather TEXT,
                humidity INTEGER,
                pressure INTEGER,
                visibility REAL,
                wind TEXT,
                sea_level REAL,
                grnd_level REAL,
                sunrise TEXT,
                sunset TEXT
            )
        """)
        self.conn.commit()

    def insert_weather(self, city, temp, feels_like, weather, humidity, pressure,
                   visibility, wind, sea_level, grnd_level,
                   sunrise, sunset):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO weather (timestamp, city, temp, feels_like, weather,
            humidity, pressure, visibility, wind,
            sea_level, grnd_level, sunrise, sunset)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            city, temp, feels_like, weather,
            humidity, pressure, visibility, wind,
            sea_level, grnd_level, sunrise, sunset
        ))
        self.conn.commit()

    def get_all_history(self):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT timestamp, city, temp, feels_like, weather, humidity, pressure,
            visibility, wind, sea_level, grnd_level, sunrise, sunset
            FROM weather ORDER BY timestamp DESC LIMIT 50
        """)
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
            hottest_city = "N/A"
            hottest_time = "N/A"

        # Coldest
        cur.execute("SELECT temp, city, timestamp FROM weather ORDER BY temp ASC LIMIT 1")
        c = cur.fetchone()
        if c:
            coldest_raw = c[0]
            coldest_city = c[1]
            coldest_time = c[2]
        else:
            coldest_raw = None
            coldest_city = "N/A"
            coldest_time = "N/A"

        # Most humid
        cur.execute("SELECT humidity, city, timestamp FROM weather ORDER BY humidity DESC LIMIT 1")
        h2 = cur.fetchone()
        if h2:
            most_humid_value = f"{h2[0]}%"
            most_humid_city = h2[1]
            most_humid_time = h2[2]
        else:
            most_humid_value = "N/A"
            most_humid_city = "N/A"
            most_humid_time = "N/A"

        # Strongest wind
        cur.execute("SELECT wind, city, timestamp FROM weather")
        entries = cur.fetchall()
        max_speed = 0.0
        wind_entry = None
        wind_dir = None

        for e in entries:
            wind_str = e[0]
            if wind_str:
                try:
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
            strongest_wind_value = f"{max_speed:.2f} m/s, {wind_dir}"
            strongest_wind_city = wind_entry[1]
            strongest_wind_time = wind_entry[2]
        else:
            strongest_wind_value = "N/A"
            strongest_wind_city = "N/A"
            strongest_wind_time = "N/A"

        # Averages and most searched
        cur.execute("SELECT COUNT(*), AVG(temp), AVG(humidity), AVG(pressure) FROM weather")
        row = cur.fetchone()
        log_count = row[0] or 0
        avg_temp = row[1] or 0
        avg_humidity = int(row[2]) if row[2] else 0
        avg_pressure = int(row[3]) if row[3] else 0

        cur.execute("SELECT AVG(wind_speed) FROM (SELECT CAST(SUBSTR(wind, 1, INSTR(wind, ' ') - 1) AS REAL) as wind_speed FROM weather WHERE wind LIKE '% m/s%')")
        wind_row = cur.fetchone()
        avg_wind = wind_row[0] if wind_row and wind_row[0] is not None else 0

        cur.execute("SELECT city, COUNT(*) FROM weather GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1")
        city = cur.fetchone()
        most_searched = f"{city[0]} ({city[1]} times)" if city else "N/A"

        # Sea level stats
        cur.execute("SELECT AVG(sea_level) FROM weather WHERE sea_level IS NOT NULL")
        row = cur.fetchone()
        if row and row[0] is not None:
            avg_sea_level = round(row[0], 2)
        else:
            avg_sea_level = "N/A"

        cur.execute("SELECT sea_level, city, timestamp FROM weather WHERE sea_level IS NOT NULL ORDER BY sea_level DESC LIMIT 1")
        highest_sea = cur.fetchone()
        if highest_sea:
            highest_sea_value = f"{highest_sea[0]:.2f} hPa"
            highest_sea_city = highest_sea[1]
            highest_sea_time = highest_sea[2]
        else:
            highest_sea_value = highest_sea_city = highest_sea_time = "N/A"

        # Ground level stats
        cur.execute("SELECT AVG(grnd_level) FROM weather WHERE grnd_level IS NOT NULL")
        row = cur.fetchone()
        if row and row[0] is not None:
            avg_ground_level = round(row[0], 2)
        else:
            avg_ground_level = "N/A"

        cur.execute("SELECT grnd_level, city, timestamp FROM weather WHERE grnd_level IS NOT NULL ORDER BY grnd_level ASC LIMIT 1")
        lowest_ground = cur.fetchone()
        if lowest_ground:
            lowest_ground_value = f"{lowest_ground[0]:.2f} hPa"
            lowest_ground_city = lowest_ground[1]
            lowest_ground_time = lowest_ground[2]
        else:
            lowest_ground_value = lowest_ground_city = lowest_ground_time = "N/A"

        # Sunrise/Sunset stats
        cur.execute("SELECT sunrise, city FROM weather ORDER BY sunrise ASC LIMIT 1")
        earliest_sunrise = cur.fetchone()
        if earliest_sunrise:
            earliest_sunrise_time = earliest_sunrise[0]
            earliest_sunrise_city = earliest_sunrise[1]
        else:
            earliest_sunrise_time = earliest_sunrise_city = "N/A"

        cur.execute("SELECT sunset, city FROM weather ORDER BY sunset DESC LIMIT 1")
        latest_sunset = cur.fetchone()
        if latest_sunset:
            latest_sunset_time = latest_sunset[0]
            latest_sunset_city = latest_sunset[1]
        else:
            latest_sunset_time = latest_sunset_city = "N/A"

        return {
            "hottest_raw": hottest_raw,
            "hottest_city": hottest_city,
            "hottest_time": hottest_time,
            "coldest_raw": coldest_raw,
            "coldest_city": coldest_city,
            "coldest_time": coldest_time,
            "strongest_wind": strongest_wind_value,
            "strongest_wind_city": strongest_wind_city,
            "strongest_wind_time": strongest_wind_time,
            "most_humid": most_humid_value,
            "most_humid_city": most_humid_city,
            "most_humid_time": most_humid_time,
            "log_count": log_count,
            "avg_temp": avg_temp,
            "avg_humidity": avg_humidity,
            "avg_pressure": avg_pressure,
            "avg_wind": avg_wind,
            "most_searched": most_searched,
            "avg_sea_level": avg_sea_level,
            "highest_sea_value": highest_sea_value,
            "highest_sea_city": highest_sea_city,
            "highest_sea_time": highest_sea_time,
            "avg_ground_level": avg_ground_level,
            "lowest_ground_value": lowest_ground_value,
            "lowest_ground_city": lowest_ground_city,
            "lowest_ground_time": lowest_ground_time,
            "earliest_sunrise_time": earliest_sunrise_time,
            "earliest_sunrise_city": earliest_sunrise_city,
            "latest_sunset_time": latest_sunset_time,
            "latest_sunset_city": latest_sunset_city,
        }
