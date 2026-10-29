import os
import geopandas as gpd
import warnings

def main():
    print("Processing census geometries...")
    
    # Setup paths for input GeoJSON and output processed data
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, 'data', 'raw', 'total_income.geojson')
    output_dir = os.path.join(base_dir, 'data', 'processed')
    output_file = os.path.join(output_dir, 'demand_nodes.geojson')
    
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(input_file):
        print(f"Error: Source data not found at {input_file}")
        return

    # Load the Dissemination Area polygons
    gdf = gpd.read_file(input_file)
    print(f"Successfully loaded {len(gdf)} dissemination areas.")
    
    # Standardize coordinate system to Lat/Lon (WGS84)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    # Calculate geographic centroids (center dots) for each polygon 
    # These will act as the starting nodes for the A* pathfinding algorithm
    gdf['centroid'] = gdf.geometry.centroid
    gdf['centroid_lat'] = gdf['centroid'].y
    gdf['centroid_lon'] = gdf['centroid'].x

    # Suppress the Earth curve warning to keep the terminal clean
    warnings.filterwarnings('ignore')

    print("\n--- Income Related Columns ---")
    # Search for any column that has 'INC' (Income) in its name
    income_cols = [col for col in gdf.columns if 'INC' in col.upper()]
    print(income_cols)
    print("------------------------------------\n")

    # Drop the raw centroid object because it can't be saved to JSON, keep lat/lon
    gdf_clean = gdf.drop(columns=['centroid'])
    gdf_clean.to_file(output_file, driver="GeoJSON")
    print(f"Processed demand nodes saved to {output_file}")

if __name__ == "__main__":
    main()