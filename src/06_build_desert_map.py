import os
import geopandas as gpd
import pandas as pd
import folium
import branca.colormap as cm
from folium import Element

def main():
    print("Generating Polished Food Desert Heatmap...")
    
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    demand_path = os.path.join(base_dir, 'data', 'processed', 'demand_with_friction.geojson')
    fb_path = os.path.join(base_dir, 'data', 'raw', 'food_banks.csv')
    boundary_path = os.path.join(base_dir, 'data', 'raw', 'municipal_boundary.geojson')
    map_output_path = os.path.join(base_dir, 'york_region_food_deserts.html')

    gdf = gpd.read_file(demand_path)
    df_fb = pd.read_csv(fb_path)
    
    # Load boundary and STRIP OUT metadata (like timestamps) that crash the JSON reader
    gdf_boundary = gpd.read_file(boundary_path)
    gdf_boundary = gdf_boundary[['geometry']] 

    # Clean data
    gdf['MED_AFT_TAX_INC_HH'] = pd.to_numeric(gdf['MED_AFT_TAX_INC_HH'], errors='coerce')
    gdf['FAFI_Score'] = pd.to_numeric(gdf['FAFI_Score'], errors='coerce')

    # Filter vulnerable neighborhoods
    gdf_vuln = gdf[(gdf['MED_AFT_TAX_INC_HH'] > 0) & (gdf['FAFI_Score'] > 0) & (gdf['MED_AFT_TAX_INC_HH'] < 95000)].copy()

    # --- UI FORMATTING (Money and Decimals) ---
    # Create new columns just for the display tooltips
    gdf_vuln['Income_Display'] = gdf_vuln['MED_AFT_TAX_INC_HH'].apply(lambda x: f"${x:,.0f}")
    gdf_vuln['FAFI_Display'] = gdf_vuln['FAFI_Score'].round(3)

    # Create the Color Map
    min_fafi = gdf_vuln['FAFI_Score'].min()
    max_fafi = gdf_vuln['FAFI_Score'].max()
    colormap = cm.LinearColormap(
        colors=['#FFEDA0', '#FEB24C', '#F03B20', '#BD0026'], 
        vmin=min_fafi, vmax=max_fafi,
        caption='FAFI Score (Higher = Harder to Access Food Bank)'
    )

    # Build the base map
    esri_dark = 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}'
    york_map = folium.Map(location=[44.0, -79.40], zoom_start=10, tiles=esri_dark, attr='Esri')

    # Add York Region Outline Border
    folium.GeoJson(
        gdf_boundary,
        name='York Region Boundary',
        style_function=lambda x: {'fillColor': 'transparent', 'color': '#ffffff', 'weight': 2, 'opacity': 0.5}
    ).add_to(york_map)

    # Add the precise interactive layer
    folium.GeoJson(
        gdf_vuln,
        name='Food Deserts',
        style_function=lambda feature: {
            'fillColor': colormap(feature['properties']['FAFI_Score']),
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.8
        },
        highlight_function=lambda feature: {
            'weight': 3,
            'color': 'white',
            'fillOpacity': 1
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=['Income_Display', 'FAFI_Display', 'Best_Food_Bank'],
            aliases=['Median After-Tax Income:', 'Friction Score (FAFI):', 'Assigned Hub:'],
            labels=True,
            sticky=True
        )
    ).add_to(york_map)

    colormap.add_to(york_map)

    # --- UI HACK: Make legend text white so it's visible on dark map ---
    css = """
    <style>
    .legend text { fill: white !important; font-weight: bold; }
    .legend .caption { fill: white !important; font-weight: bold; }
    </style>
    """
    york_map.get_root().html.add_child(Element(css))

    # Add Food Banks (With wider popups so text isn't squished)
    for idx, row in df_fb.iterrows():
        if pd.notna(row['Latitude']):
            marker_color = 'blue' if row['Type'] == 'Primary Hub' else 'green'
            # Use HTML to prevent text wrapping
            popup_html = f"<div style='white-space: nowrap; font-size: 14px;'><b>{row['Name']}</b></div>"
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=marker_color, icon='info-sign')
            ).add_to(york_map)

    york_map.save(map_output_path)
    print(f"Success! Polished map saved to {map_output_path}")

if __name__ == "__main__":
    main()