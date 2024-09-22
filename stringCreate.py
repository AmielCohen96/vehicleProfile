import pandas as pd
from datetime import datetime
from VehicleProfiles import VehicleProfiles

def lat_lon_to_grid(lat, lon, grid_size_km=2):
    earth_circumference_km = 40075.0
    km_per_degree = earth_circumference_km / 360.0
    try:
        lon = float(lon)
        lat = float(lat)
    except ValueError:
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
    time_format = "%d/%m/%Y %H:%M"
    try:
        time_obj = datetime.strptime(time_str, time_format)
    except ValueError:
        return "Invalid time"
    total_minutes = time_obj.hour * 60 + time_obj.minute
    categories = ["j", "a", "b", "c", "d", "e", "f", "g", "h", "i"]
    thresholds = [270, 360, 480, 660, 780, 870, 990, 1140, 1260, 1440]
    for i, threshold in enumerate(thresholds):
        if total_minutes < threshold:
            return categories[i]
    return "Invalid time"

def process_time_type(value):
    return categorize_time(value)

def process_coordinates(lat, lon):
    x_index, y_index = lat_lon_to_grid(lat, lon)
    if x_index is None or y_index is None:
        return "n"
    return grid_to_letters(x_index, y_index)

def process_duration(value, thresholds, categories):
    try:
        duration = float(value)
    except ValueError:
        return "n"
    for i, threshold in enumerate(thresholds):
        if duration < threshold:
            return categories[i]
    return categories[-1]

def process_drive_duration(value):
    thresholds = [7, 15, 25, 50, 100, 140, 240]
    categories = ["a", "b", "c", "d", "e", "f", "g", "h"]
    return process_duration(value, thresholds, categories)

def process_idle_duration(value):
    thresholds = [3, 5, 8, 11, 15, 18, 25]
    categories = ["a", "b", "c", "d", "e", "f", "g", "h"]
    return process_duration(value, thresholds, categories)

def process_mileage(value):
    thresholds = [4, 8, 15, 30, 35, 38, 55, 70, 85, 100, 115]
    categories = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"]
    return process_duration(value, thresholds, categories)

def process_row(row):
    return (process_time_type(row['start_drive']) +
            process_coordinates(row['start_latitude'], row['start_longitude']) +
            process_time_type(row['end_drive']) +
            process_coordinates(row['end_latitude'], row['end_longitude']) +
            process_drive_duration(row['drive_duration']) +
            process_idle_duration(row['idle_duration']) +
            process_mileage(row['mileage']))

# Load the CSV file into a DataFrame
csv_file_path = 'data/Trips.csv'
df = pd.read_csv(csv_file_path, low_memory=False)

# Initialize VehicleProfiles
vehicle_profiles = VehicleProfiles()

# Process the entire DataFrame at once
df['trip_description'] = df.apply(process_row, axis=1)

# Create the vehicle profiles
vehicle_trips = df.groupby('vehicle_id')['trip_description'].apply(''.join).to_dict()
for vehicle_id, trip_string in vehicle_trips.items():
    vehicle_profiles.add_trip(vehicle_id, trip_string)

# Calculate probabilities
vehicle_id_to_check = "235268"
df_check = df.head(1490).copy()
df_check['probability'] = df_check.apply(lambda row: vehicle_profiles.calculate_probability_for_vehicle(vehicle_id_to_check, row['trip_description']), axis=1)
df_check['belongs_to_vehicle'] = df_check['vehicle_id'].astype(str) == vehicle_id_to_check

sorted_trip_probabilities = df_check[['trip_description', 'probability', 'belongs_to_vehicle']].sort_values(by='probability', ascending=False)

# Create DataFrame for output
df_output = pd.DataFrame({
    'Index': range(1, len(sorted_trip_probabilities) + 1),
    'Trip String': sorted_trip_probabilities['trip_description'].values,
    'Probability': sorted_trip_probabilities['probability'].values,
    'Belongs to Vehicle 235268': ['Belongs' if x else "Doesn't belong" for x in sorted_trip_probabilities['belongs_to_vehicle']]
})

# Save to Excel
output_excel_file = 'output_trip_probabilities.xlsx'
df_output.to_excel(output_excel_file, index=False)
print(f"Results saved to {output_excel_file}")
