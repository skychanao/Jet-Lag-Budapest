import pandas as pd
import geopandas as gpd
import folium
import streamlit as st
from shapely.geometry import Polygon

from config import SCRIPT_FOLDER
from utils import clean_geometry

def admin1(m):
    #read Stockholm json data
    raw_municialities = gpd.read_file(SCRIPT_FOLDER / "admin1.geojson")

    #clean up data
    municipalities = clean_geometry(raw_municialities[['name', 'geometry']])
    # Filter to only keep Polygon and MultiPolygon geometries for overlay mapping
    municipalities = municipalities[municipalities.geometry.type.isin(['Polygon', 'MultiPolygon'])]
    st.session_state.poi_data["Municipality"] = municipalities

    #build a GeoDataFrame with the cleaned data
    game_area = gpd.GeoDataFrame(municipalities, crs="EPSG:4326")
    st.session_state.game_area = game_area

    #Create a mask, which plots world_borer - game_area,
    world_border = [[-180, -90], [-180, 90], [180, 90], [180, -90], [-180, -90]]
    world_poly = Polygon(world_border)
    world_gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[world_poly])
    mask_gdf = gpd.overlay(world_gdf, game_area, how='difference')
    
    #Add the masked layers to the map
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
    
    #Add boundaries of municipalities to the map
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


def admin2(m):
    raw_districts = gpd.read_file(SCRIPT_FOLDER / "admin2.geojson")
    districts = clean_geometry(raw_districts)
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

def coastline(m):
    raw_coastlines = gpd.read_file(SCRIPT_FOLDER / "coastlines.geojson")
    game_area = st.session_state.game_area
    coastlines = gpd.clip(clean_geometry(raw_coastlines), game_area)
    st.session_state.poi_data["Coastline"] = coastlines

    #Plot coastlines on the map
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

def train(m):
    raw_train_lines = gpd.read_file(SCRIPT_FOLDER / "train.geojson")
    train_lines = clean_geometry(raw_train_lines)

    #reduce length of tram line names 
    train_lines['name'] = train_lines['name'].str.split(':').str[0].str.strip()
    st.session_state.poi_data["Train Line"] = train_lines


    #plot train lines
    folium.GeoJson(
        train_lines,
        name = "Train lines",
            style_function=lambda feature: {
                'color':"#8E8E8E87",
                'opacity': 0.8,
                'dashArray': '10, 10'
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels = False
        ),
        show = True
    ).add_to(m)

def M_lines(m):
    raw_metro_lines = gpd.read_file(SCRIPT_FOLDER / "metro-lines.geojson")
    metro_lines = clean_geometry(raw_metro_lines)

    #reduce length of metro line names
    metro_lines['name'] = metro_lines['name'].str[:13]
    metro_layer = folium.FeatureGroup(name="Metro Lines")
    #plot metro lines
    folium.GeoJson(
        metro_lines,
        name = "Metro Lines",
            style_function=lambda feature: {
                'color': feature['properties'].get('colour', '#555555'),
                'width': 1
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels = False
        ),
        show = True
    ).add_to(metro_layer)
    
    metro_layer.add_to(m)

def T_lines(m):
    raw_TLines = gpd.read_file(SCRIPT_FOLDER / "tram-lines.geojson")
    tram_lines = clean_geometry(raw_TLines[['name','geometry','colour']])

    #reduce length of tram line names 
    tram_lines['name'] = tram_lines['name'].str.split(':').str[0].str.strip()

    #plot tram lines
    folium.GeoJson(
        tram_lines,
        name = "Tram Lines",
        style_function=lambda feature: {
            'color': feature['properties'].get('colour', '#555555'),
            'width': 1
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['name'],
            labels = False
        ),
        show = True
    ).add_to(m)

def stations(m):
    game_area = st.session_state.game_area
    #read data from GeoJson
    raw_Tstations = gpd.read_file(SCRIPT_FOLDER / "tram-stations.geojson")
    raw_Mstations = gpd.read_file(SCRIPT_FOLDER / "metro-stations.geojson")

    #extract name and geometry of unique tram stations 
    tram_stations = clean_geometry(raw_Tstations[['name','geometry']].drop_duplicates(subset=['name']))
    #only select stations within the game area
    tram_stations = gpd.clip(tram_stations, game_area)
    #select starting tram stations of the game
    start_T = tram_stations[tram_stations['name'] == "T-Centralen"][['name','geometry']]
    #remove starting tram stations from other tram stations
    tram_stations = tram_stations[~tram_stations['name'].isin(start_T['name'])]

    #extract name and geometry of unique metro stations 
    metro_stations = clean_geometry(raw_Mstations[['name','geometry']].drop_duplicates(subset=['name']))
    #only select stations within the game area
    metro_stations = gpd.clip(metro_stations, game_area)
    #select starting metro stations of the game
    start_M = metro_stations[metro_stations['name'] == "T-Centralen"][['name','geometry']]
    #remove starting tram stations from other tram stations
    metro_stations = metro_stations[~metro_stations['name'].isin(start_M['name'])]

    #plot starting points
    start = pd.concat([start_M,start_T])

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
    
    #plot stations with metro
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

    #plot stations with tram
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
    
    # plop hiding zones
    all_station = pd.concat([metro_stations,tram_stations,start])
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
