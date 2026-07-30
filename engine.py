import networkx as nx
import osmnx as ox
import pandas as pd
import os 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_graph(centre_coords=(53.8008, -1.5491), distance=3500):
    ox.settings.use_cache = True
    graph = ox.graph_from_point(centre_coords, dist=distance, network_type="drive")
    graph = ox.add_edge_speeds(graph)
    graph = ox.add_edge_travel_times(graph)
    return graph

def calculate_dispatch_options(graph, hospitals, emergency_coords):

    end_node = ox.nearest_nodes(graph, X=emergency_coords[1], Y=emergency_coords[0])
    results = {} # Stores the hospitals times and distances

    for name, coords in hospitals.items():
        hospital_node = ox.nearest_nodes(graph, X=coords[1], Y=coords[0])

        try:
            # 1. Optimize for Time
            time_route = nx.shortest_path(graph, source=hospital_node, target=end_node, weight="travel_time")
            time_gdf = ox.routing.route_to_gdf(graph, time_route)
            
            # 2. Optimize for Distance
            dist_route = nx.shortest_path(graph, source=hospital_node, target=end_node, weight="length")
            dist_gdf = ox.routing.route_to_gdf(graph, dist_route)

            results[name] = {
                "coords": coords,
                "time_sec": time_gdf["travel_time"].sum(),
                "time_dist_m": time_gdf["length"].sum(),
                "time_coords": [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in time_route],
                "dist_m": dist_gdf["length"].sum(),
                "dist_sec": dist_gdf["travel_time"].sum(),
                "dist_coords": [(graph.nodes[n]['y'], graph.nodes[n]['x']) for n in dist_route]
            }
        except nx.NetworkXNoPath:
            results[name] = None

    return results
def export_summary_csv(dispatch_data, filename='hospital_dispatch_summary.csv'):
    rows = []
    for name, data in dispatch_data.items():
        if data is None:
            continue
        rows.append({
            'Hospital': name,
            "Fastest_Dist_m": round(data["time_dist_m"]),
            "Fastest_Time_min": round(data["time_sec"] / 60.0, 2),
            "Shortest_Dist_m": round(data["dist_m"]),
            "Shortest_Time_min": round(data["dist_sec"] / 60.0, 2)
        })
    df = pd.DataFrame(rows)

    filepath = os.path.join(BASE_DIR, filename)
    df.to_csv(filepath, index=False)
    return filepath

def export_winning_route_nodes_csv(winning_coords, hospital_name, filename="winning_route_nodes.csv"):
    
    rows = [
        {
            "step_index": idx + 1,
            "hospital_name": hospital_name,
            "latitude": lat,
            "longitude": lng
        }
        for idx, (lat, lng) in enumerate(winning_coords)
    ]
    
    df = pd.DataFrame(rows)
    filepath = os.path.join(BASE_DIR, filename)
    df.to_csv(filepath, index=False)
    return filepath

