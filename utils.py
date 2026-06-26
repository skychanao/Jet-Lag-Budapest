import pandas as pd
import geopandas as gpd
import streamlit as st

def clean_geometry(gdf):
    """Keep standard shapes and drop rows with missing geometry."""
    gdf = gdf.dropna(subset=['geometry'])
    supported_shapes = ['Point', 'MultiPoint', 'LineString', 'MultiLineString', 'Polygon', 'MultiPolygon']
    gdf = gdf[gdf.geometry.type.isin(supported_shapes)]
    # Convert datetime columns to string to avoid JSON serialization errors
    for col in gdf.select_dtypes(include=['datetime', 'datetimetz']).columns:
        gdf[col] = gdf[col].astype(str)

    return gdf

def read_coord(coord):
    """Format coordinate read from streamlit input."""
    if "," in coord:
        parts = coord.split(',')
        try:
            latitude = float(parts[0].strip())
            longitude = float(parts[1].strip())
        except ValueError:
            st.sidebar.error("Error: Please only type numbers.")
        return latitude, longitude

def get_poi_data(category_name):
    """Fetch POI data from session state."""
    if category_name is None:
        return None
    if category_name in st.session_state.poi_data:
        return st.session_state.poi_data[category_name]

def filter_close_stations(stations_gdf, min_dist_m=500):
    """Filter out stations that are too close to each other (less than min_dist_m) to reduce overlap."""
    if stations_gdf.empty:
        return stations_gdf
        
    proj = stations_gdf.to_crs(epsg=32634)
    to_drop = set()
    for i, row in proj.iterrows():
        if i in to_drop:
            continue
        dists = proj.geometry.distance(row.geometry)
        close = dists[(dists < min_dist_m) & (dists.index != i)].index
        to_drop.update(close)
    
    return stations_gdf.drop(list(to_drop))
