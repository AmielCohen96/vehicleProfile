import pandas as pd
from datetime import datetime
import math
from TravelProfiles import TravelProfiles


def lat_lon_to_grid(lat, lon, grid_size_km=2):
    earth_circumference_km = 40075.0
    km_per_degree = earth_circumference_km / 360.0
    try:
        lon = float(lon)
        lat = float(lat)
    except ValueError:
        print(f"Error: Latitude '{lat}' or Longitude '{lon}' is not a valid float.")
        return None, None

    x_index = int(lon * km_per_degree / grid_size_km)
    y_index = int(lat * km_per_degree / grid_size_km)

    return x_index, y_index


def grid_to_letters(x_index, y_index):
    def index_to_letters(index):
        letters = ""
        while index >= 0:
            letters = chr(index % 26 + ord('a')) + letters
            index = index // 26 - 1
        return letters

    x_letters = index_to_letters(x_index)
    y_letters = index_to_letters(y_index)
    return f"{x_letters}{y_letters}"


def categorize_time(time_str):
    time_format = "%Y-%m-%d %H:%M:%S"
    try:
        time_obj = datetime.strptime(time_str, time_format)
    except ValueError:
        print(f"Error: Time '{time_str}' does not match format '{time_format}'")
        return "Invalid time"

    hour = time_obj.hour
    minute = time_obj.minute
    total_minutes = hour * 60 + minute
    if 270 <= total_minutes < 360:
        return "a"
    elif 360 <= total_minutes < 480:
        return "b"
    elif 480 <= total_minutes < 660:
        return "c"
    elif 660 <= total_minutes < 780:
        return "d"
    elif 780 <= total_minutes < 870:
        return "e"
    elif 870 <= total_minutes < 990:
        return "f"
    elif 990 <= total_minutes < 1140:
        return "g"
    elif 1140 <= total_minutes < 1260:
        return "h"
    elif 1260 <= total_minutes < 1440:
        return "i"
    elif 0 <= total_minutes < 270:
        return "j"
    else:
        return "Invalid time"


def process_time_type(value):
    return categorize_time(value)


def process_coordinates(lat, lon):
    x_index, y_index = lat_lon_to_grid(lat, lon)
    if x_index is None or y_index is None:
        return "Invalid coordinates"
    return grid_to_letters(x_index, y_index)


def process_drive_duration(value):
    try:
        duration = float(value)
    except ValueError:
        print(f"Invalid drive duration value: '{value}', setting to default.")
        return "Invalid drive duration"

    if 0 <= duration < 7:
        return "a"
    elif 7 <= duration < 15:
        return "b"
    elif 15 <= duration < 25:
        return "c"
    elif 25 <= duration < 50:
        return "d"
    elif 50 <= duration < 100:
        return "e"
    elif 100 <= duration < 140:
        return "f"
    elif 140 <= duration < 240:
        return "g"
    elif 240 <= duration:
        return "h"
    return f"Drive Duration: {value} "  # Handle any unexpected value


def process_idle_duration(value):
    try:
        duration = float(value)  # Convert to float to handle potential decimal values
    except ValueError:
        print(f"Invalid idle duration value: '{value}', setting to default.")
        return "Invalid idle duration"

    if 0 <= duration < 3:
        return "a"
    elif 3 <= duration < 5:
        return "b"
    elif 5 <= duration < 8:
        return "c"
    elif 8 <= duration < 11:
        return "d"
    elif 11 <= duration < 15:
        return "e"
    elif 15 <= duration < 18:
        return "f"
    elif 18 <= duration < 25:
        return "g"
    elif 25 <= duration:
        return "h"

    return f"Idle Duration: {value} "  # Handle any unexpected value


def process_mileage(value):
    try:
        duration = float(value)  # Convert to float to handle potential decimal values
    except ValueError:
        print(f"Invalid mileage value: '{value}', setting to default.")
        return "Invalid mileage"

    if 0 <= duration < 4:
        return "a"
    elif 4 <= duration < 8:
        return "b"
    elif 8 <= duration < 15:
        return "c"
    elif 15 <= duration < 30:
        return "d"
    elif 30 <= duration < 35:
        return "e"
    elif 35 <= duration < 38:
        return "f"
    elif 38 <= duration < 55:
        return "g"
    elif 55 <= duration < 70:
        return "h"
    elif 70 <= duration < 85:
        return "i"
    elif 85 <= duration < 100:
        return "j"
    elif 100 <= duration < 115:
        return "k"
    elif 115 <= duration:
        return "l"

    return f"Mileage: {value} "  # Handle any unexpected value


# Load the CSV file into a DataFrame
csv_file_path = 'C:\\Users\\User\\PycharmProjects\\driverProfile\\data\\Trips.csv'
df = pd.read_csv(csv_file_path, low_memory=False)

# Initialize TravelProfiles
travel_profiles = TravelProfiles()

# Print unique vehicle numbers to verify 235268 is present
print("Unique vehicle numbers in the CSV file:")
print(df['vehicle_id'].unique())

# Process a single row
def process_row(row):
    result = ""
    result += process_time_type(row['start_drive'])
    result += process_coordinates(row['start_latitude'], row['start_longitude'])
    result += process_time_type(row['end_drive'])
    result += process_coordinates(row['end_latitude'], row['end_longitude'])
    result += process_drive_duration(row['drive_duration'])
    result += process_idle_duration(row['idle_duration'])
    result += process_mileage(row['mileage'])
    return result

# Iterate over the first 50 rows and process them
for index, row in df.head(2000).iterrows():
    print(f"Processing row {index} with vehicle_id {row['vehicle_id']}")
    row_description = process_row(row)
    print(f"Processed trip description: {row_description}")
    # Get the vehicle number from the row and add the trip to the corresponding Trie
    vehicle_id = row['vehicle_id']
    print("vehicle id: " + f"{vehicle_id}")
    travel_profiles.add_trip(vehicle_id, row_description)
print("Trie for vehicle 235268:")
travel_profiles.display_profile("235268")
