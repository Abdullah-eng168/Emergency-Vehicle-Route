import warnings
# Silence that LibreSSL warning so your terminal stays completely clean
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

import osmnx as ox
import networkx as nx
import folium

ox.settings.use_cache = True
print("Step 1: Downloading the street network for Leeds City Centre...")
# This downloads real data from OpenStreetMap (only drivable roads)
leeds_centre = (53.8008, -1.5491)
graph = ox.graph_from_point(leeds_centre, dist=3000, network_type="drive")
print(f"Map Loaded! Found {len(graph.nodes)} intersections and {len(graph.edges)} roads.")

print("\n Step 2: Defining emergency locations...")
# Let's set up two random coordinates in Leeds (Latitude, Longitude)
# Start Point (e.g., An Ambulance Station near the University)
start_coords = (53.8067, -1.5555) 
# End Point (e.g., An emergency call location near Leeds Minster)
end_coords = (53.7961, -1.5362)

# Find the closest physical intersections (nodes) on our map to those coordinates
start_node = ox.nearest_nodes(graph, X=start_coords[1], Y=start_coords[0])
end_node = ox.nearest_nodes(graph, X=end_coords[1], Y=end_coords[0])

print("Step 3: Running Dijkstra's Algorithm to find the fastest path...")
# This is where NetworkX uses graph theory discrete math to find the optimal path
shortest_path = nx.shortest_path(graph, source=start_node, target=end_node, weight="length")
print(f"Route calculated! The route passes through {len(shortest_path)} intersections.")

print("\n Step 4: Generating interactive web map...")
# 1. Extract the exact (Latitude, Longitude) coordinates for every intersection in the path
route_coords = [(graph.nodes[node]["y"], graph.nodes[node]["x"]) for node in shortest_path]

# 2. Create a clean, interactive Folium base map centered on Leeds
visual_map = folium.Map(location=leeds_centre, zoom_start=14)

# 3. Add start and end pins to clearly show the ambulance dispatch
folium.Marker(location=start_coords, popup="Ambulance Station", icon=folium.Icon(color="green")).add_to(visual_map)
folium.Marker(location=end_coords, popup="Emergency Call", icon=folium.Icon(color="red")).add_to(visual_map)

# 4. Use standard Folium to paint the red emergency line across the coordinates
folium.PolyLine(route_coords, color="red", weight=5, opacity=0.8).add_to(visual_map)

# 5. Save it as an HTML webpage inside your project folder
output_filename = "ambulance_route.html"
visual_map.save(output_filename)
print(f" Success! The interactive map has been saved as '{output_filename}' in your sidebar.")