import dml
from pymongo import MongoClient
import bson.code
import requests 
from bs4 import BeautifulSoup as bs
import pandas as pd
import datetime
import prov.model
import uuid

# Gets list of public libraries in Massachusetts from public libraries site and geocodes location for each one based on Google Maps. 
# For some reason, Truro Public Library didn't have a location in Google Maps, so I had to manually look it up and add it.

class get_libraries(dml.Algorithm):
    contributor = 'emilymo'
    reads = []
    writes = ['d.libs']
    
    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        
        client = dml.pymongo.MongoClient() # TO FIX: AUTH??
        d = client.d
        
        site = 'https://publiclibraries.com/state/massachusetts/'
        pg = requests.get(site)
        sp = bs(pg.content, "lxml")
        tbl = sp.find('table')
        rows = tbl.find_all('tr')
        l = [] 
        for tr in rows: 
            td = tr.find_all('td')
            row = [tr.text for tr in td]
            l.append(row)
        colnames = [str(c.string) for c in sp.find_all('th')]
        lib = pd.DataFrame(l, columns=colnames) 
        libd = lib.to_dict('records')[1:] 
        d['libs1'].insert_many(libd)
        
        # get api from auth.json
        ## testing what's stored in auth object
            # pathToAuth = "/Users/emily/Documents/cs504/proj1/course-2019-spr-proj/auth.json" # this path is wrong, just for testing
            # auth = json.loads(open(pathToAuth).read())
            # auth['services']['googlemaps']['key']   
        ##
        import time
        libnames = [e['Library'] for e in libd]
        libraries = []
        failed = []
        base = 'https://maps.googleapis.com/maps/api/geocode/json?' 
        api = dml.auth['services']['googlemaps']['key']
        for n in libnames:
            address = n
            try:
                # print(address)
                url = base + "address=" + "+massachusetts" + address.replace(" ","+") + "&key=" + api
                r = requests.get(url)
                results = r.json()['results']
                location = results[0]['geometry']['location']
                # time.sleep(1)
                geo = location['lat'], location['lng']
            except:
                print('Failed:')
                print(failed.append(address))
                geo = "NA"
            libraries.append({'Library':n, 'Location':geo})
        # manual fixing of truro public library
        for l in libraries:
            if l['Library'] == "Truro Public Library":
                address = "7 Standish Way North Truro MA"
                url = base + "address=" + "+massachusetts" + address.replace(" ","+") + "&key=" + api
                r = requests.get(url)
                results = r.json()['results']
                location = results[0]['geometry']['location']
                geo = location['lat'], location['lng'] # lat, lon form
                l['Location'] = geo
                d['libs'].insert_many(libraries)
                
        d.logout()
        endTime = datetime.datetime.now()
        
        return {"start":startTime, "end":endTime}
        
        
        
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/') 
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') 
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        
        doc.add_namespace('lib', 'https://publiclibraries.com/state/')
        
        this_script = doc.agent('alg:emilymo#get_libraries', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent']})
        get_libraries = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        libsite = doc.entity('lib:massachusetts/', {prov.model.PROV_LABEL:'Massachusetts Library Table', prov.model.PROV_TYPE:'ont:DataResource'})
        libs1 = doc.entity('dat:emilymo#libs1', {prov.model.PROV_LABEL:'Massachusetts Libraries', prov.model.PROV_TYPE:'ont:DataSet'})
        libs = doc.entity('dat:emilymo#libs', {prov.model.PROV_LABEL:'Geocoded Massachusetts Libraries', prov.model.PROV_TYPE:'ont:DataSet'})
        
        doc.wasAttributedTo(libs1, this_script)
        doc.wasAttributedTo(libs, this_script)
        doc.wasGeneratedBy(libs1, get_libraries)
        doc.wasAssociatedWith(get_libraries, this_script)
        doc.used(get_libraries, libsite, other_attributes={prov.model.PROV_TYPE:'ont:Retrieval'})
        doc.used(get_libraries, libs1, other_attributes={prov.model.PROV_TYPE:'ont:Computation'})
        doc.wasDerivedFrom(libs, libs1)
        doc.wasGeneratedBy(libs, get_libraries)
        doc.wasDerivedFrom(libs1, libsite)
        
        return doc
        
# get_libraries.execute()
# get_libraries.provenance()