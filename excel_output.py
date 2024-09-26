# import pandas as pd
# from vehicle_profiles import VehicleProfiles
# from string_create import process_row
# from trash_hold_calc import process_excel_with_roc
#
#
# # Load the CSV file into a DataFrame
# csv_file_path = 'data/Trips.csv'
# df = pd.read_csv(csv_file_path, low_memory=False)
#
# # Initialize VehicleProfiles
# vehicle_profiles = VehicleProfiles()
#
#
#
# # Process the entire DataFrame at once
# df['trip_description'] = df.apply(process_row, axis=1)
#
# # Create the vehicle profiles
# vehicle_trips = df.groupby('vehicle_id')['trip_description'].apply(''.join).to_dict()
# for vehicle_id, trip_string in vehicle_trips.items():
#     vehicle_profiles.add_trip(vehicle_id, trip_string)
#
# vehicle_id_to_check = '235268'
# # Calculate probabilities
# df_check = df.head(2500).copy()
#
# # יש לוודא שהחישוב קורה רק אם יש ממצאים לעץ
# df_check['probability'] = df_check['trip_description'].apply(
#     lambda trip_desc: vehicle_profiles.calculate_probability_for_vehicle(vehicle_id_to_check, trip_desc)
# )
#
# # לדוגמה, המרת ערכים קטנים מאוד לפורמט מספרי ברור יותר (למניעת תצוגה של 0)
# df_check['Belongs_to_vehicle'] = df_check['vehicle_id'].astype(str) == vehicle_id_to_check
#
# # Create DataFrame for output
# df_output = pd.DataFrame({
#     'Index': range(1, len(df_check) + 1),
#     'Trip String': df_check['trip_description'].values,
#     'Probability': df_check['probability'].values,
#     'Belongs to Vehicle 235268': ['Belongs' if x else "Doesn't belong" for x in df_check['Belongs_to_vehicle']]
#
# })
#
# process_excel_with_roc(df_output, vehicle_col='Belongs to Vehicle 235268', belongs_value='Belongs')
#
#
#
#
# # # Save to Excel
# # output_excel_file = 'data/output_trip_probabilities.xlsx'
# # df_output.to_excel(output_excel_file, index=False)
# # print(f"Results saved to {output_excel_file}")
# #import pandas as pd
