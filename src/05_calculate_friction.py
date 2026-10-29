import os
import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd

def main():
    print("Starting Optimized A* Pathfinding...")
    
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    graph_path = os.path.join(base_dir, 'data', 'processed', 'york_region_network.graphml')
    demand_path = os.path.join(base_dir, 'data', 'processed', 'demand_nodes.geojson')
    fb_path = os.path.join(base_dir, 'data', 'raw', 'food_banks.csv')
    output_path = os.path.join(base_dir, 'data', 'processed', 'demand_with_friction.geojson')

    print("Loading network graph...")
    G = ox.load_graphml(graph_path)
    
    print("Loading demand nodes and food banks...")
    gdf_demand = gpd.read_file(demand_path)
    df_fb = pd.read_csv(fb_path)

    print("Snapping Food Banks to the road network...")
    fb_nodes = []
    for idx, row in df_fb.iterrows():
        if pd.notna(row['Latitude']):
            node = ox.distance.nearest_nodes(G, X=row['Longitude'], Y=row['Latitude'])
            fb_nodes.append({
                'name': row['Name'],
                'node_id': node,
                'appt_only': row['Appointment_Only']
            })

    print(f"Calculating Friction Index for {len(gdf_demand)} neighborhoods...")
    
    best_fb_names = []
    friction_scores = []
    SPEED_M_PER_MIN = 666.6  # approx 40 km/h

    count = 0
    for idx, row in gdf_demand.iterrows():
        count += 1
        if count % 100 == 0:
            print(f"   ...processed {count}/{len(gdf_demand)} neighborhoods")

        start_node = ox.distance.nearest_nodes(G, X=row['centroid_lon'], Y=row['centroid_lat'])
        
        lowest_friction = float('inf')
        best_fb = "None"

        try:
            # OPTIMIZATION: Calculate distance to ALL nodes at once using Single-Source Dijkstra
            distances = nx.single_source_dijkstra_path_length(G, start_node, weight='length')
            
            # Now just look up the 27 food banks in our pre-calculated dictionary!
            for fb in fb_nodes:
                if fb['node_id'] in distances:
                    distance_meters = distances[fb['node_id']]
                    base_time_mins = distance_meters / SPEED_M_PER_MIN
                    
                    # Apply the 1.5x friction penalty for appointment-only locations
                    total_friction = base_time_mins * 1.5 if fb['appt_only'] == 1 else base_time_mins
                        
                    if total_friction < lowest_friction:
                        lowest_friction = total_friction
                        best_fb = fb['name']
                        
        except Exception:
            pass
                
        friction_scores.append(lowest_friction)
        best_fb_names.append(best_fb)

    gdf_demand['FAFI_Score'] = friction_scores
    gdf_demand['Best_Food_Bank'] = best_fb_names

    print("Saving calculated data...")
    gdf_demand.to_file(output_path, driver="GeoJSON")
    print(f"Success! Friction data saved to {output_path}")

if __name__ == "__main__":
    main()