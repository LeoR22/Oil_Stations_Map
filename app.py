"""
********************************************************************
* Author = https://github.com/LeoR22                          *
* Date = '10/02/2024'                                              *
* Description = Streamlit App - Oil Stations                       *
********************************************************************
"""


import streamlit as st
import pandas as pd
from PIL import Image
import time
import json
import random
from datetime import datetime
import datetime
import os
import numpy as np
import requests


from tqdm import tqdm
from cred_here_Template import *

import ast

# Tools

import folium
#NUEVO CODIGO
from utils import GetLatLon2, distance_estac, transform_df_map, marker_rest, calculate_route
import pydeck as pdk

##
from shapely.geometry import Polygon
import numpy as np
import geojson
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import Polygon
import shapely.wkt
from haversine import haversine, Unit
import random
import time
from pyproj import Geod

from shapely import wkt
from geopandas import datasets, GeoDataFrame, read_file, points_from_xy

from folium.plugins import MeasureControl
from folium.plugins import MarkerCluster

from utils import GetLatLon2,cal_dist,distance_estac,transform_df_map,marker_rest
from streamlit_folium import folium_static

image = Image.open('C:\\Users\\lrivera\\Downloads\\INTEGRACION\\CURSOS\\DATA ENGINNER\\PROYECTOS\\PROJEC-4\\oil_stations_files\\1_Fuel-prices.jpg')

st.sidebar.image(image , caption="Nearby Oil App",width = 256)
app_mode = st.sidebar.selectbox("Choose app mode", ["Run App","About Me"])
#st.sidebar.image(image, caption="Nearby Oil App", width=256)
#st.sidebar.header("App Modes")
#app_mode = st.sidebar.radio("Select Mode", ["Run App", "About Me"])


if app_mode == 'Run App':
     
    st.title('Nearby Oil Station App')
    st.markdown('App que busca las estaciones de gasolina cercanas a un punto de referencia.  ')

    df_map = pd.read_csv('C:\\Users\\lrivera\\Downloads\\INTEGRACION\\CURSOS\\DATA ENGINNER\\PROYECTOS\\PROJEC-4\\oil_stations_files\\DF_STATIONS.csv')
    cities =  list(df_map['Municipio'].unique())

    c1,c2,c3,c4,c5 = st.columns((1,6,6,6,1))

    choose_city =  c2.selectbox("Choose city", cities)

    central_location = c2.text_input('Central Location', 'CC Viva , Itagui')

    DEVELOPER_KEY = YOUR_API_KEY
    
    if len(central_location) != 0 :

        R = GetLatLon2(central_location,YOUR_API_KEY)
        geo_source = R[1],R[2]

        unit = 'Km'
        rad = c4.slider('Radius',1,3,1)

        df_city = df_map[df_map['Municipio']==choose_city]
        df_city.reset_index(inplace = True)
        df_city.drop(columns = 'index',inplace = True)

        df_city =  transform_df_map(df_city)

        results = distance_estac(geo_source,df_city,rad,unit)
        results = results.reset_index()
        results = results.drop(columns = 'index')
        products =  list(results['Producto'].unique())

        gdf_stores_results = GeoDataFrame(results,
                                            geometry=points_from_xy(results.LNG,results.LAT))


        choose_products =  c3.selectbox("Choose Oil", products)
        def handle_click(latitude, longitude, central_location_coords):
            st.write(f"Clicked Location: ({latitude}, {longitude})")
            route = calculate_route(central_location_coords, (latitude, longitude))
            st.write("Route:", route)
            if route:
                # Draw the route on the map
                st.pydeck_chart(pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=pdk.ViewState(
                        latitude=central_location_coords[0],  # Usamos central_location_coords aquí
                        longitude=central_location_coords[1],  # Usamos central_location_coords aquí
                        zoom=15,
                        pitch=0,
                    ),
                    layers=[
                        pdk.Layer(
                            "PathLayer",
                            data=route,
                            get_path="coordinates",
                            width_scale=20,
                            width_min_pixels=3,
                            get_color=[255, 0, 0],
                            pickable=True,
                            auto_highlight=True,
                        ),
                    ],
                ))
            else:
                st.error("Error calculating route. Please try again.")



        if c3.button('SHOW MAP'):
            central_location_coords = (geo_source[0], geo_source[1])
            clicked_location = st.map.click_event if hasattr(st.map, "click_event") else None

            if clicked_location:
                latitude, longitude = clicked_location["lat"], clicked_location["lon"]
                handle_click(latitude, longitude, central_location_coords)

            gdf_stores_results2 = gdf_stores_results[gdf_stores_results['Producto']==choose_products]
            gdf_stores_results2 = gdf_stores_results2.reset_index()
            gdf_stores_results2 = gdf_stores_results2.drop(columns = 'index')
            icono = "usd"

            m = folium.Map([geo_source[0],geo_source[1]], zoom_start=15)

            # Circle
            folium.Circle(
            radius=int(rad)*1000,
            location=[geo_source[0],geo_source[1]],
            color='green',
            fill='red').add_to(m)

            # Centroid
            folium.Marker(location=[geo_source[0],geo_source[1]],
                                icon=folium.Icon(color='black', icon_color='white',
                                icon="home", prefix='glyphicon')
                                ,popup = "<b>CENTROID</b>").add_to(m)

            marker_rest(gdf_stores_results2,m,unit,choose_products,icono)

            # call to render Folium map in Streamlit
            folium_static(m)

            clicked_location = st.map.click_event if hasattr(st.map, "click_event") else None

            if clicked_location:
                latitude, longitude = clicked_location["lat"], clicked_location["lon"]
                handle_click(latitude, longitude)
            




elif app_mode == "About Me":
    st.title('Nearby Oil Station App')
    st.success("Feel free to contacting me here 👇 ")

    col1,col2,col3,col4 = st.columns((2,1,2,1))
    col1.markdown('* [**Medium**](https://leandroriveradev.medium.com/)')
    col1.markdown('* [**LinkedIn**](https://www.linkedin.com/in/leandrorivera/)')
    #col1.markdown('* [**Website**](https://portafolio-ab.herokuapp.com/)')
    col1.markdown('* [**GitHub**](https://github.com/LeoR22)')
    #col1.markdown('* [**Twitter**](https://twitter.com/datexland)')
    image2 = Image.open('profile.jpg')
    col3.image(image2,width=230)