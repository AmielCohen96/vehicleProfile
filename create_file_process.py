import pandas as pd
from vehicle_profiles import VehicleProfiles
from string_create import process_row
from trash_hold_calc import process_excel_with_roc
from openpyxl.drawing.image import Image
import os


def load_csv(csv_file_path: str) -> pd.DataFrame:
    """Loads a CSV file into a DataFrame."""
    return pd.read_csv(csv_file_path, low_memory=False)


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Processes the DataFrame by creating a trip description column."""
    if 'trip_description' not in df.columns:
        df['trip_description'] = df.apply(process_row, axis=1)
    return df


def create_vehicle_profiles(df: pd.DataFrame) -> VehicleProfiles:
    """Creates vehicle profiles based on trip descriptions."""
    vehicle_profiles = VehicleProfiles()
    vehicle_trips = df.groupby('vehicle_id')['trip_description'].apply(''.join).to_dict()

    for vehicle_id, trip_string in vehicle_trips.items():
        vehicle_profiles.add_trip(vehicle_id, trip_string)

    return vehicle_profiles


def calculate_probabilities(df: pd.DataFrame, vehicle_profiles: VehicleProfiles,
                            vehicle_id_to_check: str) -> pd.DataFrame:
    """Calculates the probability for a specific vehicle across the DataFrame."""
    df['probability'] = df['trip_description'].apply(
        lambda trip_desc: vehicle_profiles.calculate_probability_for_vehicle(vehicle_id_to_check, trip_desc)
    )

    df['Belongs_to_vehicle'] = df['vehicle_id'].astype(str) == vehicle_id_to_check
    return df


def create_output_dataframe(df: pd.DataFrame, vehicle_id_to_check: str) -> pd.DataFrame:
    """Creates the output DataFrame for saving to Excel."""
    return pd.DataFrame({
        'Index': range(1, len(df) + 1),
        'Trip String': df['trip_description'].values,
        'Probability': df['probability'].values,
        f'Belongs to Vehicle {vehicle_id_to_check}': [
            'Belongs' if x else "Doesn't belong" for x in df['Belongs_to_vehicle']
        ]
    })


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


def process_and_save_results(writer, df_output: pd.DataFrame, vehicle_id_to_check: str,
                             vehicle_profiles: VehicleProfiles, output_dir: str = 'media'):
    """Processes the DataFrame with ROC and saves it to an Excel sheet, and updates the vehicle profile threshold."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Compute ROC and get the ROC curve image path
        roc_curve_image = process_excel_with_roc(
            df=df_output,
            vehicle_col=f'Belongs to Vehicle {vehicle_id_to_check}',
            belongs_value='Belongs',
            vehicle_id=vehicle_id_to_check,
            output_dir=output_dir,
        )
    except ValueError as e:
        print(f"Skipping ROC for vehicle {vehicle_id_to_check} due to error: {e}")
        roc_curve_image = None
        return  # במקרה של שגיאה, לא להמשיך כדי להימנע מעדכון שגוי של הסף

    # עדכון threshold בפרופיל של הרכב לאחר החישוב
    optimal_threshold = df_output['Threshold'].dropna().iloc[0]  # הנחת שזה הערך שחושב
    vehicle_profiles.set_threshold(vehicle_id_to_check, optimal_threshold)

    # Save DataFrame to the specific sheet
    sheet_name = f'Vehicle_{vehicle_id_to_check}'
    df_output.to_excel(writer, sheet_name=sheet_name, index=False)

    # Access the workbook and sheet via the writer
    workbook = writer.book
    if sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
    else:
        sheet = workbook.create_sheet(sheet_name)

    # Insert the image into the sheet
    if roc_curve_image and os.path.exists(roc_curve_image):
        img = Image(roc_curve_image)
        # Adjust the position as needed; 'A10' is an example
        sheet.add_image(img, 'A10')
    else:
        print(f"No ROC curve image to insert for vehicle {vehicle_id_to_check}.")


def create_file():
    """Main function to execute the entire pipeline."""
    csv_file_path = 'data/Trips.csv'

    # Step 1: Load CSV data
    df = load_csv(csv_file_path)

    # Step 2: Process the DataFrame once before the loop
    df = process_dataframe(df)

    # Step 3: Create vehicle profiles
    vehicle_profiles = create_vehicle_profiles(df)

    # Create a new Excel file
    output_excel_file = 'data/output_with_roc.xlsx'
    with pd.ExcelWriter(output_excel_file, engine='openpyxl') as writer:
        unique_vehicle_ids = df['vehicle_id'].unique().astype(str)
        for vehicle_id in unique_vehicle_ids:
            vehicle_id_to_check = vehicle_id

            # Step 4: Calculate probabilities for vehicle_id_to_check
            df_belongs = df[df['vehicle_id'].astype(str) == vehicle_id_to_check].copy()
            df_not_belongs = df[df['vehicle_id'].astype(str) != vehicle_id_to_check].copy()

            # Sample negative examples equal to the number of positive examples
            if len(df_not_belongs) >= len(df_belongs):
                df_not_belongs_sample = df_not_belongs.sample(n=len(df_belongs), random_state=42)
            else:
                df_not_belongs_sample = df_not_belongs.copy()

            # Combine positive and negative examples
            df_check = pd.concat([df_belongs, df_not_belongs_sample], ignore_index=True)

            # Step 5: Calculate probabilities
            df_check = calculate_probabilities(df_check, vehicle_profiles, vehicle_id_to_check)

            # Step 6: Create output DataFrame
            df_output = create_output_dataframe(df_check, vehicle_id_to_check)

            # Step 7: Process and save results, including inserting ROC image and updating threshold
            process_and_save_results(writer, df_output, vehicle_id_to_check, vehicle_profiles)

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
