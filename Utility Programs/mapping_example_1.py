import folium


def plot_coordinates_on_map(coordinates, filename):
    # Create a map centered on the first coordinate in the set
    map_center = coordinates[0]
    m = folium.Map(location=map_center, zoom_start=10)

    # Add markers for each coordinate to the map
    for coord in coordinates:
        folium.Marker(location=coord).add_to(m)

    # Save the map as an HTML file
    m.save(filename)

coordinates = [
    (40.7128, -74.0060),  # New York City
    (51.5074, -0.1278),   # London
    (48.8566, 2.3522),    # Paris
    (35.6895, 139.6917)   # Tokyo
]

filename = "my_map.html"

plot_coordinates_on_map(coordinates, filename)