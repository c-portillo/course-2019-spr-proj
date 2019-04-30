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
import random
import pandas as pd
import branca.colormap as cm

def map(wards):
    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

    url = "https://opendata.arcgis.com/datasets/398ee443f4ac49e9a0b7facf80afc20f_8.geojson"
    response = urllib.request.urlopen(url).read().decode("utf-8")
    data = json.loads(response)

    default = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21"]
    wards_to_visit = ["01"]

    latinx_data = repo['carlosp_jpva_tkay_yllescas.sampling'].find()
    max = 0
    min = 1
    for x in latinx_data:
        for ward in default:
            for feature in data['features']:
                if int(feature['properties']['WARD']) == int(ward):
                    feature['properties']['prop'] = x['W' + ward]['H_Prop']
                if x['W' + ward]['H_Prop'] > max:
                    max = feature['properties']['prop']
                if x['W' + ward]['H_Prop'] < min:
                    min = feature['properties']['prop']

    # proportion colormap
    colormap = cm.linear.Paired_04.scale(min, max)
    colormap.caption = "Latinx Percentage"

    m = folium.Map(location=[42.3055, -71.0589], zoom_start=12)

    visit = {"type":"FeatureCollection","features":[]}
    map = {"type":"FeatureCollection","features":[]}
    if wards_to_visit == []:
        wards_to_visit = default

    for feature in data['features']:
        for ward in default:
            if int(feature["properties"]["WARD"]) == int(ward):
                for w in wards_to_visit:
                    map["features"].append(feature)
                    if ward == w:
                        visit["features"].append(feature)

    #def color(d):
    #    if d['WARD'] not in ward_to_visit:
    #        return 
    #    else:
    #        retucolormap(d['prop'])
    #    return colormap

    folium.GeoJson(visit,
                   name='Wards to Visit',
                   style_function=lambda x: {"weight":2,
                                             'color':'black',
                                             'fillColor': 'red',
                                             'fillOpacity':1},
                   highlight_function=lambda x: {'weight':3,
                                                 'color':'red'},
                   smooth_factor=2.0,
                   tooltip=folium.features.GeoJsonTooltip(fields=['WARD', 'prop'],
                                                          aliases=['Ward', 'Latinx Proportion'],
                                                          sticky=True,
                                                          labels=True),
                   show=False
                  ).add_to(m)

    folium.GeoJson(map,
                   name='City of Boston Wards',
                   style_function=lambda x: {"weight":2,
                                             'color':'black',
                                             'fillColor': colormap(x['properties']['prop']),
                                             'fillOpacity':0.7},
                   highlight_function=lambda x: {'weight':3,
                                                 'color':'red'},
                   smooth_factor=2.0,
                   tooltip=folium.features.GeoJsonTooltip(fields=['WARD', 'prop'],
                                                          aliases=['Ward', 'Latinx Proportion'],
                                                          sticky=True,
                                                          labels=True),
                  ).add_to(m)

    colormap.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    m.save('map.html')