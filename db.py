"""
db.py

Database module for Weather Dashboard.

Provides WeatherDB class to manage SQLite database:
- Establish connection to data/weather.db
- Initialize the weather table if needed
- Insert new weather records with timestamps
- Retrieve recent history and compute various statistics
"""

import os
import sqlite3
from datetime import datetime

# Define the path for the SQLite database file inside the "data/" directory
DB_PATH = os.path.join("data", "weather.db")

class WeatherDB:

    '''
    A class to manage storing and retrieving weather data using a SQLite database file.
    '''

    def __init__(self, db_path=DB_PATH):
        # Establish a connection to the SQLite database
        self.conn = sqlite3.connect(db_path)

        # Create the "weather" table if it does not exist
        self.create_table()

    def create_table(self):

        '''
        Create the "weather" table to store weather records. Fields cover various weather parameters.
        '''

        # Get a cursor object for executing SQL statements
        cur = self.conn.cursor()

        # Execute a SQL command to create the table if it does not already exist
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

        # Commit the changes to persist the table creation
        self.conn.commit()

    def insert_weather(self, city, temp, feels_like, weather, humidity, pressure,
                       visibility, wind, sea_level, grnd_level, sunrise, sunset):
        
        '''
        Insert a new weather record into the database with the current timestamp.

        Parameters:
            city (str): Name of the city
            temp (float): Current temperature
            feels_like (float): "Feels like" temperature
            weather (str): Weather description
            humidity (int): Humidity percentage
            pressure (int): Atmospheric pressure in hPa
            visibility (float): Visibility in meters
            wind (str): Wind speed and direction (e.g., "5.1 m/s, NW")
            sea_level (float): Sea level pressure
            grnd_level (float): Ground level pressure
            sunrise (str): Sunrise time as text
            sunset (str): Sunset time as text
        '''

        # Prepare a cursor for insertion
        cur = self.conn.cursor()

        # Execute the INSERT statement, including a formatted timestamp on line 83
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

        '''
        Retrieve the most recent 50 weather entries, ordered by timestamp descending.

        Returns:
            list of tuples: Each tuple represents a stored weather record.
        '''

        # Prepare cursor for querying the database
        cur = self.conn.cursor()

        # Execute the SELECT statement to fetch the last 50 entries
        cur.execute("""
            SELECT timestamp, city, temp, feels_like, weather, humidity, pressure,
            visibility, wind, sea_level, grnd_level, sunrise, sunset
            FROM weather 
            ORDER BY timestamp DESC 
            LIMIT 50
        """
        )

        # Return all fetched rows as a list
        return cur.fetchall()

    def get_stats(self):

        '''
        Compute various statistics from the stored weather data.

        Returns:
            dict: Contains keys for extremes (hottest, coldest, most humid, strongest wind, 
                  highest sea level, lowest ground level), averages, and most-searched city.
        '''

        # Prepare cursor for querying the database
        cur = self.conn.cursor()
        try:
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
                        # Split speed and direction
                        speed_part = wind_str.split()[0]
                        dir_part = wind_str.split(",")[1].strip() if "," in wind_str else "N/A"
                        speed = float(speed_part)
                        if speed > max_speed:
                            max_speed = speed
                            wind_entry = e
                            wind_dir = dir_part
                    except ValueError:
                        # Skip if parsing fails
                        continue

            if wind_entry:
                strongest_wind_value = f"{max_speed:.2f} m/s, {wind_dir}"
                strongest_wind_city = wind_entry[1]
                strongest_wind_time = wind_entry[2]
            else:
                strongest_wind_value = "N/A"
                strongest_wind_city = "N/A"
                strongest_wind_time = "N/A"

            # Basic count and averages for temperature, humidity, pressure
            cur.execute("SELECT COUNT(*), AVG(temp), AVG(humidity), AVG(pressure) FROM weather")
            row = cur.fetchone()
            log_count = row[0] or 0
            avg_temp = row[1] or 0
            avg_humidity = int(row[2]) if row[2] else 0
            avg_pressure = int(row[3]) if row[3] else 0

            # Average wind speed calculation
            cur.execute("SELECT AVG(wind_speed) FROM (SELECT CAST(SUBSTR(wind, 1, INSTR(wind, ' ') - 1) AS REAL) as wind_speed FROM weather WHERE wind LIKE '% m/s%')")
            wind_row = cur.fetchone()
            avg_wind = wind_row[0] if wind_row and wind_row[0] is not None else 0

            # Identify most-searched city by entry count
            cur.execute("SELECT city, COUNT(*) FROM weather GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1")
            city = cur.fetchone()
            most_searched = f"{city[0]} ({city[1]} times)" if city else "N/A"

            # Sea level pressure averages and maximum
            cur.execute("SELECT AVG(sea_level) FROM weather WHERE sea_level IS NOT NULL")
            row = cur.fetchone()
            avg_sea_level = round(row[0], 2) if row and row[0] is not None else "N/A"
            cur.execute("SELECT sea_level, city, timestamp FROM weather WHERE sea_level IS NOT NULL ORDER BY sea_level DESC LIMIT 1")
            highest_sea = cur.fetchone()
            if highest_sea:
                highest_sea_value = f"{highest_sea[0]:.2f} hPa"
                highest_sea_city = highest_sea[1]
                highest_sea_time = highest_sea[2]
            else:
                highest_sea_value = highest_sea_city = highest_sea_time = "N/A"

            # Ground level pressure averages and minimum
            cur.execute("SELECT AVG(grnd_level) FROM weather WHERE grnd_level IS NOT NULL")
            row = cur.fetchone()
            avg_ground_level = round(row[0], 2) if row and row[0] is not None else "N/A"

            cur.execute("SELECT grnd_level, city, timestamp FROM weather WHERE grnd_level IS NOT NULL ORDER BY grnd_level ASC LIMIT 1")
            lowest_ground = cur.fetchone()
            if lowest_ground:
                lowest_ground_value = f"{lowest_ground[0]:.2f} hPa"
                lowest_ground_city = lowest_ground[1]
                lowest_ground_time = lowest_ground[2]
            else:
                lowest_ground_value = lowest_ground_city = lowest_ground_time = "N/A"

            # Earliest sunrise and latest sunset time
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

            # Compile all stats into a dictionary and return
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
        except sqlite3.DatabaseError as e:
            # Handle any database errors gracefully
            print(f"Database error during stats fetch: {e}")
            return {}
