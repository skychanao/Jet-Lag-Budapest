import folium
import geopandas as gpd
import streamlit as st

from config import SCRIPT_FOLDER
from utils import clean_geometry

@st.cache_data
def load_poi_data(filename, split_char='-'):
    raw_data = gpd.read_file(SCRIPT_FOLDER / filename)
    data = clean_geometry(raw_data)
    if 'label' in data.columns:
        data['label'] = data['label'].str.split(split_char).str[0].str.strip()
    return data

def add_poi_layer(m, df, session_key, name, color, icon):
    st.session_state.poi_data[session_key] = df
    folium.GeoJson(
        df,
        name=name,
        marker=folium.Marker(
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ),
        popup=folium.GeoJsonPopup(fields=['label'], labels=False) if 'label' in df.columns else None,
        show=False
    ).add_to(m)

def parks(m):
    df = load_poi_data("parks.geojson", '-')
    add_poi_layer(m, df, "Park", "Parks", "green", "tree")

def amusementParks(m):
    df = load_poi_data("Amusement-Park.geojson", '-')
    add_poi_layer(m, df, "Amusement Park", "Amusement Parks", "pink", "ticket")

def zoo(m):
    df = load_poi_data("zoos.geojson", ' - ')
    add_poi_layer(m, df, "Zoo", "Zoos", "darkred", "paw")

def aquarium(m):
    df = load_poi_data("aquariums.geojson", ' - ')
    add_poi_layer(m, df, "Aquarium", "Aquariums", "lightblue", "fish")

def golf(m):
    df = load_poi_data("golf-courses.geojson", ' - ')
    add_poi_layer(m, df, "Golf Course", "Golf Courses", "darkgreen", "golf-ball")

def museum(m):
    df = load_poi_data("museums.geojson", ' - ')
    add_poi_layer(m, df, "Museum", "Museums", "orange", "university")

def theaters(m):
    df = load_poi_data("movie-theaters.geojson", ' - ')
    add_poi_layer(m, df, "Movie Theater", "Movie Theaters", "cadetblue", "film")

def hospitals(m):
    df = load_poi_data("hospitals.geojson", ' - ')
    add_poi_layer(m, df, "Hospital", "Hospitals", "red", "ambulance")

def libraries(m):
    df = load_poi_data("libraries.geojson", ' - ')
    add_poi_layer(m, df, "Library", "Libraries", "lightred", "book")

def consulates(m):
    df = load_poi_data("consulates.geojson", ' - ')
    add_poi_layer(m, df, "Consluate", "Consluates", "darkpurple", "globe")
