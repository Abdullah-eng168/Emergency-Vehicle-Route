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
print(f"Map Loaded! Found {len(graph.nodes)} intersections and {len(graph.edges)} roads.")

print("Step 2: Defining emergency locations...")
# Let's set up two random coordinates in Leeds (Latitude, Longitude)
#Possible starting hospitals and coordinates
hospitals = {'Leeds General Infirmary': (53.8016, -1.5516),
             'St James\'s University Hospital': (53.8066, -1.5204),
             'Beckett Street Station': (53.8115, -1.5265)}
# Start Point (e.g., An Ambulance Station near the University)
# End Point (e.g., An emergency call location near Leeds Minster)
end_coords = (53.7961, -1.5362)
end_node = ox.nearest_nodes(graph, X=end_coords[1], Y=end_coords[0])

#Folium Map of Leeds
visual_map = folium.Map(location = leeds_centre, zoom_start =14)

#Emergency marker
folium.Marker(location=end_coords, icon=folium.Icon(color='red', icon='ambulance', prefix='ra')).add_to(visual_map)

print("Step 3: Calculating routes for all available ambulances...")

best_hospital = None
shortest_distance = float('inf')
best_route_coords = []

#Find the hospitals paths using Dijkstra's 

for name, coords in hospitals.items():
    #Nearest Node to Hospital
    hospital_node = ox.nearest_nodes(graph, X=coords[1], Y=coords[0])

    #Calculate route distance
    try:
        route = nx.shortest_path(graph, source = hospital_node, target = end_node)
        #route distance
        route_length = sum(ox.routing.route_to_gdf(graph, route)["length"])
        print(f'{name}: Route is {round(route_length,2)} metres long.')
        #Exact coordinates for drawing lines
        route_coords = [(graph.nodes[node]['y'], graph.nodes[node]['x']) for node in route]
        #Check against shortest length
        if route_length < shortest_distance:
            shortest_distance = route_length
            best_hospital = name
            best_route_coords = route_coords
        folium.PolyLine(route_coords, color='gray', weight=3, opacity = 0.6, tooltip=f'Route from {name}').add_to(visual_map)
        folium.Marker(location = coords, popup = name, icon=folium.Icon(color='blue', icon='h-square', prefix='fa')).add_to(visual_map)
    except nx.NetworkXNoPath:
        print(f'Could not find a drivable route from {name}')
    
folium.PolyLine(best_route_coords, color = 'green', weight = 6, opacity = 1, tooltip='Dispatched Route').add_to(visual_map)

output_filename = "ambulance_route.html"
visual_map.save(output_filename)
URLpath = os.path.abspath(output_filename)
webbrowser.open('file://' + URLpath)
print(f"Success! Open '{output_filename}' to see the winning route highlighted in green.")

