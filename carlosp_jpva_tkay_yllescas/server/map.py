import urllib
import json
import dml
import prov.model
import datetime
import uuid
import sys
import math
from urllib import request, parse
import folium
import os
import csv
import googlemaps

wards_to_visit = ["01", "19"]
url = "http://bostonopendata-boston.opendata.arcgis.com/datasets/2bc185ec9b0b478d8c2f7e720d116863_0.geojson"
response = urllib.request.urlopen(url).read().decode("utf-8")

data = json.loads(response)

m = folium.Map(location=[42.3601, -71.0589], zoom_start=12)

vis = os.path.join('data', 'vis.json')


map = {"type":"FeatureCollection","features":[]}
for ward in wards_to_visit:
    for feature in data['features']:
        if (feature["properties"]["WARD_PRECINCT"][0:2] == ward):
            map["features"].append(feature)
    

folium.Choropleth(geo_data = map, data=None, columns=None, key_on=None, bins=6, fill_color='blue', nan_fill_color='black', fill_opacity=0.6, nan_fill_opacity=None, line_color='black', line_weight=1, line_opacity=1, name=None, legend_name='', overlay=True, control=True, show=True, topojson=None, smooth_factor=None, highlight=None).add_to(m)

m.save('map.html')