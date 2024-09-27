import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score
import os
from vehicle_profiles import VehicleProfiles


def process_excel_with_roc(df: pd.DataFrame, vehicle_col: str, belongs_value="Belongs", vehicle_id: str = "unknown",
                           output_dir: str = 'media', vehicle_profiles: VehicleProfiles = None) -> str:
    """Process the DataFrame, calculate ROC, and save the ROC curve image. Returns the image path."""

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Check if both classes are present
    unique_classes = df[vehicle_col].unique()
    if len(unique_classes) < 2:
        raise ValueError("Only one class present in y_true. ROC AUC score is not defined in that case.")

    # Add new headers if not present
    new_headers = ['Threshold', 'TP', 'TN', 'FP', 'FN', 'Recall', 'Precision', 'Specificity']
    for header in new_headers:
        df[header] = np.nan

    # Convert labels to binary
    true_labels = np.where(df[vehicle_col] == belongs_value, 1, 0)
    probabilities = df['Probability'].values

    # Check if probabilities are valid numbers
    if np.any(np.isnan(probabilities)) or np.any(np.isinf(probabilities)):
        raise ValueError("Probability column contains invalid values.")

    # Compute ROC curve and AUC
    fpr, tpr, thresholds = roc_curve(true_labels, probabilities)
    auc_value = roc_auc_score(true_labels, probabilities)

    # Find the optimal threshold using Youden's J statistic
    j_scores = tpr - fpr
    optimal_idx = np.argmax(j_scores)
    optimal_threshold = thresholds[optimal_idx]

    print(f"Optimal threshold for vehicle {vehicle_id}: {optimal_threshold}")
    if vehicle_profiles is not None:
        vehicle_profiles.set_threshold(vehicle_id, optimal_threshold)
        vehicle_profiles.display_profile(vehicle_id)  # Print the updated threshold for checking

    #  TP, TN, FP, FN
    tp = np.sum((true_labels == 1) & (probabilities >= optimal_threshold))
    tn = np.sum((true_labels == 0) & (probabilities < optimal_threshold))
    fp = np.sum((true_labels == 0) & (probabilities >= optimal_threshold))
    fn = np.sum((true_labels == 1) & (probabilities < optimal_threshold))

    #  Recall, Precision ו-Specificity
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
    plt.plot(fpr, tpr, label=f'ROC curve (AUC = {auc_value:.2f})')
    plt.plot([0, 1], [0, 1], linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve for Vehicle {vehicle_id}')
    plt.legend(loc="lower right")

    # Save the ROC curve as an image with a unique name
    roc_curve_image = os.path.join(output_dir, f'roc_curve_vehicle_{vehicle_id}.png')
    plt.savefig(roc_curve_image)
    plt.close()

    return roc_curve_image
