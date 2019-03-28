# shape file found from https://docs.digital.mass.gov/dataset/massgis-data-massachusetts-department-transportation-massdot-roads

import shapefile
import pandas as pd

file_name = 'MassDOT_Roads_SHP/EOTROADS_ARC.shp'

# read the shapefile
reader = shapefile.Reader(file_name)
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buffer = []
for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature", geometry=geom, properties=atr))

# write the GeoJSON file
from json import dumps

geojson = open("major_roads.json", "w")
geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
geojson.close()


