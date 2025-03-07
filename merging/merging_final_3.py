import pandas as pd

# File paths (update these to match your local file locations)
fire_incidents_file = "/Users/genevievenantel/Documents/ycbs/ycbs299/data/fire_incidents_with_weather.csv"  # Your fire incidents with weather data
caserne_file = "/Users/genevievenantel/Documents/ycbs/ycbs299/data/caserne_data_with_features.csv"         # Your caserne data with features
output_file = "fire_incidents_with_caserne_features.csv"  # Output file name

# Read the CSV files
print("Reading fire incidents with weather data...")
fire_df = pd.read_csv(fire_incidents_file)

print("Reading caserne data with features...")
caserne_df = pd.read_csv(caserne_file)

# Ensure the caserne columns are of the same type (integer) for merging
fire_df['CASERNE'] = fire_df['CASERNE'].astype(int)
caserne_df['caserne_id'] = caserne_df['caserne_id'].astype(int)

# Merge the datasets on 'CASERNE' (fire incidents) and 'caserne_id' (caserne data)
print("Merging datasets...")
merged_df = fire_df.merge(
    caserne_df,
    how='left',  # Left join to keep all fire incidents, even if caserne data is missing
    left_on='CASERNE',
    right_on='caserne_id'
)

# Drop the redundant 'caserne_id' column since it's the same as 'CASERNE'
merged_df = merged_df.drop(columns=['caserne_id'])

# Compute risk_level based on incident_count (assuming it's in fire_df)
def assign_risk_level(incident_count):
    if incident_count <= merged_df['incident_count'].quantile(0.5):  # Bottom 50%
        return 'Low'
    elif incident_count <= merged_df['incident_count'].quantile(0.8):  # 50% to 80%
        return 'Medium'
    else:  # Top 20%
        return 'High'

print("Computing risk levels...")
merged_df['risk_level'] = merged_df['incident_count'].apply(assign_risk_level)

# Save the merged dataset to a new CSV file
print(f"Saving merged data to {output_file}...")
merged_df.to_csv(output_file, index=False)

print("Done! Check the output file:", output_file)

# Optional: Display the first few rows to verify
print("\nFirst few rows of the merged dataset:")
print(merged_df.head())
