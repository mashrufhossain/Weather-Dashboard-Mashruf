import csv
from datetime import datetime

def save_to_csv(city, temp, description, file_path='history.csv'):
    """Save weather data to CSV file with timestamp."""
    with open(file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), city, temp, description])
