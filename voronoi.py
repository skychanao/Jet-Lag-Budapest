import folium
from folium import plugins
from folium.plugins import Draw
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely import LineString
from shapely.geometry import Polygon
from shapely.ops import voronoi_diagram
from shapely.geometry import MultiPoint

from config import SCRIPT_FOLDER
from utils import clean_geometry, filter_close_stations



def main():

    global script_folder
    script_folder = Path(__file__).parent

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


    #Base Map features
    municipalities(m)
    districts(m)
    # coastline(m)
    # playableArea(m)

    train(m)
    M_lines(m)
    T_lines(m)
    stations(m)

    reachable(m)
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

    #Add location request
    folium.plugins.LocateControl(auto_start=False).add_to(m)

    #Add draw
    Draw(export=False).add_to(m)

    folium.LayerControl().add_to(m)




    #map generation
    print("sucessfully generated map.")
    file_name = Path(__file__).parent / "Budapest.html"
    m.save(file_name)

# =============================
# BASE MAP FEATURES
# =============================

def reachable(m):
    game_area = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "reachable.geojson"))
    folium.GeoJson(
        game_area,
        name = "Playable area",
            style_function=lambda feature: {
                'color':"#3ae868",
                'opacity': 0.8
        },
        show = False,
        control=True
    ).add_to(m)

def municipalities(m):
    raw_municialities = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "admin1.geojson"))
    municipalities = clean_geometry(raw_municialities[['name', 'geometry']])
    municipalities = municipalities[municipalities.geometry.type.isin(['Polygon', 'MultiPolygon'])]

    global game_area
    game_area = gpd.GeoDataFrame(municipalities, crs="EPSG:4326")

    # Convert any Timestamp columns to strings (or drop them)
    for col in game_area.columns:
        if pd.api.types.is_datetime64_any_dtype(game_area[col]):
            game_area[col] = game_area[col].astype(str)

    #Create a mask, which plots world_borer - game_area,
    minx, miny, maxx, maxy = game_area.total_bounds
    pad = 10.0 # 10 degree padding is enough to cover the visible map when zoomed out
    world_border = [
        [minx - pad, miny - pad],
        [minx - pad, maxy + pad],
        [maxx + pad, maxy + pad],
        [maxx + pad, miny - pad],
        [minx - pad, miny - pad]
    ]
    world_poly = Polygon(world_border)
    world_gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[world_poly])
    
    # Dissolve game area into a single polygon to prevent masking glitches
    game_area_dissolved = game_area.assign(dummy=1).dissolve(by='dummy')
    mask_gdf = gpd.overlay(world_gdf, game_area_dissolved, how='difference')
    
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

def districts(m):
    districts = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "admin2.geojson"))

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
    raw_coastlines = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "coastlines.geojson"))

    #merge all coastline polygons and lines into one shape
    coastlines = gpd.clip(clean_geometry(raw_coastlines),game_area)
    folium.GeoJson(
        coastlines,
        name = "Coastline",
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#897CFF',
            'weight': 2
        },
        show = False
    ).add_to(m)

def playableArea(m):
    raw_reachable = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "35min.geojson"))

    reachable = gpd.clip(clean_geometry(raw_reachable),game_area)
    folium.GeoJson(
        reachable,
        name = "Playable Area",
        style_function=lambda x: {
            'fillColor': "#1EA400",
            'color': "#1EA400",
            'weight': 2
        },
        show = False
    ).add_to(m)

def train(m):
    train_lines = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "train.geojson"))
    folium.GeoJson(
        train_lines,
        name = "Train lines",
            style_function=lambda feature: {
                'color':"#6E6E6E",
                'opacity': 0.8,
                'dashArray': '10, 10'
        },
        show = False,
        control=True
    ).add_to(m)

def M_lines(m):
    metro_lines = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "metro-lines.geojson"))
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
    if 'colour' not in metro_lines.columns:
        metro_lines['colour'] = metro_lines.apply(map_metro_color, axis=1)

    folium.GeoJson(
        metro_lines,
        name = "Metro Lines",
            style_function=lambda feature: {
                'color': feature['properties'].get('colour', '#555555'),
        },
        tooltip=folium.GeoJsonTooltip(
            fields = ['ref'] if 'ref' in metro_lines.columns else [],
            labels = False
        ) if 'ref' in metro_lines.columns else None,
        show = True
    ).add_to(m)

def T_lines(m):
    raw_TLines = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "tram-lines.geojson"))
    folium.GeoJson(
        raw_TLines,
        name = "Tram Lines",
        style_function=lambda feature: {
            'color': '#e37c07',
            
        },
        show = True
    ).add_to(m)

def stations(m):
    #read data from GeoJson
    raw_Tstations = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "tram-stations.geojson"))
    raw_Mstations = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "metro-stations.geojson"))


    #extract name and geometry of unique tram stations 
    tram_stations = raw_Tstations[['name','geometry']].drop_duplicates(subset=['name'])
    #only select stations within the game area
    tram_stations = gpd.clip(tram_stations, game_area)
    #select starting tram stations of the game
    start_T = tram_stations[tram_stations['name'] == "Deák Ferenc tér"][['name','geometry']]
    #remove starting tram stations from other tram stations
    tram_stations = tram_stations[~tram_stations['name'].isin(start_T['name'])]

    # Filter out tram stations that are too close to each other (less than 500m) to reduce overlap
    tram_stations = filter_close_stations(tram_stations, min_dist_m=500)

    #extract name and geometry of unique metro stations 
    metro_stations = raw_Mstations[['name','geometry']].drop_duplicates(subset=['name'])
    #only select stations within the game area
    metro_stations = gpd.clip(metro_stations, game_area)
    #select starting metro stations of the game
    start_M = metro_stations[metro_stations['name'] == "Deák Ferenc tér"][['name','geometry']]
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

# =============================
# PLOT POIS
# =============================

def parks(m):
    raw_parks = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "parks.geojson"))
    raw_parks['label'] = raw_parks['label'].str.split('-').str[0].str.strip()

    parks = Voronoi(raw_parks)

    folium.GeoJson(
        parks,
        name = "Parks",
        marker=folium.Marker(
            icon=folium.Icon(
                color='green', 
                icon='tree', 
                prefix='fa')
        ),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#270F7D',
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def amusementParks(m):
    raw_amusementParks = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "Amusement-Park.geojson"))
    raw_amusementParks['label'] = raw_amusementParks['label'].str.split('-').str[0].str.strip()
 
    amusementParks = Voronoi(raw_amusementParks)

    folium.GeoJson(
        amusementParks,
        name = "Amusement Parks",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='pink',
                icon='ticket', 
                prefix='fa')
        ),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#270F7D',
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def zoo(m):
    raw_zoos = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "zoos.geojson"))
    
    raw_zoos['label'] = raw_zoos['label'].str.split(' - ').str[0].str.strip()
    zoos = Voronoi(raw_zoos)

    folium.GeoJson(
        zoos,
        name = "Zoos",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='darkred',
                icon='paw', 
                prefix='fa')
        ),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#270F7D',
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def aquarium(m):
    raw_aquariums = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "aquariums.geojson"))
    raw_aquariums['label'] = raw_aquariums['label'].str.split(' - ').str[0].str.strip()

    aquariums = Voronoi(raw_aquariums)

    folium.GeoJson(
        aquariums,
        name = "Aquariums",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='lightblue',
                icon='fish', 
                prefix='fa')
        ),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#270F7D',
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def golf(m):
    raw_golfcourses = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "golf-courses.geojson"))
    raw_golfcourses['label'] = raw_golfcourses['label'].str.split(' - ').str[0].str.strip()
    
    golf_courses = Voronoi(raw_golfcourses)
    folium.GeoJson(
        golf_courses,
        name = "Golf Courses",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='darkgreen',
                icon='golf-ball', 
                prefix='fa')
        ),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#270F7D',
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def museum(m):
    raw_museums = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "museums.geojson"))
    raw_museums['label'] = raw_museums['label'].str.split(' - ').str[0].str.strip()

    museums = Voronoi(raw_museums)

    folium.GeoJson(
        museums,
        name = "Museums",
        marker=folium.Marker(
            icon=folium.Icon(
                color ='orange',
                icon='university', 
                prefix='fa')
        ),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#270F7D',
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def theaters(m):
    raw_theaters = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "movie-theaters.geojson"))
    raw_theaters['label'] = raw_theaters['label'].str.split(' - ').str[0].str.strip()
    theaters = Voronoi(raw_theaters)

    folium.GeoJson(
        theaters,
        name = "Movie Theaters",
        marker=folium.Marker(
            icon=folium.Icon(
            color='cadetblue',
            icon='film', 
            prefix='fa')
        ),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#270F7D',
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def hospitals(m):
    raw_hospitals = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "hospitals.geojson"))
    raw_hospitals['label'] = raw_hospitals['label'].str.split(' - ').str[0].str.strip()

    hospitals = Voronoi(raw_hospitals)

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
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#270F7D',
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def libraries(m):
    raw_libraries = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "libraries.geojson"))
    raw_libraries['label'] = raw_libraries['label'].str.split(' - ').str[0].str.strip()

    libraries = Voronoi(raw_libraries)

    folium.GeoJson(
        libraries,
        name = "Libraries",
        marker=folium.Marker(
            icon=folium.Icon(
                color='lightred', 
                icon='book', 
                prefix='fa')

        ),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': '#270F7D',
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def consulates(m):
    raw_consulates = clean_geometry(gpd.read_file(SCRIPT_FOLDER / "consulates.geojson"))
    raw_consulates['label'] = raw_consulates['label'].str.split(' - ').str[0].str.strip()

    consulates = Voronoi(raw_consulates)

    folium.GeoJson(
        consulates,
        name = "Consluates",
        marker=folium.Marker(
            icon=folium.Icon(
                color='darkpurple',
                icon='globe',
                prefix='fa')
        ),
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': "#270F7D",
            'weight': 3
        },
        popup=folium.GeoJsonPopup(
            fields = ['label'],
            labels=False
        ),
        show = False
    ).add_to(m)

def Voronoi(gdf):
    world_border = MultiPoint([(-90,-90), (90,-90),(-90,90),(90,90)]).envelope
    multipoint = MultiPoint(gdf.geometry.values)
    voronoi_collection = voronoi_diagram(multipoint, envelope=world_border)
    # Create a GeoDataFrame with the Voronoi polygons:
    voronoi_gdf = gpd.GeoDataFrame(geometry=list(voronoi_collection.geoms), crs='EPSG:4326').clip(game_area)
    return pd.concat([voronoi_gdf,gdf])

def clean_geometry(gdf):
    # 1. Drop data with no shape data
    gdf = gdf.dropna(subset=['geometry'])
    
    # 2. Keep only the standard shapes that Folium knows how to draw
    supported_shapes = ['Point', 'MultiPoint', 'LineString', 'MultiLineString', 'Polygon', 'MultiPolygon']
    gdf = gdf[gdf.geometry.type.isin(supported_shapes)]
    
    # ✅ THE FIX: Find any Timestamp/Datetime columns and convert them to simple strings
    for col in gdf.select_dtypes(include=['datetime64', 'datetimetz']).columns:
        gdf[col] = gdf[col].astype(str)
        
    return gdf


if __name__ == "__main__":
    main()


