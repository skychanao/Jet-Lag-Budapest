import folium
import geopandas as gpd
import streamlit as st

from config import SCRIPT_FOLDER
from utils import clean_geometry

def parks(m):
    raw_parks = gpd.read_file(SCRIPT_FOLDER / "parks.geojson")
    parks = clean_geometry(raw_parks)
    parks['label'] = parks['label'].str.split('-').str[0].str.strip()

    st.session_state.poi_data["Park"] = parks

    folium.GeoJson(
        parks,
        name = "Parks",
        marker=folium.Marker(
            icon=folium.Icon(
                color='green', 
                icon='tree', 
                prefix='fa')
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def amusementParks(m):
    raw_amusementParks = gpd.read_file(SCRIPT_FOLDER / "Amusement-Park.geojson")
    amusementParks = clean_geometry(raw_amusementParks)
    amusementParks['label'] = raw_amusementParks['label'].str.split('-').str[0].str.strip()

    st.session_state.poi_data["Amusement Park"] = amusementParks

    folium.GeoJson(
        amusementParks,
        name = "Amusement Parks",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='pink',
                icon='ticket', 
                prefix='fa')
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def zoo(m):
    raw_zoos = gpd.read_file(SCRIPT_FOLDER / "zoos.geojson")
    zoos = clean_geometry(raw_zoos)
    zoos['label'] = zoos['label'].str.split(' - ').str[0].str.strip()

    st.session_state.poi_data["Zoo"] = zoos

    folium.GeoJson(
        zoos,
        name = "Zoos",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='darkred',
                icon='paw', 
                prefix='fa')
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def aquarium(m):
    raw_aquariums = gpd.read_file(SCRIPT_FOLDER / "aquariums.geojson")
    aquariums = clean_geometry(raw_aquariums)
    aquariums['label'] = aquariums['label'].str.split(' - ').str[0].str.strip()

    st.session_state.poi_data["Aquarium"] = aquariums

    folium.GeoJson(
        aquariums,
        name = "Aquariums",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='lightblue',
                icon='fish', 
                prefix='fa')
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def golf(m):
    raw_golfcourses = gpd.read_file(SCRIPT_FOLDER / "golf-courses.geojson")
    golf_courses = clean_geometry(raw_golfcourses)
    golf_courses['label'] = golf_courses['label'].str.split(' - ').str[0].str.strip()

    st.session_state.poi_data["Golf Course"] = golf_courses

    folium.GeoJson(
        golf_courses,
        name = "Golf Courses",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='darkgreen',
                icon='golf-ball', 
                prefix='fa')
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def museum(m):
    raw_museums = gpd.read_file(SCRIPT_FOLDER / "museums.geojson")
    museums = clean_geometry(raw_museums)
    museums['label'] = museums['label'].str.split(' - ').str[0].str.strip()

    st.session_state.poi_data["Museum"] = museums

    folium.GeoJson(
        museums,
        name = "Museums",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='orange',
                icon='university', 
                prefix='fa')
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def theaters(m):
    raw_theaters = gpd.read_file(SCRIPT_FOLDER / "movie-theaters.geojson")
    theaters = clean_geometry(raw_theaters)
    theaters['label'] = theaters['label'].str.split(' - ').str[0].str.strip()

    st.session_state.poi_data["Movie Theater"] = theaters

    folium.GeoJson(
        theaters,
        name = "Movie Theaters",
        marker=folium.Marker(
            icon=folium.Icon(
            color='cadetblue',
            icon='film', 
            prefix='fa')
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def hospitals(m):
    raw_hospitals = gpd.read_file(SCRIPT_FOLDER / "hospitals.geojson")
    hospitals = clean_geometry(raw_hospitals)
    hospitals['label'] = hospitals['label'].str.split(' - ').str[0].str.strip()

    st.session_state.poi_data["Hospital"] = hospitals

    folium.GeoJson(
        hospitals,
        name = "Hospitals",
        marker=folium.Marker(
            icon=folium.Icon(
                color='red',
                icon='ambulance',
                prefix='fa',
            )
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def libraries(m):
    raw_libraries = gpd.read_file(SCRIPT_FOLDER / "libraries.geojson")
    libraries = clean_geometry(raw_libraries)
    libraries['label'] = libraries['label'].str.split(' - ').str[0].str.strip()

    st.session_state.poi_data["Library"] = libraries

    folium.GeoJson(
        libraries,
        name = "Libraries",
        marker=folium.Marker(
            icon=folium.Icon(
                color='lightred', 
                icon='book', 
                prefix='fa')
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def consulates(m):
    raw_consulates = gpd.read_file(SCRIPT_FOLDER / "consulates.geojson")
    consulates = clean_geometry(raw_consulates)
    consulates['label'] = consulates['label'].str.split(' - ').str[0].str.strip()

    st.session_state.poi_data["Consluate"] = consulates

    folium.GeoJson(
        consulates,
        name = "Consluates",
        marker=folium.Marker(
            icon=folium.Icon(
                color='darkpurple',
                icon='globe',
                prefix='fa')
        ),
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)
