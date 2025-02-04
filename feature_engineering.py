import pandas as pd
from config import GRID_ID_COL

# Load processed data
fire_incidents = pd.read_csv("data/processed_fire_incidents.csv")
crimes = pd.read_csv("data/crimes.csv")
weather_data = pd.read_csv("data/processed_weather_data.csv")

# Extract Year and Month from the 'CREATION_DATE_TIME' column for fire incidents
fire_incidents["CREATION_DATE_TIME"] = pd.to_datetime(fire_incidents["CREATION_DATE_TIME"], errors="coerce")
fire_incidents["Year"] = fire_incidents["CREATION_DATE_TIME"].dt.year
fire_incidents["Month"] = fire_incidents["CREATION_DATE_TIME"].dt.month

# Extract Year and Month from the 'DATE' column for crimes
crimes["DATE"] = pd.to_datetime(crimes["DATE"], errors="coerce")
crimes["Year"] = crimes["DATE"].dt.year
crimes["Month"] = crimes["DATE"].dt.month

# Aggregate fire incidents by 'NOM_ARROND', Year & Month
fire_counts = fire_incidents.groupby([GRID_ID_COL, "Year", "Month"]).size().reset_index(name="Fire_Incident_Count")

# Aggregate crimes by Year & Month (No grid ID for crimes)
crime_counts = crimes.groupby(["Year", "Month"]).size().reset_index(name="Crime_Count")

# Aggregate weather data by Year & Month (for temperature and precipitation)
weather_aggregates = weather_data.groupby(["Year", "Month"]).agg({
    "Max Temp (°C)": "mean",
    "Min Temp (°C)": "mean",
    "Mean Temp (°C)": "mean",
    "Total Precip (mm)": "sum"
}).reset_index()

# Merge all datasets
df = fire_counts.merge(crime_counts, on=["Year", "Month"], how="left").fillna(0)
df = df.merge(weather_aggregates, on=["Year", "Month"], how="left")

# Save feature set
df.to_csv("data/features.csv", index=False)

print("Feature engineering complete.")
