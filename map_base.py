import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from shapely.geometry import Polygon

from config import SCRIPT_FOLDER
from utils import clean_geometry

@st.cache_data
def load_admin1_data():
    raw_municialities = gpd.read_file(SCRIPT_FOLDER / "admin1.geojson")
    municipalities = clean_geometry(raw_municialities[['name', 'geometry']])
    municipalities = municipalities[municipalities.geometry.type.isin(['Polygon', 'MultiPolygon'])]
    game_area = gpd.GeoDataFrame(municipalities, crs="EPSG:4326")
    
    world_border = [[-180, -90], [-180, 90], [180, 90], [180, -90], [-180, -90]]
    world_poly = Polygon(world_border)
    world_gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[world_poly])
    mask_gdf = gpd.overlay(world_gdf, game_area, how='difference')
    return municipalities, game_area, mask_gdf

def admin1(m):
    municipalities, game_area, mask_gdf = load_admin1_data()
    st.session_state.poi_data["Municipality"] = municipalities
    st.session_state.game_area = game_area

    folium.GeoJson(
        mask_gdf,
        name="Out of Bounds",
        style_function=lambda x: {
            'fillColor': '#3388ff',
            'color': '#3388ff',       
            'weight': 3,
            'fillOpacity': 0.4
        },
        control=False
    ).add_to(m)
    
    folium.GeoJson(
        game_area,
        name= "Municipalities",
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 3
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            aliases=['Municipality:']
        ),
        show = True,
        control=False
    ).add_to(m)

@st.cache_data
def load_admin2_data():
    raw_districts = gpd.read_file(SCRIPT_FOLDER / "admin2.geojson")
    return clean_geometry(raw_districts)

def admin2(m):
    districts = load_admin2_data()
    st.session_state.poi_data["District"] = districts

    folium.GeoJson(
        districts,
        name = "Districts",
            style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'black',
            'weight': 2
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            aliases=['Districts:'],
        ),
        show = True
    ).add_to(m)

@st.cache_data
def load_coastline_data():
    raw_coastlines = gpd.read_file(SCRIPT_FOLDER / "coastlines.geojson")
    _, game_area, _ = load_admin1_data()
    coastlines = gpd.clip(clean_geometry(raw_coastlines), game_area)
    # Simplify coastline to reduce points and improve map rendering time
    coastlines['geometry'] = coastlines['geometry'].simplify(tolerance=0.0005)
    return coastlines

def coastline(m):
    coastlines = load_coastline_data()
    st.session_state.poi_data["Coastline"] = coastlines

    folium.GeoJson(
        coastlines,
        name="Coastline",
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': "#897CFF",
            'weight': 2
        },
        show=False
    ).add_to(m)

@st.cache_data
def load_train_data():
    raw_train_lines = gpd.read_file(SCRIPT_FOLDER / "train.geojson")
    return clean_geometry(raw_train_lines)

def train(m):
    train_lines = load_train_data()
    st.session_state.poi_data["Train Line"] = train_lines

    folium.GeoJson(
        train_lines,
        name = "Train lines",
            style_function=lambda feature: {
                'color':"#8E8E8E87",
                'opacity': 0.8,
                'dashArray': '10, 10'
        },
        show = False
    ).add_to(m)

@st.cache_data
def load_M_lines_data():
    raw_metro_lines = gpd.read_file(SCRIPT_FOLDER / "metro-lines.geojson")
    metro_lines = clean_geometry(raw_metro_lines)

    budapest_colors = {
        "M1": "gold",
        "M2": "red",
        "M3": "blue",
        "M4": "green"
    }
    def map_metro_color(row):
        ref = str(row.get('ref', ''))
        name = str(row.get('name', ''))
        for line_id, color in budapest_colors.items():
            if line_id in ref or line_id in name:
                return color
        return "#555555"
    metro_lines['colour'] = metro_lines.apply(map_metro_color, axis=1)
    return metro_lines

def M_lines(m):
    metro_lines = load_M_lines_data()
    metro_layer = folium.FeatureGroup(name="Metro Lines")
    folium.GeoJson(
        metro_lines,
        name = "Metro Lines",
            style_function=lambda feature: {
                'color': feature['properties'].get('colour', '#555555'),
                'width': 1
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['ref'],
            labels = False
        ),
        show = True
    ).add_to(metro_layer)
    metro_layer.add_to(m)

@st.cache_data
def load_T_lines_data():
    raw_TLines = gpd.read_file(SCRIPT_FOLDER / "tram-lines.geojson")
    return clean_geometry(raw_TLines)

def T_lines(m):
    tram_lines = load_T_lines_data()
    folium.GeoJson(
        tram_lines,
        name = "Tram Lines",
        style_function=lambda feature: {
            'color': feature['properties'].get('colour', '#f2d004'),
            'width': 1
        },
        show = True
    ).add_to(m)

@st.cache_data
def load_stations_data():
    _, game_area, _ = load_admin1_data()
    raw_Tstations = gpd.read_file(SCRIPT_FOLDER / "tram-stations.geojson")
    raw_Mstations = gpd.read_file(SCRIPT_FOLDER / "metro-stations.geojson")

    tram_stations = clean_geometry(raw_Tstations[['name','geometry']].drop_duplicates(subset=['name']))
    tram_stations = gpd.clip(tram_stations, game_area)

    start_T = tram_stations[tram_stations['name'] == "Deák Ferenc tér"][['name','geometry']]
    tram_stations = tram_stations[~tram_stations['name'].isin(start_T['name'])]

    metro_stations = clean_geometry(raw_Mstations[['name','geometry']].drop_duplicates(subset=['name']))
    metro_stations = gpd.clip(metro_stations, game_area)
    
    start_M = metro_stations[metro_stations['name'] == "Deák Ferenc tér"][['name','geometry']]
    metro_stations = metro_stations[~metro_stations['name'].isin(start_M['name'])]

    start = pd.concat([start_M,start_T])
    all_station = pd.concat([metro_stations,tram_stations,start])
    
    return tram_stations, metro_stations, start, all_station

def stations(m):
    tram_stations, metro_stations, start, all_station = load_stations_data()

    folium.GeoJson(
        start,
        name = "Starting Point",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='black',
                icon='flag-checkered', 
                prefix='fa')
        ),
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels=False
        ),
        show = True
    ).add_to(m)
    
    folium.GeoJson(
        metro_stations,
        name = "Metro Stations",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='darkblue',
                icon='train-subway', 
                prefix='fa')
        ),
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels=False
        ),
        show = False
    ).add_to(m)

    folium.GeoJson(
        tram_stations,
        name = "Tram Stations",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='red',
                icon='train-tram', 
                prefix='fa')
        ),
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels=False
        ),
        show = False
    ).add_to(m)
    
    hiding_zone = folium.FeatureGroup(name="Hiding Zone", show=False)

    for idx, row in all_station.iterrows():
        hidingZones(hiding_zone,500,row.geometry.y,row.geometry.x)

    hiding_zone.add_to(m)

def hidingZones(group,radius,lat,long):
    folium.Circle(
        location=[lat, long],
        radius=radius,
        color = '#5F5F5F',
        weight=0.5,
        fill_color = '#5F5F5F',
        fill_opacity=0.3,
        show=False,
    ).add_to(group)
