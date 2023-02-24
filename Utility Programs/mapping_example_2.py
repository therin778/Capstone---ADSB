import folium

def plot_coordinates_on_map(coords, filename):
    # Create a map centered on the first coordinate in the set
    map_center = coords[0]
    m = folium.Map(location=map_center, zoom_start=10)

    # Add markers for each coordinate to the map
    for coord in coords:
        folium.Marker(location=coord).add_to(m)

    # Draw a line connecting the coordinates
    folium.PolyLine(coords, color='red').add_to(m)

    # Save the map as an HTML file
    m.save(filename)

coords = [
    (40.7128, -74.0060),  # New York City
    (40.7128, -74.0055),  # New York City (slightly to the east)
    (40.7128, -74.0050),  # New York City (slightly to the east)
    (40.7128, -74.0045)   # New York City (slightly to the east)
]

filename = "my_map.html"

plot_coordinates_on_map(coords, filename)