
"""
********************************************************************
* Author = https://github.com/LeoR22                          *
* Date = '10/02/2024'                                              *
* Description = Streamlit App - Oil Stations                       *
********************************************************************
"""

import random
import pandas as pd
from tqdm import tqdm
from cred_here_Template import *
import json
import requests

import ast

# Tools

import folium
from shapely.geometry import Polygon
import numpy as np
import geojson
import folium
import geopandas as gpd
from shapely.geometry import Polygon
import shapely.wkt
from haversine import haversine, Unit
import random
import time
from pyproj import Geod
#from polygon_geohasher.polygon_geohasher import geohash_to_polygon

from shapely import wkt
from geopandas import datasets, GeoDataFrame, read_file, points_from_xy
from geopandas.tools import overlay
from geopandas.tools import sjoin

from folium.plugins import MeasureControl
from folium.plugins import MarkerCluster

import time




def GetLatLon2(Address,YOUR_API_KEY):

    url2_geocode  = f'https://geocode.search.hereapi.com/v1/geocode?q={Address}&apiKey='+YOUR_API_KEY

    try:
        response = requests.get(url2_geocode).json()
        CleanAddress = response['items'][0]['title'].upper()
        LAT = response['items'][0]['position']['lat']
        LON = response['items'][0]['position']['lng']
        results = [CleanAddress,round(LAT,7),round(LON,7)]
    except:
        results = ['NotFound','NA','NA']
    return results

def GetLatLon2_google(Address,YOUR_API_KEY):

    api_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={Address}&key={YOUR_API_KEY}'
    try:
        j = requests.get(api_url).json()
        CleanAddress = str(j['results'][0]['formatted_address']).upper()
        LAT = j['results'][0]['geometry']['location']['lat']
        LON = j['results'][0]['geometry']['location']['lng']
        results = [CleanAddress,round(LAT,7),round(LON,7)]
    except:
        results = ['NotFound','NA','NA']
    return results,j

# Calc Distance
def cal_dist(geo_source,point2,unit):


    if unit == 'Km':
        distance = haversine(geo_source, point2,Unit.KILOMETERS)
    elif unit == 'm':
        distance = haversine(geo_source, point2,Unit.METERS)
    elif unit == 'miles':
        distance = haversine(geo_source, point2,Unit.MILES)

    return distance

# Locations within radius
def distance_estac(geo_source,df,radio,unit):


    distancia = []
    source = []


    for i in tqdm(range(len(df)),colour = 'green'):
        distancia.append(cal_dist(geo_source,df['POINT'][i],unit))
        source.append(geo_source)

    new_df = df.copy()
    new_df['SOURCE'] = source
    new_df['DISTANCE'] = distancia
    new_df = new_df[new_df['DISTANCE']<=radio]
    new_df = new_df.reset_index()
    new_df = new_df.drop(columns ='index')
    return new_df.sort_values(by='DISTANCE',ascending=True)

# Create centroid pairs
def transform_df_map(df_temp):



    coordenadas = []

    for i in range(len(df_temp)):

        try :

            coord = float(df_temp['LAT'][i]),float(df_temp['LNG'][i])
            coordenadas.append(coord)
        except :
            coordenadas.append('EMPTY')
    df_temp['POINT'] = coordenadas
    df_temp = df_temp[df_temp['POINT']!='EMPTY']
    df_temp = df_temp.reset_index()
    df_temp = df_temp.drop(columns = 'index')
    new_df = df_temp.copy()

    return new_df

def marker_rest(df,mapa,unit,oil,icono):

    df = df[df['Producto']==oil]
    df = df.reset_index()
    df = df.drop(columns = 'index')

    for i in range(len(df)):

        if df['Precio'][i]==df['Precio'].min():

            html =  f"""<b>MARCA:</b> {df.Bandera[i]} <br>
                    <b>NAME:</b> {df.Nombre_comercial[i]} <br>
                    <b>PRODUCTO:</b> {df.Producto[i]} <br>
                    <b>PRECIO:</b> {df.Precio[i]} <br>
                    <b>DISTANCE:</b> {round(df.DISTANCE[i],2)}<br>
                    <b>DIRECCION:</b> {df.Direccion[i]}<br>
                    <b>UNIT:</b> {unit}<br>
                    <button onclick="traceRoute({df.LAT[i]}, {df.LNG[i]})">Trace Route</button>"""
            #iframe = folium.IFrame(html,figsize=(6, 3))
            #popup = folium.Popup(iframe)
            iframe = folium.IFrame(html, width=300, height=200)
            popup = folium.Popup(iframe, max_width=300)




            folium.Marker(location=[float(df['LAT'][i]),float(df['LNG'][i])],
                               icon=folium.Icon(color='darkgreen', icon_color='white',
                               icon=icono, prefix='glyphicon'),
                               popup = popup).add_to(mapa)

        elif df['Precio'][i]==df['Precio'].max():

            html =  f"""<b>MARCA:</b> {df.Bandera[i]} <br>
                    <b>NAME:</b> {df.Nombre_comercial[i]} <br>
                    <b>PRODUCTO:</b> {df.Producto[i]} <br>
                    <b>PRECIO:</b> {df.Precio[i]} <br>
                    <b>DISTANCE:</b> {round(df.DISTANCE[i],2)}<br>
                    <b>DIRECCION:</b> {df.Direccion[i]}<br>
                    <b>UNIT:</b> {unit}<br>
                    <button onclick="traceRoute({df.LAT[i]}, {df.LNG[i]})">Trace Route</button>"""
            iframe = folium.IFrame(html,figsize=(6, 3))
            popup = folium.Popup(iframe)



            folium.Marker(location=[float(df['LAT'][i]),float(df['LNG'][i])],
                               icon=folium.Icon(color='darkred', icon_color='white',
                               icon=icono, prefix='glyphicon'),
                               popup =popup).add_to(mapa)
        else :
            html =  f"""<b>MARCA:</b> {df.Bandera[i]} <br>
                    <b>NAME:</b> {df.Nombre_comercial[i]} <br>
                    <b>PRODUCTO:</b> {df.Producto[i]} <br>
                    <b>PRECIO:</b> {df.Precio[i]} <br>
                    <b>DISTANCE:</b> {round(df.DISTANCE[i],2)}<br>
                    <b>DIRECCION:</b> {df.Direccion[i]}<br>
                    <b>UNIT:</b> {unit}<br>
                    <button onclick="traceRoute({df.LAT[i]}, {df.LNG[i]})">Trace Route</button>"""
            iframe = folium.IFrame(html,figsize=(6, 3))
            popup = folium.Popup(iframe)



            folium.Marker(location=[float(df['LAT'][i]),float(df['LNG'][i])],
                               icon=folium.Icon(color='orange', icon_color='white',
                               icon=icono, prefix='glyphicon'),
                               popup =popup).add_to(mapa) #<font-awesome-icon icon="fa-regular fa-gas-pump" />

    return

def calculate_route(start_coords, end_coords):
    # Replace YOUR_ROUTING_API_KEY with your actual routing API key
    routing_api_key = "YOUR_API_KEY"
    
    # Construct the request URL
    #url = f'https://maps.googleapis.com/maps/api/geocode/json?address={start_coords[0]},{start_coords[1]}&end={end_coords[0]},{end_coords[1]}&key={routing_api_key}'
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={start_coords[0]},{start_coords[1]}&destination={end_coords[0]},{end_coords[1]}&key={routing_api_key}'
    
    
    try:
        # Make a GET request to the routing API
        response = requests.get(url)
        data = response.json()
        
        
        #route_coordinates = data["route"]["coordinates"]
        route_coordinates = []
        for step in data['routes'][0]['legs'][0]['steps']:
                start_location = step['start_location']
                end_location = step['end_location']
                route_coordinates.append([start_location['lat'], start_location['lng']])
                route_coordinates.append([end_location['lat'], end_location['lng']])
        
        return route_coordinates

    
    except Exception as e:
        print(f"Error calculating route: {e}")
        return []

    