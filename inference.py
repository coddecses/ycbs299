import pandas as pd
import joblib

# Load new data (e.g., features.csv)
df_new = pd.read_csv("data/features.csv")

# Handle missing or infinite values in the features
df_new[["Crime_Count", "Max Temp (°C)", "Min Temp (°C)", "Mean Temp (°C)", "Total Precip (mm)"]] = df_new[["Crime_Count", "Max Temp (°C)", "Min Temp (°C)", "Mean Temp (°C)", "Total Precip (mm)"]].replace([float('inf'), -float('inf')], pd.NA)  # Replace infinity with NaN
df_new = df_new.fillna(df_new.mean())  # Fill NaN with mean of the column

# Load the trained Random Forest model
rf_model = joblib.load('models/random_forest_model.pkl')

# Make predictions for the new data
df_new["RF_Predicted_Risk"] = rf_model.predict(df_new[["Crime_Count", "Max Temp (°C)", "Min Temp (°C)", "Mean Temp (°C)", "Total Precip (mm)"]])

# Save predictions to a new file
df_new.to_csv("data/predictions.csv", index=False)

print("Predictions saved.")
