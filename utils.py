import csv
from datetime import datetime

def save_to_csv(city, temp, description):
    with open('history.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().isoformat(), city, temp, description])
