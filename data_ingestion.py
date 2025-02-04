import os
import pandas as pd
import gcsfs
from config import BUCKET_NAME, FIRE_INCIDENTS_FILES, CRIMES_FILE, PROPERTY_ASSESSMENT_FILE, FIRE_STATIONS_FILE, WEATHER_FILES

# Google Cloud authentication
fs = gcsfs.GCSFileSystem()

def load_data_from_gcs(file_name):
    """Load a CSV file from Google Cloud Storage into a Pandas DataFrame."""
    file_path = f"gs://{BUCKET_NAME}/{file_name}"
    return pd.read_csv(file_path, encoding="utf-8")

# Load datasets from GCP
fire_incidents_list = []
for file in FIRE_INCIDENTS_FILES:
    fire_incidents_data = load_data_from_gcs(file)
    fire_incidents_list.append(fire_incidents_data)

# Concatenate fire incident data into a single DataFrame
fire_incidents = pd.concat(fire_incidents_list, ignore_index=True)

# Load other datasets
crimes = load_data_from_gcs(CRIMES_FILE)
property_assessment = load_data_from_gcs(PROPERTY_ASSESSMENT_FILE)
fire_stations = load_data_from_gcs(FIRE_STATIONS_FILE)

# Load weather data from GCP (files listed in WEATHER_FILES in config.py)
weather_data_list = []
for file in WEATHER_FILES:
    weather_data = load_data_from_gcs(file)
    weather_data_list.append(weather_data)

# Combine all weather data into a single DataFrame
weather_data = pd.concat(weather_data_list, ignore_index=True)

# Create 'data' directory if it doesn't exist
if not os.path.exists('data'):
    os.makedirs('data')

# Save all data locally for further processing
fire_incidents.to_csv("data/fire_incidents.csv", index=False)
crimes.to_csv("data/crimes.csv", index=False)
property_assessment.to_csv("data/property_assessment.csv", index=False)
fire_stations.to_csv("data/fire_stations.csv", index=False)
weather_data.to_csv("data/weather_data.csv", index=False)

print("Data ingestion complete.")
