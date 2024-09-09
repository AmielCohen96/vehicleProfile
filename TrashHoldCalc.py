import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score
from openpyxl import load_workbook
from openpyxl.drawing.image import Image


def process_excel_with_roc(file_path, thresholds, vehicle_col, belongs_value="Belongs"):
    # Load the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Create space for new headers and columns
    existing_columns = df.shape[1]
    for i in range(3):
        df.insert(existing_columns + i, f'Space_{i + 1}', np.nan)

    # Add new headers if not present
    new_headers = ['Threshold', 'TP', 'TN', 'FP', 'FN', 'Recall', 'Precision', 'Specificity']
    for header in new_headers:
        df[header] = np.nan

    # Calculate the metrics for each threshold
    for threshold in thresholds:
        tp = tn = fp = fn = 0
        numeric_column = 'Probability'  # Replace this with your actual numeric column

        for _, row in df.iterrows():
            value = row[vehicle_col]
            num_value = row[numeric_column]

            if num_value > threshold:
                if value == belongs_value:
                    tp += 1
                else:
                    tn += 1
            else:
                if value == belongs_value:
                    fp += 1
                else:
                    fn += 1

        # Calculate metrics
        recall = tp / (tp + fn) if tp + fn > 0 else 0
        precision = tp / (tp + fp) if tp + fp > 0 else 0
        specificity = tn / (tn + fp) if tn + fp > 0 else 0

        # Add values to the DataFrame
        new_data = {'Threshold': threshold, 'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn,
                    'Recall': recall, 'Precision': precision, 'Specificity': specificity}
        first_empty_row = df[df['Threshold'].isna()].index[0]
        for header, value in new_data.items():
            df.at[first_empty_row, header] = value

    # Now calculate ROC and AUC
    true_labels = np.where(df[vehicle_col] == belongs_value, 1, 0)  # Convert to binary labels
    probabilities = df['Probability'].values  # Replace 'Index' with your numeric score column

    # Compute ROC curve
    fpr, tpr, _ = roc_curve(true_labels, probabilities)
    auc_value = roc_auc_score(true_labels, probabilities)

    # Plot the ROC curve
    plt.figure()
    plt.plot(fpr, tpr, label=f'ROC curve (area = {auc_value:.2f})')
    plt.plot([0, 1], [0, 1], linestyle='--')  # Plotting the diagonal
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend(loc="lower right")

    # Save the plot as an image
    roc_curve_image = 'roc_curve.png'
    plt.savefig(roc_curve_image)
    plt.close()

    # Save the updated DataFrame back to Excel
    output_file = 'output_with_roc.xlsx'
    df.to_excel(output_file, index=False)

    # Insert the ROC curve image into the Excel file
    workbook = load_workbook(output_file)
    sheet = workbook.active
    img = Image(roc_curve_image)
    sheet.add_image(img, 'P5')  # Adjust the position as needed

    # Save the Excel file with the image
    workbook.save(output_file)


# Example usage
file_path = 'output_trip_probabilities.xlsx'
thresholds = [0.00001, 0.00002, 0.00005]
process_excel_with_roc(file_path, thresholds, 'Belongs to Vehicle 235268')
