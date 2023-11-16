import population
import pandas as pd
import folium
from folium.plugins import MarkerCluster

# Create a DataFrame similar to the one we used before
data = population.data

population_df = pd.DataFrame(data)

# Initialize the map centered around India
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

# Create a marker cluster
marker_cluster = MarkerCluster().add_to(m)

# Add city data as markers to the map
for idx, row in population_df.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=row['Population'] / 10000000,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(marker_cluster)

# Show the map by saving it to an HTML file
m.save('india_population_map.html')
