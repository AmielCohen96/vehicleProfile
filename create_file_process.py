import pandas as pd
from vehicle_profiles import VehicleProfiles
from string_create import process_row
from trash_hold_calc import process_excel_with_roc
from openpyxl import Workbook  # נוודא שהספריה הזו מותקנת


def load_csv(csv_file_path: str) -> pd.DataFrame:
    """Loads a CSV file into a DataFrame."""
    return pd.read_csv(csv_file_path, low_memory=False)


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Processes the DataFrame by creating a trip description column."""
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


def process_and_save_results(writer, df_output: pd.DataFrame, vehicle_id_to_check: str):
    """Processes the DataFrame with ROC and saves it to an Excel file."""
    process_excel_with_roc(df_output, vehicle_col=f'Belongs to Vehicle {vehicle_id_to_check}', belongs_value='Belongs')



    # שמירה לגליון חדש בקובץ
    df_output.to_excel(writer, sheet_name=f'Vehicle_{vehicle_id_to_check}', index=False)


def create_file():
    """Main function to execute the entire pipeline."""
    csv_file_path = 'data/Trips.csv'

    # Step 1: Load CSV data
    df = load_csv(csv_file_path)

    # יצירת קובץ אקסל חדש
    output_excel_file = 'data/output_with_roc.xlsx'  # עדכון לשם הקובץ
    with pd.ExcelWriter(output_excel_file, engine='openpyxl') as writer:
        unique_vehicle_ids = df['vehicle_id'].unique().astype(str)
        for vehicle_id in unique_vehicle_ids:
            vehicle_id_to_check = vehicle_id

            # Step 2: Process the DataFrame
            df = process_dataframe(df)

            # Step 3: Create vehicle profiles
            vehicle_profiles = create_vehicle_profiles(df)

            # Step 4: Calculate probabilities for vehicle_id_to_check
            df_check = df.head(2500).copy()
            df_check = calculate_probabilities(df_check, vehicle_profiles, vehicle_id_to_check)

            # Step 5: Create output DataFrame
            df_output = create_output_dataframe(df_check, vehicle_id_to_check)

            # Step 6: Process and save results
            process_and_save_results(writer, df_output, vehicle_id_to_check)

    print(f"Results saved to {output_excel_file}")

