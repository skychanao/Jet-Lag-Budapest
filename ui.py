import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd

from utils import read_coord, get_poi_data

def streamlit_features():

    if "radars" not in st.session_state:
        st.session_state.radars = []
    if "thermometer" not in st.session_state:
        st.session_state.thermometer = []
    if "matching" not in st.session_state:
        st.session_state.matching = []
    if "measure" not in st.session_state:
        st.session_state.measure=[]
    if "poi_data" not in st.session_state:
        st.session_state.poi_data = {}

    error_placeholder = st.empty()

    # read user input
    with st.sidebar:

        location = streamlit_geolocation()
        tab_radar, tab_therm,tab_matching, tab_measuring = st.tabs(["Radar", "Thermometer","Matching","Measuring"])

        #Copy auto-filled GPS coordinate into text box
        def copy_to_text_box(target_key):
            if location['latitude'] is not None and location['longitude'] is not None:
                #Format Number
                st.session_state[target_key] = f"{location['latitude']}, {location['longitude']}"
            else:
                st.warning("Still searching for GPS...")

        #radar Tab
        with tab_radar:
            
            st.button("Autofill Coordinates", on_click=copy_to_text_box, args=("coord_input",), use_container_width=True)

            coordinate = st.text_input(label = "Coordinate", placeholder = "lat, lon (eg: 59.0, 18.0)",key="coord_input")
            radius = st.number_input(label = "Radius(km)", placeholder = "x (km)", step=0.5, min_value=0.0)
            radar_type = st.radio("Radar Type", ["Hit", "Miss"])


            if st.button("Plot Radar", use_container_width=True):
                #Read Coordinates
                latitude = -99999.99
                longitude = -99999.99
                updated_R = False
                try:
                    latitude,longitude = read_coord(coordinate)    
                    updated_R = True
                except TypeError:
                    error_placeholder.error("Error: Invalid RADAR Input.")
                if updated_R:
                    radar_number = len(st.session_state.radars) + 1
                    st.session_state.radars.append({
                            "lat": latitude,
                            "lon": longitude,
                            "size": radius,
                            "type": radar_type,
                            "counter": radar_number
                        })

            if st.button("Undo Radar", use_container_width=True):
                if st.session_state.radars:
                    st.session_state.radars.pop() # Removes the last drawn radar   
        
        #Termometer Tab
        with tab_therm:

            st.button("Autofill Starting Point", on_click=copy_to_text_box, args=("coord_start",), use_container_width=True)
            st.button("Autofill Ending Point", on_click=copy_to_text_box,args=("coord_end",), use_container_width=True)

            start = st.text_input(label = "Starting Point", placeholder = "lat, lon (eg: 59.0, 18.0)",key="coord_start")
            end = st.text_input(label = "End Point", placeholder = "lat, lon (eg: 59.0, 18.0)",key="coord_end")
            therm_type = st.radio("Result", ["Hotter", "Colder"])

            if st.button("Plot Thermometer", use_container_width=True):
                #Read Coordinates
                start_latitude = -99999.99
                start_longitude = -99999.99
                end_latitude = -99999.99
                end_longitude = -99999.99
                updated_T = False
                try:
                    start_latitude, start_longitude = read_coord(start)
                    end_latitude, end_longitude = read_coord(end)
                    updated_T = True
                except TypeError:
                    error_placeholder.error("Error: Invalid THERMOMETER Input.")

                if updated_T:
                    thermometer_number = len(st.session_state.thermometer) + 1
                    thermometer_name = f"{thermometer_number}"  
                    st.session_state.thermometer.append({
                        "start_lat": start_latitude,
                        "start_lon": start_longitude,
                        "end_lat": end_latitude,
                        "end_lon": end_longitude,
                        "type": therm_type,
                        "name": thermometer_name
                    })

            if st.button("Undo Thermometer", use_container_width=True):
                if st.session_state.thermometer:
                    st.session_state.thermometer.pop() # Removes the last drawn radar

        # Matching Tab
        with tab_matching:
            categories_matching = ["Municipality","District","Park","Amusement Park", "Zoo","Aquarium","Golf Course","Museum",
                            "Movie Theater", "Hospital", "Library","Consluate"]
            selected_category = st.pills("Question", options = categories_matching)

            poi_gdf = get_poi_data(selected_category)
            if poi_gdf is not None:
                if selected_category != "Municipality" and selected_category != "District":
                    poi_names = poi_gdf['label'].tolist()
                else:
                    if 'ref' in poi_gdf.columns:
                        # Convert ref to numeric for proper numerical sorting (so 2 comes before 10)
                        ref_numeric = pd.to_numeric(poi_gdf['ref'], errors='coerce')
                        sorted_gdf = poi_gdf.loc[ref_numeric.sort_values(na_position='last').index]
                        poi_names = sorted_gdf['name'].tolist()
                    else:
                        poi_names = poi_gdf['name'].tolist()

                selected_poi = st.selectbox("Your Closest/Current POI", poi_names)
                matching_type = st.radio("Result", ["Same", "Different"])

            if st.button("Plot Matching", use_container_width=True):
                    matching_counter = len(st.session_state.matching) + 1
                    st.session_state.matching.append({
                        "category": selected_category,
                        "poi_name": selected_poi,
                        "type": matching_type,
                        "counter" : matching_counter
                    })

            if st.button("Undo Matching", use_container_width=True):
                if st.session_state.matching:
                    st.session_state.matching.pop()

        #Measuring Tab
        with tab_measuring:
            #Read Input Coordinate
            st.button("Autofill Coordinates", on_click=copy_to_text_box, args=("coord_measure",), use_container_width=True, key="measure_auto")
            coordinate = st.text_input(label = "Coordinate", placeholder = "lat, lon (eg: 59.0, 18.0)",key="coord_measure")
            
            #Read Measuring question
            categories_measuring = ["Train Line","Coastline","Park","Amusement Park", "Zoo","Aquarium","Golf Course","Museum",
                "Movie Theater", "Hospital", "Library","Consluate"]
            selected_category = st.pills("Question", options = categories_measuring, key="measure_cat")
            measuring_type = st.radio("Result", ["Closer", "Further"])

            if st.button("Plot measuring", use_container_width=True):
                updated_R = False
                try:
                    latitude,longitude = read_coord(coordinate)    
                    updated_R = True
                except TypeError:
                    error_placeholder.error("Error: Invalid Coordinate Input.")
                if updated_R:
                    measuring_counter = len(st.session_state.measure) + 1
                    st.session_state.measure.append({
                        "lat":latitude,
                        "lon": longitude,
                        "category": selected_category,
                        "type": measuring_type,
                        "counter" : measuring_counter
                    })

            if st.button("Undo Measuring", use_container_width=True):
                if st.session_state.measure:
                    st.session_state.measure.pop()
