import os
import webbrowser
import folium
from engine import load_graph, calculate_dispatch_options

def run_app():
    leeds_centre = (53.8008, -1.5491)
    emergency_coords = (53.7961, -1.5362)
    hospitals = {
        "Leeds General Infirmary": (53.8016, -1.5516),
        "St James's University Hospital": (53.8066, -1.5204),
        "Beckett Street Station": (53.8115, -1.5265)
    }

    print("Step 1: Downloading & Enriching Map via Engine...")
    graph = load_graph(leeds_centre)

    print("\nStep 2: Calculating Dispatch Metrics...")
    dispatch_data = calculate_dispatch_options(graph, hospitals, emergency_coords)

    # Initialize Folium Map
    visual_map = folium.Map(location=leeds_centre, zoom_start=14)
    folium.Marker(
        location=emergency_coords, 
        popup="ACTIVE EMERGENCY", 
        icon=folium.Icon(color='red', icon='ambulance', prefix='fa')
    ).add_to(visual_map)

    best_time_sec = float('inf')
    best_time_coords = []
    best_time_hospital = ""

    best_dist_m = float('inf')
    best_dist_coords = []
    best_dist_hospital = ""

    for name, data in dispatch_data.items():
        if data is None:
            print(f"Could not find route from {name}")
            continue

        print(f"\n{name}:")
        print(f"    Time-Optimized:   {data['time_dist_m']:.0f}m | Est. Arrival: {data['time_sec']/60.0:.2f} mins")
        print(f"    Distance-Optimized: {data['dist_m']:.0f}m | Est. Arrival: {data['dist_sec']/60.0:.2f} mins")

        if data['time_sec'] < best_time_sec:
            best_time_sec = data['time_sec']
            best_time_coords = data['time_coords']
            best_time_hospital = name

        if data['dist_m'] < best_dist_m:
            best_dist_m = data['dist_m']
            best_dist_coords = data['dist_coords']
            best_dist_hospital = name

        folium.Marker(location=data['coords'], popup=name, icon=folium.Icon(color='blue', icon='h-square', prefix='fa')).add_to(visual_map)

    # Plot winning paths (Dual-Stroke Overlay)
    if best_dist_coords:
        folium.PolyLine(best_dist_coords, color='blue', weight=10, opacity=0.6, tooltip=f"Shortest Distance: {best_dist_hospital}").add_to(visual_map)
    if best_time_coords:
        folium.PolyLine(best_time_coords, color='lime', weight=4, opacity=1.0, tooltip=f"Fastest Time: {best_time_hospital}").add_to(visual_map)

    # Legend HTML
    legend_html = '''
     <div style="position: fixed; bottom: 30px; left: 30px; width: 260px; height: 95px; 
                 border:2px solid gray; z-index:9999; font-size:13px; background-color:white;
                 padding: 10px; border-radius: 5px;">
     <b>Dispatch Route Legend</b><br>
     <i style="background: lime; width: 25px; height: 4px; display: inline-block; margin-right: 8px;"></i><b>Fastest Route (Time)</b><br>
     <i style="background: blue; width: 25px; height: 4px; display: inline-block; margin-right: 8px;"></i><b>Shortest Route (Distance)</b>
     </div>
     '''
    visual_map.get_root().html.add_child(folium.Element(legend_html))

    output_filename = "ambulance_route.html"
    visual_map.save(output_filename)
    
    file_url = f"file://{os.path.abspath(output_filename)}"
    print(f"\nSuccess! Map saved to '{output_filename}'. Opening in browser...")
    webbrowser.open(file_url)

if __name__ == "__main__":
    run_app()