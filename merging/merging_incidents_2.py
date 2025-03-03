import pandas as pd

# File paths (update these to match your local file locations)
weather_file = "/Users/genevievenantel/Documents/ycbs/ycbs299/data/gen/ycbsdata/weather.csv"  # Your weather data file
incidents_file = "/Users/genevievenantel/Documents/ycbs/ycbs299/data/gen/ycbsdata/fireincidents.csv"  # Your fire incidents file
output_file = "fire_incidents_with_weather.csv"  # Output file name

# Read the CSV files
print("Reading weather data...")
weather_df = pd.read_csv(weather_file)

print("Reading fire incidents data...")
incidents_df = pd.read_csv(incidents_file)

# Convert CREATION_DATE to datetime and extract year and month
print("Processing dates in fire incidents...")
incidents_df['CREATION_DATE'] = pd.to_datetime(incidents_df['CREATION_DATE'])
incidents_df['year'] = incidents_df['CREATION_DATE'].dt.year
incidents_df['month'] = incidents_df['CREATION_DATE'].dt.month

# Ensure weather_df has 'year' and 'month' as integers for merging
weather_df['year'] = weather_df['year'].astype(int)
weather_df['month'] = weather_df['month'].astype(int)

# Merge the datasets on 'year' and 'month'
print("Merging datasets...")
merged_df = incidents_df.merge(
    weather_df,
    how='left',
    on=['year', 'month']
)

# Drop the temporary 'year' and 'month' columns from the final output if you don't need them
merged_df = merged_df.drop(columns=['year', 'month'])

# Save the merged dataset to a new CSV file
print(f"Saving merged data to {output_file}...")
merged_df.to_csv(output_file, index=False)

print("Done! Check the output file:", output_file)

# Optional: Display the first few rows to verify
print("\nFirst few rows of the merged dataset:")
print(merged_df.head())