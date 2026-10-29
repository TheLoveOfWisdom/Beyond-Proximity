import os
import geopandas as gpd
import pandas as pd
import folium

def main():
    print("Starting Heatmap Generation...")
    
    # 1. Setup file paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    demand_geojson_path = os.path.join(base_dir, 'data', 'processed', 'demand_nodes.geojson')
    food_banks_path = os.path.join(base_dir, 'data', 'raw', 'food_banks.csv')
    heatmap_output_path = os.path.join(base_dir, 'york_region_heatmap.html')

    # 2. Load the data
    try:
        gdf = gpd.read_file(demand_geojson_path)
        fb_df = pd.read_csv(food_banks_path)
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Clean the income data (StatCan uses None or 0 for empty neighborhoods like parks)
    # We filter out invalid data so it doesn't mess up our map colors
    gdf['MED_AFT_TAX_INC_HH'] = pd.to_numeric(gdf['MED_AFT_TAX_INC_HH'], errors='coerce')
    gdf_clean = gdf[gdf['MED_AFT_TAX_INC_HH'] > 0]

   # 3. Initialize the Map
    # Switch to Esri Dark Gray Base (No API key required, looks professional)
    print("Building the map layers...")
    esri_dark = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
    esri_attr = 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'

    york_map = folium.Map(
        location=[44.0, -79.40], 
        zoom_start=10, 
        tiles=esri_dark, 
        attr=esri_attr
    )

    # 4. Create the Choropleth (Heatmap) layer
    # YlOrRd_r means Yellow-Orange-Red (Reversed). Red = Low Income, Yellow = High Income
    folium.Choropleth(
        geo_data=gdf_clean,
        name='Household Income',
        data=gdf_clean,
        columns=['DAUID', 'MED_AFT_TAX_INC_HH'],
        key_on='feature.properties.DAUID',
        fill_color='YlOrRd_r', 
        fill_opacity=0.7,
        line_opacity=0.1,
        legend_name='Median After-Tax Household Income ($)'
    ).add_to(york_map)

    # 5. Add the Food Banks on top
    for idx, row in fb_df.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            marker_color = 'blue' if row['Type'] == 'Primary Hub' else 'green'
            
            popup_info = f"<b>{row['Name']}</b><br>Type: {row['Type']}"
            
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_info, max_width=300),
                icon=folium.Icon(color=marker_color, icon='info-sign')
            ).add_to(york_map)

    # 6. Save the map
    york_map.save(heatmap_output_path)
    print(f"Success! Heatmap saved to {heatmap_output_path}")

if __name__ == "__main__":
    main()