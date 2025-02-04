import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# Load features
df = pd.read_csv("data/features.csv")

# Define target variable (e.g., predicting Fire Risk Level)
df["Fire_Risk_Level"] = pd.cut(df["Fire_Incident_Count"], bins=[0, 10, 50, float('inf')], labels=["Low", "Medium", "High"])

# Select features
features = ["Crime_Count", "Max Temp (°C)", "Min Temp (°C)", "Mean Temp (°C)", "Total Precip (mm)"]
target = "Fire_Risk_Level"

# Handle missing or infinite values
df[features] = df[features].replace([float('inf'), -float('inf')], pd.NA)  # Replace infinity with NaN
df = df.fillna(df.mean())  # Fill NaN with mean of the column

# Split data into train and test sets
X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Classifier with class weights
rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
rf.fit(X_train, y_train)

# Make predictions
rf_pred = rf.predict(X_test)

# Evaluate Random Forest model
print("Random Forest Classification Report:\n", classification_report(y_test, rf_pred))

# Ensure 'models/' directory exists, if not, create it
os.makedirs('models', exist_ok=True)

# Save Random Forest model
joblib.dump(rf, 'models/random_forest_model.pkl')
