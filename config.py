# config.py
# GCP Bucket Name
BUCKET_NAME = "ycbs299"

# Data file names from GCP
FIRE_INCIDENTS_FILES = [
    "donneesouvertes-interventions-sim_2015_2022.csv",
    "donneesouvertes-interventions-sim-2005-2014.csv",
    "donneesouvertes-interventions-sim.csv"
]
CRIMES_FILE = "actes-criminels.csv"
PROPERTY_ASSESSMENT_FILE = "uniteevaluationfonciere.csv"
FIRE_STATIONS_FILE = "casernes.csv"

# External datasets (Download them and save in the project folder)
CENSUS_FILE = "census_montreal.csv"  # Download from StatsCan
WEATHER_FILES = [
    "en_climate_daily_QC_702S006_2002_P1D.csv",
    "en_climate_daily_QC_702S006_2003_P1D.csv",
    "en_climate_daily_QC_702S006_2004_P1D.csv",
    "en_climate_daily_QC_702S006_2005_P1D.csv",
    "en_climate_daily_QC_702S006_2006_P1D.csv",
    "en_climate_daily_QC_702S006_2007_P1D.csv",
    "en_climate_daily_QC_702S006_2008_P1D.csv",
    "en_climate_daily_QC_702S006_2009_P1D.csv",
    "en_climate_daily_QC_702S006_2010_P1D.csv",
    "en_climate_daily_QC_702S006_2011_P1D.csv",
    "en_climate_daily_QC_702S006_2012_P1D.csv",
    "en_climate_daily_QC_702S006_2013_P1D.csv",
    "en_climate_daily_QC_702S006_2014_P1D.csv",
    "en_climate_daily_QC_702S006_2015_P1D.csv",
    "en_climate_daily_QC_702S006_2016_P1D.csv",
    "en_climate_daily_QC_702S006_2017_P1D.csv",
    "en_climate_daily_QC_702S006_2018_P1D.csv",
    "en_climate_daily_QC_702S006_2019_P1D.csv",
    "en_climate_daily_QC_702S006_2020_P1D.csv",
    "en_climate_daily_QC_702S006_2021_P1D.csv",
    "en_climate_daily_QC_702S006_2022_P1D.csv",
    "en_climate_daily_QC_702S006_2023_P1D.csv",
    "en_climate_daily_QC_702S006_2024_P1D.csv",
    "en_climate_daily_QC_702S006_2025_P1D.csv"
]

# Columns to use for feature engineering
TIME_COL = "CREATION_DATE_TIME"
GRID_ID_COL = "NOM_ARROND"

# Paths for saving data locally
LOCAL_DATA_PATH = "data/"  # Default path for storing processed data locally
