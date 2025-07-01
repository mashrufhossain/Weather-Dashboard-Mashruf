import csv

def read_all_entries(file_path='history.csv'):
    """Return all rows from the CSV file."""
    try:
        with open(file_path, 'r') as file:
            rows = list(csv.reader(file))
            return rows
    except FileNotFoundError:
        return []
