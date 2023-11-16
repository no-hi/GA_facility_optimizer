import population
import pandas as pd
import folium
from folium.plugins import HeatMap

# Create a DataFrame similar to the one we used before
data = population.data

population_df = pd.DataFrame(data)

# Initialize the map centered around India
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

# Prepare data for HeatMap
heat_data = [[row['Latitude'], row['Longitude'], row['Population']] for idx, row in population_df.iterrows()]

# Create a HeatMap and add it to the map
HeatMap(heat_data, radius=50).add_to(m)

# Save the map to an HTML file
m.save('india_population_heatmap.html')
