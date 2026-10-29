import pandas as pd
import folium
import os

def main():
    print("Starting map generation...")
    
    # Define file paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_csv_path = os.path.join(base_dir, 'data', 'raw', 'food_banks.csv')
    map_output_path = os.path.join(base_dir, 'york_region_base_map.html')

    try:
        df = pd.read_csv(raw_csv_path)
        print(f"Loaded {len(df)} food banks from CSV.")
    except FileNotFoundError:
        print(f"Error: Could not find {raw_csv_path}.")
        return

    # Initialize the base map using Esri tiles for a clean, academic look
    esri_tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}'
    esri_attr = 'Tiles &copy; Esri'

    york_region_map = folium.Map(
        location=[44.0, -79.40], 
        zoom_start=10, 
        tiles=esri_tiles, 
        attr=esri_attr
    )

    # Plot each food bank on the map with specific color coding and data popups
    for idx, row in df.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            marker_color = 'blue' if row['Type'] == 'Primary Hub' else 'green'
            
            popup_text = f"""
            <div style="font-family: Arial; font-size: 12px;">
                <b>{row['Name']}</b><br>
                Type: {row['Type']}<br>
                Hours/Week: {row['Hours_Per_Week']}<br>
                Appt Only: {'Yes' if row['Appointment_Only'] == 1 else 'No'}
            </div>
            """
            
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=marker_color, icon='info-sign')
            ).add_to(york_region_map)

    york_region_map.save(map_output_path)
    print(f"Success! Map saved to {map_output_path}")

if __name__ == "__main__":
    main()