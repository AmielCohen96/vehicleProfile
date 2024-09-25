import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score
from openpyxl import load_workbook
from openpyxl.drawing.image import Image

def process_excel_with_roc(file_path, vehicle_col, belongs_value="Belongs"):
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

    # Convert labels to binary
    true_labels = np.where(df[vehicle_col] == belongs_value, 1, 0)  # Convert to binary labels
    probabilities = df['Probability'].values  # Replace 'Probability' with your numeric score column

    # Ensure probabilities are valid numbers
    if np.any(np.isnan(probabilities)) or np.any(np.isinf(probabilities)):
        raise ValueError("Probability column contains invalid values.")

    # Compute ROC curve
    fpr, tpr, thresholds = roc_curve(true_labels, probabilities)
    auc_value = roc_auc_score(true_labels, probabilities)

    # Find the optimal threshold based on Youden's J statistic
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = thresholds[optimal_idx]

    print(f"Optimal threshold: {optimal_threshold}")

    # Calculate metrics for the optimal threshold
    tp = tn = fp = fn = 0
    for _, row in df.iterrows():
        value = row[vehicle_col]
        num_value = row['Probability']

        if num_value > optimal_threshold:
            if value == belongs_value:
                tp += 1
            else:
                fp += 1  # Increment FP here if the value does not belong
        else:
            if value == belongs_value:
                fn += 1  # Increment FN if it belongs but was predicted as negative
            else:
                tn += 1  # Increment TN if it does not belong and was predicted as negative

    # Calculate metrics
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    # Add values to the DataFrame for the optimal threshold
    new_data = {'Threshold': optimal_threshold, 'TP': tp, 'TN': tn, 'FP': fp, 'FN': fn,
                'Recall': recall, 'Precision': precision, 'Specificity': specificity}
    first_empty_row = df[df['Threshold'].isna()].index[0]
    for header, value in new_data.items():
        df.at[first_empty_row, header] = value

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
    output_file = r'data/output_with_roc.xlsx'
    df.to_excel(output_file, index=False)

    # Insert the ROC curve image into the Excel file
    workbook = load_workbook(output_file)
    sheet = workbook.active
    img = Image(roc_curve_image)
    sheet.add_image(img, 'P5')  # Adjust the position as needed

    # Save the Excel file with the image
    workbook.save(output_file)

# Example usage:
process_excel_with_roc('data/output_trip_probabilities.xlsx', vehicle_col='Belongs to Vehicle 235268', belongs_value='Belongs')
