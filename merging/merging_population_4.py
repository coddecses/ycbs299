import pandas as pd
import numpy as np
from fuzzywuzzy import process, fuzz
import os

# Set Google Application Credentials (if loading from GCP)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/content/peppy-web-437616-r6-ec3f12e7c15e.json'

# Load the master dataset from GCP bucket
from google.cloud import storage

bucket_name = 'ycbs299'
blob_name = 'fire_incidents_with_caserne_features.csv'
local_file_path = '/content/fire_incidents_with_caserne_features.csv'

storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)
blob = bucket.blob(blob_name)
blob.download_to_filename(local_file_path)

print(f"File downloaded to {local_file_path}")

# Load the master dataset
master_df = pd.read_csv(local_file_path)

# Load the population and area data (replace with your actual file paths)
population_df = pd.read_csv('/content/municipalities-boroughs-population.csv')  # Population data (2005–2024)
area_df = pd.read_csv('/content/municipalities-boroughs-area.csv')  # Area data (AREA_SQUARE_KM)

# Clean and standardize borough names for fuzzy matching
def clean_name(name):
    if pd.isna(name):
        return ""
    # Remove "Le", "La", "L'", convert to lowercase, remove extra spaces/hyphens
    name = str(name).lower().replace("le ", "").replace("la ", "").replace("l'", "").replace("-", " ").strip()
    return name

# Apply cleaning to borough names in all datasets
master_df['NOM_ARROND_clean'] = master_df['NOM_ARROND'].apply(clean_name)
population_df['MUNICIPALITY/BOROUGH_clean'] = population_df['MUNICIPALITY/BOROUGH'].apply(clean_name)
area_df['MUNICIPALITY/BOROUGH_clean'] = area_df['MUNICIPALITY/BOROUGH'].apply(clean_name)

# Get unique borough names from all datasets
master_boroughs = master_df['NOM_ARROND_clean'].unique()
population_boroughs = population_df['MUNICIPALITY/BOROUGH_clean'].unique()  # Fixed syntax error
area_boroughs = area_df['MUNICIPALITY/BOROUGH_clean'].unique()

# Split combined borough names (e.g., "Beaconsfield / Baie d'Urfé" → ["Beaconsfield", "Baie d'Urfé"])
def split_combined_name(name):
    if '/' in name:
        return [clean_name(part.strip()) for part in name.split('/')]
    return [name]

# Fuzzy match borough names, handling combined names
def fuzzy_match_combined(name, choices, threshold=90):
    # Split the name if it contains a slash
    name_parts = split_combined_name(name)
    
    # Try matching each part individually
    for part in name_parts:
        match = process.extractOne(part, choices, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= threshold:
            return match[0]
    
    # If no match found for individual parts, try matching the full name
    match = process.extractOne(name, choices, scorer=fuzz.token_sort_ratio)
    if match and match[1] >= threshold:
        return match[0]
    
    return None

# Create mapping dictionaries for population and area datasets
pop_mapping = {borough: fuzzy_match_combined(borough, population_boroughs) for borough in master_boroughs}
area_mapping = {borough: fuzzy_match_combined(borough, area_boroughs) for borough in master_boroughs}

# Manual overrides for known mismatches
manual_mapping = {
    "beaconsfield / baie d'urfé": "beaconsfield",  # Map combined name to one part
    "beaconsfield": "beaconsfield",
    "baie d'urfé": "baie d'urfé",
    "côte st luc / hampstead / mtl ouest": "côte saint luc",  # Example mapping
    "pierrefonds / senneville": "pierrefonds",
    "dollard des ormeaux / roxboro": "dollard des ormeaux",
    "dorval / ile dorval": "dorval",
    "ile bizard / ste geneviève / ste a de b": "l'ile bizard",
    "indéterminé": None  # Special case: no match
}
pop_mapping.update(manual_mapping)
area_mapping.update(manual_mapping)

# Apply the mappings to the master dataset
master_df['pop_matched_borough'] = master_df['NOM_ARROND_clean'].map(pop_mapping)
master_df['area_matched_borough'] = master_df['NOM_ARROND_clean'].map(area_mapping)

# Check for unmatched boroughs
unmatched_pop = master_df[master_df['pop_matched_borough'].isna()]['NOM_ARROND'].unique()
unmatched_area = master_df[master_df['area_matched_borough'].isna()]['NOM_ARROND'].unique()
print("Unmatched boroughs for population:", unmatched_pop)
print("Unmatched boroughs for area:", unmatched_area)

# Merge population data (year-specific)
# Melt the population DataFrame to have year as a column
pop_melted = population_df.melt(id_vars=['MUNICIPALITY/BOROUGH_clean'], 
                                value_vars=[str(year) for year in range(2005, 2025)],
                                var_name='year', value_name='population')
pop_melted['year'] = pop_melted['year'].astype(int)

# Extract year from CREATION_DATE in master_df
master_df['year'] = pd.to_datetime(master_df['CREATION_DATE']).dt.year

# Merge population based on year and matched borough
master_df = master_df.merge(pop_melted, how='left', 
                            left_on=['pop_matched_borough', 'year'], 
                            right_on=['MUNICIPALITY/BOROUGH_clean', 'year'])

# For future years (2025–2026), use 2024 population as a proxy
master_df.loc[master_df['year'] >= 2025, 'population'] = master_df[master_df['year'] == 2024][['pop_matched_borough']].merge(
    pop_melted[pop_melted['year'] == 2024][['MUNICIPALITY/BOROUGH_clean', 'population']],
    left_on='pop_matched_borough', right_on='MUNICIPALITY/BOROUGH_clean', how='left')['population']

# Merge area data (static)
master_df = master_df.merge(area_df[['MUNICIPALITY/BOROUGH_clean', 'AREA_SQUARE_KM']], how='left',
                            left_on='area_matched_borough', right_on='MUNICIPALITY/BOROUGH_clean')
master_df = master_df.rename(columns={'AREA_SQUARE_KM': 'area_square_km'})

# Clean up temporary columns
master_df = master_df.drop(columns=['NOM_ARROND_clean', 'pop_matched_borough', 'area_matched_borough', 
                                    'MUNICIPALITY/BOROUGH_clean_x', 'MUNICIPALITY/BOROUGH_clean_y'])

# Impute missing values for new columns and special cases like "Indéterminé"
master_df['population'] = master_df['population'].fillna(master_df['population'].median())
master_df['area_square_km'] = master_df['area_square_km'].fillna(master_df['area_square_km'].median())

# Save the updated master dataset
updated_file_path = '/content/fire_incidents_with_caserne_features_updated.csv'
master_df.to_csv(updated_file_path, index=False)
print(f"Updated master dataset saved to {updated_file_path}")