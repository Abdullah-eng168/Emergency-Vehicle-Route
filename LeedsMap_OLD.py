import osmnx as ox
import networkx as nx
import folium
import webbrowser
import os

ox.settings.use_cache = True
print("Step 1: Downloading the street network for Leeds City Centre...")
# This downloads real data from OpenStreetMap (only drivable roads)
leeds_centre = (53.8008, -1.5491)
graph = ox.graph_from_point(leeds_centre, dist=3000, network_type="drive")
#Added speeds in km/h and travel time on roads
graph = ox.add_edge_speeds(graph)
graph = ox.add_edge_travel_times(graph)

print(f"Map Loaded! Found {len(graph.nodes)} intersections and {len(graph.edges)} roads.")

print("Step 2: Defining emergency locations...")
# Let's set up two random coordinates in Leeds (Latitude, Longitude)
#Possible starting hospitals and coordinates
hospitals = {'Leeds General Infirmary': (53.8016, -1.5516),
             'St James\'s University Hospital': (53.8066, -1.5204),
             'St James\'s (Beckett St Entrance)': (53.8115, -1.5265)}
# Start Point (e.g., An Ambulance Station near the University)
# End Point (e.g., An emergency call location near Leeds Minster)
end_coords = (53.7961, -1.5362)
end_node = ox.nearest_nodes(graph, X=end_coords[1], Y=end_coords[0])

#Folium Map of Leeds
visual_map = folium.Map(location = leeds_centre, zoom_start =14)

#Emergency marker
folium.Marker(location=end_coords, icon=folium.Icon(color='red', icon='ambulance', prefix='ra')).add_to(visual_map)

print("Step 3: Calculating routes for all available ambulances...")

best_time_hospital = None
fastest_time_sec = float('inf')
best_time_coords = []

best_dist_hospital = None
shortest_dist_m = float('inf')
best_dist_coords = []

#Find the hospitals paths using Dijkstra's 

for name, coords in hospitals.items():
    # Nearest Node to Hospital
    hospital_node = ox.nearest_nodes(graph, X=coords[1], Y=coords[0])

    try:
        # --- 1. OPTIMISE FOR TIME (Seconds) ---
        time_route = nx.shortest_path(graph, source=hospital_node, target=end_node, weight="travel_time")
        
        # Calculate weights directly along the path
        time_sec = nx.path_weight(graph, time_route, weight="travel_time")
        time_dist_m = nx.path_weight(graph, time_route, weight="length")
        
        # --- 2. OPTIMISE FOR DISTANCE (Meters) ---
        dist_route = nx.shortest_path(graph, source=hospital_node, target=end_node, weight="length")
        
        # Calculate weights directly along the path
        dist_m = nx.path_weight(graph, dist_route, weight="length")
        dist_sec = nx.path_weight(graph, dist_route, weight="travel_time")

        print(f"\n {name}:")
        print(f"     Time-Optimized:   {time_dist_m:.0f}m | Est. Arrival: {time_sec/60.0:.2f} mins")
        print(f"    Distance-Optimized: {dist_m:.0f}m | Est. Arrival: {dist_sec/60.0:.2f} mins")

        # Track overall fastest time winner
        if time_sec < fastest_time_sec:
            fastest_time_sec = time_sec
            best_time_hospital = name
            best_time_coords = [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in time_route]

        # Track overall shortest distance winner
        if dist_m < shortest_dist_m:
            shortest_dist_m = dist_m
            best_dist_hospital = name
            best_dist_coords = [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in dist_route]

        # Add hospital marker to map
        folium.Marker(
            location=coords, 
            popup=name, 
            icon=folium.Icon(color='blue', icon='h-square', prefix='fa')
        ).add_to(visual_map)

    except nx.NetworkXNoPath:
        print(f"    Could not find a drivable route from {name}")

# --- DRAW WINNING PATHS ---

# 1. Winning DISTANCE-optimised route (Dashed Blue Line)
if best_dist_coords:
    folium.PolyLine(
        best_dist_coords, color='blue', weight=10, opacity=0.8, dash_array='8, 8',
        tooltip=f"Shortest Distance Winner: {best_dist_hospital} ({shortest_dist_m:.0f} meters)"
    ).add_to(visual_map)

# 2. Winning TIME-optimised route (Solid Green Line)
if best_time_coords:
    folium.PolyLine(
        best_time_coords, color='green', weight=4, opacity=0.9,
        tooltip=f"Fastest Time Winner: {best_time_hospital} ({fastest_time_sec/60.0:.2f} mins)"
    ).add_to(visual_map)

print("\n" + "="*50)
print(f" FASTEST DISPATCH:  {best_time_hospital} ({fastest_time_sec/60.0:.2f} minutes)")
print(f" SHORTEST DISPATCH: {best_dist_hospital} ({shortest_dist_m:.0f} meters)")
print("="*50)

legend_html = '''
 <div style="position: fixed; bottom: 30px; left: 30px; width: 260px; height: 95px; 
             border:2px solid gray; z-index:9999; font-size:13px; background-color:white;
             padding: 10px; border-radius: 5px;">
 <b>Dispatch Route Legend</b><br>
 <i style="background: green; width: 25px; height: 4px; display: inline-block; margin-right: 8px;"></i><b>Minimum Time Route (Free-Flow)</b><br>
 <i style="background: blue; width: 25px; height: 0px; border-top: 3px dashed blue; display: inline-block; margin-right: 8px;"></i><b>Shortest Route (Distance)</b>
 </div>
 '''
visual_map.get_root().html.add_child(folium.Element(legend_html))
output_filename = "ambulance_route.html"
visual_map.save(output_filename)
URLpath = os.path.abspath(output_filename)
webbrowser.open('file://' + URLpath)
print(f"Success! Open '{output_filename}' to see the winning route highlighted in green.")

