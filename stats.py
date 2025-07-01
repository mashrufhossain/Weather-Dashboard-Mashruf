import csv

def calculate_stats(file_path='history.csv'):
    """Calculate min/max temperatures and count weather types."""
    temps = []
    weather_counts = {}

    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 4:
                    continue
                temp = float(row[2])
                description = row[3].lower()
                temps.append(temp)
                weather_counts[description] = weather_counts.get(description, 0) + 1

        if not temps:
            return None

        return {
            "min": min(temps),
            "max": max(temps),
            "counts": weather_counts
        }
    except FileNotFoundError:
        return None