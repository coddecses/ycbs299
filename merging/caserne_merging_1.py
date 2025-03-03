import pandas as pd
import geopandas as gpd
import logging
from shapely import wkt

# === Configure Logging === #
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# === Load Datasets === #
logging.info("📂 Loading datasets...")

data_path = "/Users/genevievenantel/Documents/ycbs/ycbs299/data/gen/ycbsdata"

files = {
    "casernes": f"{data_path}/geojson/territoires-administratifs-casernes.geojson",
    "housing": f"{data_path}/geojson/uniteevaluationfonciere.geojson",
    "crimes": f"{data_path}/crimes.csv",
    "fire_hydrants": f"{data_path}/firehydrants.csv"
}

# Load the caserne administrative boundaries
casernes_gdf = gpd.read_file(files["casernes"]).to_crs("EPSG:4326")
casernes_gdf.rename(columns={"NO_CAS_ADM": "caserne_id"}, inplace=True)

logging.info(f"🗺️ Casernes Loaded: {casernes_gdf.shape[0]} regions")

# === Load Housing Data === #
logging.info("🏠 Loading housing data...")

housing_gdf = gpd.read_file(files["housing"]).to_crs("EPSG:4326")
logging.info(f"🏠 Housing Data Loaded: {housing_gdf.shape[0]} buildings")

# === Assign Housing to Casernes === #
logging.info("🏢 Mapping housing units to casernes...")

housing_with_casernes = gpd.sjoin(housing_gdf, casernes_gdf, how="left", predicate="within")
logging.info(f"🏢 Housing Units Assigned: {housing_with_casernes['caserne_id'].notna().sum()} mapped to casernes")

# === Aggregate Housing Data per Caserne === #
logging.info("📊 Aggregating housing data by caserne...")

# Convert relevant columns to numeric before aggregation
numeric_columns = ["ETAGE_HORS_SOL", "NOMBRE_LOGEMENT", "ANNEE_CONSTRUCTION", "SUPERFICIE_TERRAIN", "SUPERFICIE_BATIMENT"]
for col in numeric_columns:
    housing_with_casernes[col] = pd.to_numeric(housing_with_casernes[col], errors="coerce")

# === Improve Building Type Classification === #
building_categories = {
    "Residential": [
        "Logement", "Résidence pour personnes âgées", "Résidence étudiante", "Appartement", "Condo"
    ],
    "Commercial": [
        "Immeuble commercial", "Immeuble à bureaux", "Hôtel", "Magasin", "Restaurant", "Centre d'achat", "Banque"
    ],
    "Industrial": [
        "Entrepôt", "Usine", "Industrie manufacturière", "Transformation alimentaire"
    ],
    "Public_Services": [
        "École", "École élémentaire", "Hôpital", "Poste de police", "Poste de pompier", "Bibliothèque", "Église", "Centre communautaire"
    ],
    "Recreational": [
        "Parc", "Gymnase", "Stade", "Théâtre", "Centre sportif"
    ],
    "Vacant_Unused": [
        "Terrain vacant", "Espace de terrain non aménagé", "Bâtiment abandonné"
    ],
    "Infrastructure": [
        "Route", "Gare", "Pont", "Stationnement", "Autoroute", "Centrale électrique", "Transport public"
    ]
}

# Assign each property to a category using **partial matches**
housing_with_casernes["building_category"] = "Other"

for category, keywords in building_categories.items():
    housing_with_casernes.loc[
        housing_with_casernes["LIBELLE_UTILISATION"].str.contains("|".join(keywords), case=False, na=False), 
        "building_category"
    ] = category

# Aggregate by caserne
housing_aggregated = housing_with_casernes.groupby("caserne_id").agg(
    total_buildings=("ID_UEV", "count"),
    avg_floors=("ETAGE_HORS_SOL", "mean"),
    avg_units_per_building=("NOMBRE_LOGEMENT", "mean"),
    median_construction_year=("ANNEE_CONSTRUCTION", "median"),
    total_building_area=("SUPERFICIE_BATIMENT", "sum"),
    total_land_area=("SUPERFICIE_TERRAIN", "sum"),
).reset_index()

# Count building categories per caserne
building_type_distribution = housing_with_casernes.groupby(["caserne_id", "building_category"]).size().unstack(fill_value=0).reset_index()

# Merge with aggregated housing data
housing_aggregated = housing_aggregated.merge(building_type_distribution, on="caserne_id", how="left")
logging.info(f"📊 Housing Data Aggregated for {housing_aggregated.shape[0]} casernes")

# === Process Crimes with Specific Categories & Time Series === #
logging.info("🚔 Processing crimes and mapping to casernes with time breakdown...")

# Load crime dataset
crimes = pd.read_csv(files["crimes"])
crimes = crimes.dropna(subset=["LONGITUDE", "LATITUDE", "CATEGORIE", "DATE"])
crimes_gdf = gpd.GeoDataFrame(crimes, geometry=gpd.points_from_xy(crimes["LONGITUDE"], crimes["LATITUDE"]), crs="EPSG:4326")

# Convert DATE to datetime format & extract year, month, and day
crimes_gdf["DATE"] = pd.to_datetime(crimes_gdf["DATE"])
crimes_gdf["year"] = crimes_gdf["DATE"].dt.year
crimes_gdf["month"] = crimes_gdf["DATE"].dt.month
crimes_gdf["day"] = crimes_gdf["DATE"].dt.day

# Spatial join: assign crimes to their respective casernes
crimes_with_casernes = gpd.sjoin(crimes_gdf, casernes_gdf, how="left", predicate="within")

# === Aggregate General Crime Count Per Caserne & Date === #
crime_counts = crimes_with_casernes.groupby("caserne_id").size().reset_index(name="crime_count")

# === Aggregate Specific Crime Types === #
specific_crimes = ["Méfait", "Introduction", "Vols qualifiés"]

# Dictionary to store DataFrames
crime_type_counts = {}

for crime in specific_crimes:
    crime_key = crime.lower().replace(" ", "_") + "_count"  # Standardize column name
    crime_df = crimes_with_casernes[crimes_with_casernes["CATEGORIE"] == crime] \
        .groupby("caserne_id") \
        .size().reset_index(name=crime_key)
    crime_counts = crime_counts.merge(crime_df, on="caserne_id", how="left")

# Fill NaNs with 0 (if a specific crime did not occur on that day, it should be zero)
crime_counts.fillna(0, inplace=True)

logging.info(f"🚔 Crime Data Aggregated: {crime_counts.shape[0]} records with time-series breakdown")

# === Process Fire Hydrants === #
logging.info("🚒 Processing fire hydrants and mapping to casernes...")

fire_hydrants = pd.read_csv(files["fire_hydrants"])
fire_hydrants = fire_hydrants.dropna(subset=["LONGITUDE", "LATITUDE"])
fire_hydrants_gdf = gpd.GeoDataFrame(
    fire_hydrants, geometry=gpd.points_from_xy(fire_hydrants["LONGITUDE"], fire_hydrants["LATITUDE"]), crs="EPSG:4326"
)

hydrants_with_casernes = gpd.sjoin(fire_hydrants_gdf, casernes_gdf, how="left", predicate="within")
hydrant_counts = hydrants_with_casernes.groupby("caserne_id").size().reset_index(name="hydrant_count")

# === Merge All Data === #
logging.info("📑 Merging all datasets into a final dataset...")

caserne_data = casernes_gdf[["caserne_id", "geometry"]]
caserne_data = caserne_data.merge(housing_aggregated, on="caserne_id", how="left")
caserne_data = caserne_data.merge(crime_counts, on="caserne_id", how="left")
caserne_data = caserne_data.merge(hydrant_counts, on="caserne_id", how="left")

caserne_data.fillna(0, inplace=True)

# === Save Final Dataset as BOTH GeoJSON and CSV === #
logging.info("💾 Saving final datasets...")

# Save as GeoJSON (keeps spatial data for mapping)
geojson_path = "caserne_data_with_features.geojson"
caserne_data.to_file(geojson_path, driver="GeoJSON")
logging.info(f"🌍 GeoJSON file saved as '{geojson_path}'")

# Save as CSV (including geometry as WKT)
csv_path = "caserne_data_with_features.csv"
# Convert geometry to WKT format before saving
caserne_data['geometry'] = caserne_data['geometry'].apply(lambda x: x.wkt if x is not None else None)
caserne_data.to_csv(csv_path, index=False)
logging.info(f"📊 CSV file saved as '{csv_path}'")

logging.info("✅ Processing completed! Both GeoJSON and CSV versions are available.")
