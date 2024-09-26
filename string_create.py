import pandas as pd
from datetime import datetime
from vehicle_profiles import VehicleProfiles


def lat_lon_to_grid(lat, lon, grid_size_km=2):
    earth_circumference_km = 40075.0
    km_per_degree = earth_circumference_km / 360.0
    try:
        lon, lat = float(lon), float(lat)
    except ValueError:
        return None, None
    return int(lon * km_per_degree / grid_size_km), int(lat * km_per_degree / grid_size_km)

def grid_to_letters(x_index, y_index):
    def index_to_letters(index):
        letters = ""
        while index >= 0:
            letters = chr(index % 26 + ord('a')) + letters
            index = index // 26 - 1
        return letters

    return f"{index_to_letters(x_index)}{index_to_letters(y_index)}"

def categorize_time(total_minutes):
    categories = ["j", "a", "b", "c", "d", "e", "f", "g", "h", "i"]
    thresholds = [270, 360, 480, 660, 780, 870, 990, 1140, 1260, 1440]
    for i, threshold in enumerate(thresholds):
        if total_minutes < threshold:
            return categories[i]
    return "Invalid time"

def process_duration(value, thresholds, categories):
    try:
        duration = float(value)
    except ValueError:
        return "n"
    for i, threshold in enumerate(thresholds):
        if duration < threshold:
            return categories[i]
    return categories[-1]

def process_coordinates(lat, lon):
    if pd.isnull(lat) or pd.isnull(lon):
        return "Invalid coordinates"
    x_index, y_index = lat_lon_to_grid(lat, lon)
    return grid_to_letters(x_index, y_index) if x_index is not None and y_index is not None else "Invalid coordinates"

def process_drive_duration(duration):
    thresholds = [7, 15, 25, 50, 100, 140, 240]
    categories = ["a", "b", "c", "d", "e", "f", "g", "h"]
    return process_duration(duration, thresholds, categories)

def process_idle_duration(duration):
    thresholds = [3, 5, 8, 11, 15, 18, 25]
    categories = ["a", "b", "c", "d", "e", "f", "g", "h"]
    return process_duration(duration, thresholds, categories)

def process_mileage(mileage):
    thresholds = [4, 8, 15, 30, 35, 38, 55, 70, 85, 100, 115]
    categories = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"]
    return process_duration(mileage, thresholds, categories)

def process_row(row):
    total_start_minutes = datetime.strptime(row['start_drive'], "%d/%m/%Y %H:%M").hour * 60 + datetime.strptime(row['start_drive'], "%d/%m/%Y %H:%M").minute
    total_end_minutes = datetime.strptime(row['end_drive'], "%d/%m/%Y %H:%M").hour * 60 + datetime.strptime(row['end_drive'], "%d/%m/%Y %H:%M").minute

    start_coords = process_coordinates(row['start_latitude'], row['start_longitude'])
    end_coords = process_coordinates(row['end_latitude'], row['end_longitude'])

    return (
        categorize_time(total_start_minutes) +
        start_coords +
        categorize_time(total_end_minutes) +
        end_coords +
        process_drive_duration(row['drive_duration']) +
        process_idle_duration(row['idle_duration']) +
        process_mileage(row['mileage'])
    )


# פונקציה לבדיקת הסתברות מחרוזת עבור מספר רכב
def check_trip_and_add_to_tree(vehicle_profiles, vehicle_id, trip_string):
    # לחשב את ההסתברות של הנסיעה
    probability = vehicle_profiles.calculate_probability_for_vehicle(vehicle_id, trip_string)

    # ערך הסף של הרכב
    threshold = vehicle_profiles.get_threshold(vehicle_id)

    # הדפסת ההסתברות והסף
    print(f"Probability of trip: {probability}, Threshold for vehicle {vehicle_id}: {threshold}")

    # בדיקה אם ההסתברות גבוהה מהסף
    if probability > threshold:
        print(f"Trip accepted for vehicle {vehicle_id}, adding to tree.")
        vehicle_profiles.add_trip(vehicle_id, trip_string)  # הוספת הנסיעה לעץ
    else:
        print(f"Trip rejected for vehicle {vehicle_id}. Probability too low.")

    return probability > threshold  # מחזיר אם הנסיעה התקבלה או לא


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
df_check = df.head(1500).copy()
# יש לוודא שהחישוב קורה רק אם יש ממצאים לעץ
df_check['probability'] = df_check['trip_description'].apply(
    lambda trip_desc: vehicle_profiles.calculate_probability_for_vehicle(vehicle_id_to_check,trip_desc)
)

# לדוגמה, המרת ערכים קטנים מאוד לפורמט מספרי ברור יותר (למניעת תצוגה של 0)
df_check['Belongs_to_vehicle'] = df_check['vehicle_id'].astype(str) == vehicle_id_to_check

# Create DataFrame for output
df_output = pd.DataFrame({
    'Index': range(1, len(df_check) + 1),
    'Trip String': df_check['trip_description'].values,
    'Probability': df_check['probability'].values,
    'Belongs to Vehicle 235268': ['Belongs' if x else "Doesn't belong" for x in df_check['Belongs_to_vehicle']]
})

# Save to Excel
output_excel_file = 'data/output_trip_probabilities.xlsx'
df_output.to_excel(output_excel_file, index=False)
print(f"Results saved to {output_excel_file}")

while True:
        # קבלת מספר רכב מהמשתמש
        vehicle_id = input("Please enter the vehicle ID (or 'exit' to quit): ")
        if vehicle_id.lower() == 'exit':
            print("Exiting the program.")
            break

        # וידוא שמספר הרכב קיים בפרופילים
        if vehicle_id not in vehicle_profiles.profiles:
            print(f"No profile found for vehicle ID: {vehicle_id}")
            continue

        # קבלת מחרוזת נסיעה מהמשתמש
        trip_string = input("Please enter the trip string to check: ")

        # חישוב הסתברות למחרוזת והשוואה לערך הסף
        accepted = check_trip_and_add_to_tree(vehicle_profiles, vehicle_id, trip_string)

        # שאלת המשתמש אם ברצונו לבדוק נסיעה נוספת
        check_another = input("Do you want to check another trip? (yes/no): ")
        if check_another.lower() != 'yes':
            print("Exiting the program.")
            break


