import dml
from pymongo import MongoClient
import bson.code
import requests 
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime
import prov.model
import uuid
from zipfile import ZipFile
import urllib.request
import shapefile
from pyproj import Proj, transform
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
import numpy as np
import shutil
import os

# Produces a dataset that tells how many public libraries are located within the geographical bounds of each Massachusetts school district. (Note that the mapreduce step of my original code for this algorithm was producing very strange results, so I modified the functions to compensate for it as much as I could, but a lot of investigation would still be needed to actually fix the problem.)

class sort_libraries(dml.Algorithm):
    contributor = 'emilymo'
    reads = ['d.libs']
    writes = ['d.alldistr', 'd.distr', 'd.distr2', 'd.libdistr', 'd.libperdistr']

    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        
        client = dml.pymongo.MongoClient() # TO FIX: AUTH??
        d = client.d
        
        # download to temp directory that will get deleted later
        if not os.path.exists('temp'):
            os.makedirs('temp')
        z = urllib.request.urlretrieve('http://download.massgis.digital.mass.gov/shapefiles/state/schooldistricts.zip', 'temp/schooldistricts.zip')
        ZipFile('temp/schooldistricts.zip', 'r').extractall('temp/')
        shp = shapefile.Reader('temp/SCHOOLDISTRICTS_POLY.shp')
        fields = shp.fields[1:]
        fieldnms = [field[0] for field in fields]
        distr = []
        for r in shp.shapeRecords():
            atr = dict(zip(fieldnms, r.record))
            geom = r.shape.__geo_interface__
            distr.append(dict(type="Feature", \
                geometry=geom, properties=atr))
        d['alldistr'].insert_many(distr)
        
        # subset alldistr to just regional / local districts
        mapper = bson.code.Code("""
            function() {
                if (this['properties']['MADISTTYPE'] == 'Local School' || this['properties']['MADISTTYPE'] == 'Regional Academic') {
                    emit(this['_id'], {'geometry': this['geometry'], 'district':this['properties']['DISTRICT']})
                }  
            }
            """)
        reducer = bson.code.Code("""
            function(k, vs) {
                
            }
            """)
        d['alldistr'].map_reduce(mapper, reducer, 'distr')
        
        inproj = Proj(init = 'epsg:26986') 
        outproj = Proj(init = 'epsg:4326')
        for dis in d['distr'].find():
            piececount = 0
            for piece in dis['value']['geometry']['coordinates']:
                piececount += 1
                newcoords = []
                oldcoords = piece  
                for tup in oldcoords:
                    x1 = tup[0]
                    y1 = tup[1]
                    x2, y2 = transform(inproj, outproj, x1, y1)
                    newcoords.append((x2, y2))
                d['distr2'].insert_one({'geometry': newcoords, 'district':dis['value']['district'], 'piece':piececount})
                
                
                
        # There are several issues with this part, which I have not found the solution to yet.
        # One was the sum of 1s and 0s in the mapreduce was not adding up properly, because the first value emitted was always undefined. I have not fixed or found the root of the problem but have eliminated the first value in calculation of the sum, so that at some sum can at least be computed rather than showing NaN. 
        # Another problem was that some of the lists of coordinate pairs included in the school districts shapefile failed to render. I have made a list of those pairs, libsort_failed, for reference if I were to try to fix this problem at a later time. 
        # The other problem was that the sums are clearly wrong. There are districts in this list that definitely have libraries in them in real life, but the algorithm is saying that none of the library points are within the polygons for those districts. This may be an issue with the geographic datasets that needs to be investigated more.
        libsort_failed = []
        for dis in d['distr2'].find():
            try:
                for lb in d['libs'].find():
            
                    ld = dis['district']
                    ln = lb['Library']
                    
                    arr = np.array(dis['geometry'])
                    poly = Polygon(arr)
                    lbcoords_rev = tuple(lb['Location'])
                    lbcoords = (lbcoords_rev[1], lbcoords_rev[0])
                    lc = Point(lbcoords)
                    
                    b = int(poly.contains(lc)) # gives a 0 or 1
                    d['libdistr'].insert_one({'distr':ld, 'name':ln, 'within':b})
                   
        
            except:
                libsort_failed.append(dis) # ones with coordinate pairs that didn't properly form polygons
        len([r for r in d['libdistr'].find()])
        [r for r in d['libdistr'].find()][77]
        
        map2 = bson.code.Code("""
            function () {
                emit(this['distr'], {'name':this['name'], 'ins':this['within']})
        
            }
            """)
        red2 = bson.code.Code("""
            function (k, vs) {
                var numlibs = 0;
        
                vs.splice(1).forEach(function(val) {
                        numlibs += val['ins'] 
                            
                });
                return {'numlibs':numlibs};
            }
            """)
        d['libdistr'].map_reduce(map2, red2, 'libperdistr') 


        # delete temp folder
        shutil.rmtree('temp')
        
        d.logout()
        endTime = datetime.datetime.now()
        
        return {"start":startTime, "end":endTime}        
        
    @staticmethod  
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/') 
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') 
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        
        doc.add_namespace('gis', 'http://download.massgis.digital.mass.gov/shapefiles/state/')
        
        this_script = doc.agent('alg:emilymo#sort_libraries', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent']})
        sort_libraries = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        distr_site = doc.entity('gis:schooldistricts.zip', {prov.model.PROV_LABEL:'Massachusetts School Districts Zip', prov.model.PROV_TYPE:'ont:DataResource'})
        libs = doc.entity('dat:emilymo#libs', {prov.model.PROV_LABEL:'Geocoded Massachusetts Libraries', prov.model.PROV_TYPE:'ont:DataSet'})
        alldistr = doc.entity('dat:emilymo#alldistr', {prov.model.PROV_LABEL:'All Massachusetts School Districts', prov.model.PROV_TYPE:'ont:DataSet'})
        distr = doc.entity('dat:emilymo#distr', {prov.model.PROV_LABEL:'Massachusetts Regional / Local School Districts', prov.model.PROV_TYPE:'ont:DataSet'})
        distr2 = doc.entity('dat:emilymo#distr2', {prov.model.PROV_LABEL:'Massachusetts Regional / Local School Districts with Latitude / Longitude Coordinates', prov.model.PROV_TYPE:'ont:DataSet'})
        libdistr = doc.entity('dat:emilymo#libdistr', {prov.model.PROV_LABEL:'Libraries In / Not In Each District', prov.model.PROV_TYPE:'ont:DataSet'})
        libperdistr = doc.entity('dat:emilymo#libperdistr', {prov.model.PROV_LABEL:'Number of Libraries Within Boundaries of Each Massachusetts Regional / Local District', prov.model.PROV_TYPE:'ont:DataSet'})
        
        doc.wasAssociatedWith(sort_libraries, this_script)
        doc.used(sort_libraries, distr_site, other_attributes={prov.model.PROV_TYPE:'ont:Retrieval'})
        doc.used(sort_libraries, libs, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.used(sort_libraries, alldistr, other_attributes={prov.model.PROV_TYPE:'ont:Query'})
        doc.used(sort_libraries, distr, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.used(sort_libraries, distr2, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.used(sort_libraries, libdistr, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasDerivedFrom(alldistr, distr_site)
        doc.wasDerivedFrom(distr, alldistr)
        doc.wasDerivedFrom(distr2, distr)
        doc.wasDerivedFrom(libdistr, distr2)
        doc.wasDerivedFrom(libdistr, libs)
        doc.wasDerivedFrom(libperdistr, libdistr)
        doc.wasAttributedTo(alldistr, this_script)
        doc.wasAttributedTo(distr, this_script)
        doc.wasAttributedTo(distr2, this_script)
        doc.wasAttributedTo(libdistr, this_script)
        doc.wasAttributedTo(libperdistr, this_script)
        doc.wasGeneratedBy(alldistr, sort_libraries)
        doc.wasGeneratedBy(distr, sort_libraries)
        doc.wasGeneratedBy(distr2, sort_libraries)
        doc.wasGeneratedBy(libdistr, sort_libraries)
        doc.wasGeneratedBy(libperdistr, sort_libraries)
        
        return doc
        
        
        
        