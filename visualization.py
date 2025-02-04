import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load shapefile of Montreal boroughs (you'll need a shapefile or geojson file for this)
montreal_map = gpd.read_file("data/montreal_shapefile.geojson")

# Load the predictions
predictions = pd.read_csv("data/predictions.csv")

# Merge predictions with spatial data (assuming 'NOM' is the borough column in the shapefile)
geo_data = montreal_map.merge(predictions, left_on="NOM", right_on="NOM_ARROND")

# Plot fire-risk map based on predictions
geo_data.plot(column="RF_Predicted_Risk", cmap="OrRd", legend=True)
plt.title("Predicted Fire-Risk in Montreal")
plt.savefig("figures/fire_risk_map.png")
plt.show()
