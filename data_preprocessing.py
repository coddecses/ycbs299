import pandas as pd

# Load datasets
fire_incidents = pd.read_csv("data/fire_incidents.csv")
crimes = pd.read_csv("data/crimes.csv")
property_assessment = pd.read_csv("data/property_assessment.csv")
fire_stations = pd.read_csv("data/fire_stations.csv")
weather_data = pd.read_csv("data/weather_data.csv")

# Check the column names of the weather data (for debugging)
print("Weather Data Columns:", weather_data.columns)

# Correctly handle the date/time column
weather_data["Date/Time"] = pd.to_datetime(weather_data["Date/Time"], errors="coerce")
weather_data["Year"] = weather_data["Date/Time"].dt.year
weather_data["Month"] = weather_data["Date/Time"].dt.month

# Standardize other datasets' date formats
fire_incidents["CREATION_DATE_TIME"] = pd.to_datetime(fire_incidents["CREATION_DATE_TIME"], errors="coerce")
fire_incidents["Year"] = fire_incidents["CREATION_DATE_TIME"].dt.year
fire_incidents["Month"] = fire_incidents["CREATION_DATE_TIME"].dt.month

crimes["DATE"] = pd.to_datetime(crimes["DATE"], errors="coerce")
crimes["Year"] = crimes["DATE"].dt.year
crimes["Month"] = crimes["DATE"].dt.month

# Save processed files
fire_incidents.to_csv("data/processed_fire_incidents.csv", index=False)
crimes.to_csv("data/processed_crimes.csv", index=False)
weather_data.to_csv("data/processed_weather_data.csv", index=False)

print("Data preprocessing complete.")
