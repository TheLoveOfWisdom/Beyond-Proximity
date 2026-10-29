import os
import osmnx as ox
import networkx as nx

def main():
    print("Starting Road Network Generation for York Region...")
    
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, 'data', 'processed')
    os.makedirs(output_dir, exist_ok=True)
    graph_output_path = os.path.join(output_dir, 'york_region_network.graphml')

    # If we already downloaded the map, don't do it again
    if os.path.exists(graph_output_path):
        print(f"Network graph already exists at {graph_output_path}")
        return

    # Define the area we want to download
    place_name = "York Region, Ontario, Canada"

    print(f"Downloading street network for {place_name}...")
    print("(This may take 2-5 minutes. Do not close the terminal!)")
    
    try:
        # Download the driving network (roads, speed limits, one-ways)
        # We use 'drive' first to establish the baseline car friction
        G = ox.graph_from_place(place_name, network_type='drive')
        print(f"Success! Downloaded {len(G.nodes)} intersections and {len(G.edges)} roads.")
        
        # Save the graph to a file so we don't have to download it ever again
        print("Saving network to file...")
        ox.save_graphml(G, graph_output_path)
        print(f"Network saved to {graph_output_path}")
        
    except Exception as e:
        print(f"Error downloading the network: {e}")

if __name__ == "__main__":
    main()