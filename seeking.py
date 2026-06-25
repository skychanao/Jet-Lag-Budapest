import folium
import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString, MultiPoint
from shapely.ops import unary_union, voronoi_diagram

from utils import get_poi_data

def voronoi(gdf):
    world_border = MultiPoint([(-90,-90), (90,-90),(-90,90),(90,90)]).envelope
    multipoint = MultiPoint(gdf.geometry.values)
    voronoi_collection = voronoi_diagram(multipoint, envelope=world_border)

    # Create a GeoDataFrame with the Voronoi polygons:
    voronoi_gdf = gpd.GeoDataFrame(geometry=list(voronoi_collection.geoms), crs='EPSG:4326')
    return pd.concat([voronoi_gdf,gdf])

def draw_seeking_tools(m):
    game_area = st.session_state.game_area
    # Setup marker groups
    radar_list = folium.FeatureGroup(name="Radar Points")
    thermometer_list = folium.FeatureGroup(name="Thermometer Points")
    matching_list = folium.FeatureGroup(name="Matching Questions")
    measuring_list = folium.FeatureGroup(name="Measuring Questions")

    # List to store all shapes to be merged
    shapes_to_merge = [] 
    
    # Extract the total game board shape for clipping
    game_board_shape = game_area.geometry.unary_union

    # PROCESS RADAR
    if "radars" in st.session_state:
        for r in st.session_state.radars:
            center = Point(r["lon"], r["lat"])  
            circle_gdf = gpd.GeoDataFrame(geometry=[center], crs="EPSG:4326")
            circle_meters = circle_gdf.to_crs(epsg=3006) 
            circle_shape = circle_meters.buffer(r["size"] * 1000).to_crs(epsg=4326).geometry.iloc[0]

            # Add blackout geometry to our merge list
            if r["type"] == "Hit":
                # Hit: eliminate everything OUTSIDE the circle
                inverted_mask = game_board_shape.difference(circle_shape)     
                shapes_to_merge.append(inverted_mask)
            elif r["type"] == "Miss":
                # Miss: eliminate the circle itself
                shapes_to_merge.append(circle_shape)

            # Plot marker
            folium.Marker(
                location=[r["lat"], r["lon"]], 
                popup=f"Radar  #{r['counter']}",
                icon=folium.Icon(color="green", icon="crosshairs", prefix="fa")
            ).add_to(radar_list)
            radar_list.add_to(m)

    # PROCESS THERMOMETERS
    if "thermometer" in st.session_state:
        for r in st.session_state.thermometer:
            start_point = Point(r["start_lon"], r["start_lat"])  
            end_point = Point(r["end_lon"], r["end_lat"])  
            result = r["type"]
            counter = r["name"]

            # Convert to meters
            points_gdf = gpd.GeoDataFrame(geometry=[start_point, end_point], crs="EPSG:4326")
            points_meters = points_gdf.to_crs(epsg=3006)
            
            start = points_meters.geometry.iloc[0]
            end = points_meters.geometry.iloc[1]

            Mx, My = (start.x + end.x) / 2, (start.y + end.y) / 2
            M = Point(Mx, My)

            if result == "Hotter":
                dx, dy = start.x - end.x, start.y - end.y
            else:
                dx, dy = end.x - start.x, end.y - start.y
                
            length = np.hypot(dx, dy)
            if length == 0: 
                continue
            
            DIST = 25000 
            far_x, far_y = Mx + (dx / length) * DIST, My + (dy / length) * DIST
            far_point = Point(far_x, far_y)

            # Generate half of the colored rectangle
            center_line = LineString([M, far_point])
            eliminated_poly = center_line.buffer(DIST, cap_style=2)
            poly_gdf = gpd.GeoDataFrame(geometry=[eliminated_poly], crs="EPSG:3006")
            raw_eliminated_area = poly_gdf.to_crs(epsg=4326).geometry.iloc[0]

            # Add it to our merge list!
            shapes_to_merge.append(raw_eliminated_area)
            
            # Plot the markers
            folium.Marker(
                location=[r["start_lat"], r["start_lon"]], popup=f"Thermometer Start #{counter}",
                icon=folium.Icon(color="green", icon="temperature-empty", prefix="fa")
            ).add_to(thermometer_list)

            folium.Marker(
                location=[r["end_lat"], r["end_lon"]], popup=f"Thermometer End #{counter}",
                icon=folium.Icon(color="red", icon="temperature-full", prefix="fa")
            ).add_to(thermometer_list)        
            thermometer_list.add_to(m)

    # PROCESS Matching
    if "matching" in st.session_state:
        for m_tool in st.session_state.matching:
            name = m_tool["poi_name"]
            poi_gdf = get_poi_data(m_tool["category"])

            # Use voronoi diagram for POIs
            if m_tool["category"] != "Municipality" and m_tool["category"] != "District":
                vor_gdf = voronoi(poi_gdf)
                joined_vor = gpd.sjoin(
                    vor_gdf, 
                    poi_gdf[['label', 'geometry']], 
                    how='left', 
                    predicate='contains'
                )
                
                #Find polygon for the matching question
                target_col = 'label_right' if 'label_right' in joined_vor.columns else 'label'
                target_row = joined_vor[
                            (joined_vor[target_col] == m_tool["poi_name"]) & 
                            (joined_vor.geometry.type.isin(['Polygon', 'MultiPolygon']))
                            ]
                if not target_row.empty:
                    target_poly = target_row.geometry.iloc[0]

                #Add icons for each matching question that is based on POIs
                original_poi = poi_gdf[poi_gdf['label'] == m_tool["poi_name"]]
                if not original_poi.empty:
                    poi_point = original_poi.geometry.iloc[0] # Grab the original Point shape
                    
                    folium.Marker(
                        location=[poi_point.y, poi_point.x], 
                        popup=f"Matching: {m_tool['category']} - {m_tool['poi_name']} #{m_tool['counter']}",
                        icon=folium.Icon(color="purple", icon="question-circle", prefix="fa")
                    ).add_to(matching_list)
                matching_list.add_to(m)
                
            #Directly extract geometry for district/municipality
            else:
                #Find polygon for the matching question
                target_row = poi_gdf[poi_gdf['name'] == m_tool["poi_name"]]
                if not target_row.empty:
                    target_poly = target_row.geometry.iloc[0]
                    #Compute center point
                    center = target_poly.centroid
                    folium.Marker(
                            location=[center.y,center.x], 
                            popup=f"Matching: {m_tool['category']} - {m_tool['poi_name']} #{m_tool['counter']}",
                            icon=folium.Icon(color="purple", icon="question-circle", prefix="fa")
                        ).add_to(matching_list)
                    matching_list.add_to(m)

            
            # Color the map based on answer
            if m_tool["type"] == "Same":
                inverted_mask = game_board_shape.difference(target_poly)
                shapes_to_merge.append(inverted_mask)
            else:
                shapes_to_merge.append(target_poly)

    # PROCESS Measuring
    if "measure" in st.session_state: # Safety check
        for meas in st.session_state.measure:
            #Read inputs
            seeker = Point(meas["lon"], meas["lat"])
            poi_gdf = get_poi_data(meas["category"])

            #Compute seeker coordinate in meters
            seeker_gdf = gpd.GeoDataFrame(geometry=[seeker], crs="EPSG:4326")
            seeker_meter = seeker_gdf.to_crs(epsg=3006).geometry.iloc[0]
            poi_meters_gdf = poi_gdf.to_crs(epsg=3006)

            #Compute distance between seeker and closest POI
            distance = poi_meters_gdf.distance(seeker_meter)
            min_distance = distance.min()

            #All individual areas within the minimum distance of each POI
            all_circles = poi_meters_gdf.buffer(min_distance)
            closer_zones = all_circles.unary_union
            closer_zone_shape = gpd.GeoSeries([closer_zones], crs="EPSG:3006").to_crs(epsg=4326).geometry.iloc[0]

            # Compute the area to plot
            if meas["type"] == "Closer":
                inverted_mask = game_board_shape.difference(closer_zone_shape)
                shapes_to_merge.append(inverted_mask)
            else:
                shapes_to_merge.append(closer_zone_shape)

            #Add icons for each measuring questions
            folium.Marker(
                location=[meas["lat"], meas["lon"]], 
                popup=f"Measuring: {meas['category']} #{meas['counter']}",
                icon=folium.Icon(color="lightred", icon="ruler", prefix="fa")
            ).add_to(measuring_list)
            measuring_list.add_to(m)

    # Merge all shapes in shapes to merge array
    if shapes_to_merge:
        
        master_mask = unary_union(shapes_to_merge)
        
        # Clip the final blob to the game board boundary
        clean_master_mask = master_mask.intersection(game_board_shape)

        # Draw the single, continuous shape
        folium.GeoJson(
            clean_master_mask,
            name="Eliminated Area",
            style_function=lambda x: {
                'fillColor': '#3388ff',
                'color': '#3388ff',       
                'weight': 3,
                'fillOpacity': 0.4 
            },
        ).add_to(m)
