import pandas as pd
import geopandas as gpd
import streamlit as st

def clean_geometry(gdf):
    """Keep standard shapes and drop rows with missing geometry."""
    gdf = gdf.dropna(subset=['geometry'])
    supported_shapes = ['Point', 'MultiPoint', 'LineString', 'MultiLineString', 'Polygon', 'MultiPolygon']
    gdf = gdf[gdf.geometry.type.isin(supported_shapes)]
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
