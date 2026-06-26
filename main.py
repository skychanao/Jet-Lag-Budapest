import warnings
import streamlit as st
import folium
import folium.plugins
from folium.plugins import Draw
from streamlit_folium import st_folium

from config import setup_environment
from ui import streamlit_features
from seeking import draw_seeking_tools

# Base Maps
from map_base import (
    admin1, admin2, coastline,
    train, M_lines, T_lines, stations
)

# POIs
from map_poi import (
    parks, amusementParks, zoo, aquarium, golf,
    museum, theaters, hospitals, libraries, consulates
)

class JetLagApp:
    def __init__(self):
        # Ignore warnings
        warnings.filterwarnings("ignore")
        
        # Setup OS and logging
        setup_environment()
        
        # Setup Streamlit
        st.set_page_config(page_title="Budapest Map", layout="wide")

    def run(self):
        # Streamlit Features (Sidebar, UI state)
        streamlit_features()

        m = folium.Map(
            location=(47.50094518780837, 19.108623740106655),
            tiles="OpenStreetMap",
            max_bounds=True,
            zoom_start=11,
            min_zoom=10,
            max_zoom=20,
            control_scale=True,
        )

        cartonDB = 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png'
        folium.TileLayer(
            max_bounds=True,
            tiles=cartonDB,
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            name='cartonDB',
            subdomains='abcd',
            zoom_start=11,
            min_zoom=10,
            max_zoom=20,
        ).add_to(m)

        # Base Map features
        admin1(m)
        admin2(m)
        # coastline(m)
        train(m)
        M_lines(m)
        T_lines(m)
        stations(m)

        # Point of Interest for Seeking
        parks(m)
        amusementParks(m)
        zoo(m)
        # aquarium(m)
        golf(m)
        museum(m)
        theaters(m)
        hospitals(m)
        libraries(m)
        consulates(m)

        # Seeking Tools
        draw_seeking_tools(m)

        # Add location request
        folium.plugins.LocateControl(auto_start=False).add_to(m)

        # Add layer control
        folium.LayerControl().add_to(m)

        # Add draw function
        Draw(export=False).add_to(m)

        # Render Map in Streamlit
        st_folium(m, use_container_width=True, returned_objects=[])

if __name__ == "__main__":
    app = JetLagApp()
    app.run()
