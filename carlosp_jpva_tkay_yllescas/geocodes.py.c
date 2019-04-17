# finds google geocode for town
# not using because not just Boston

import urllib
import json
import dml
import prov.model
import datetime
import uuid
import sys
import math
from urllib import request, parse

class geocodes(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = ["carlosp_jpva_tkay_yllescas.demographics_by_towns"]
    writes = ['carlosp_jpva_tkay_yllescas.geocodes']
        
    @staticmethod
    def execute(trial = False):
        print("geocodes")
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        repo.dropCollection("geocodes")
        repo.createCollection("geocodes")
        demographics = repo['carlosp_jpva_tkay_yllescas.demographics_by_towns'].find()
        
        count = 0
        for town in demographics:
            if count%5==0:
                sys.stdout.write(str(math.floor(count/demographics.count()*100)) + "% processed\r")   
                sys.stdout.flush()
            count+=1
            query = urllib.parse.urlencode({"address": town["Community"], "key": dml.auth["services"]["googlegeocoding"]["key"]})     
            url = "https://maps.googleapis.com/maps/api/geocode/json?" + query
            response = urllib.request.urlopen(url).read().decode("utf-8")
            r = json.loads(response)
            repo['carlosp_jpva_tkay_yllescas.geocodes'].insert_one(r)
                
        repo['carlosp_jpva_tkay_yllescas.geocodes'].metadata({'complete':True})
        print(repo['carlosp_jpva_tkay_yllescas.geocodes'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://amplifylatinx.co/')

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#geocodes', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_geocodes = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_geocodes, this_script)
        doc.usage(get_geocodes, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Town&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )

        geocodes = doc.entity('dat:carlosp_jpva_tkay_yllescas#geocodes', {prov.model.PROV_LABEL:'Town', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(geocodes, this_script)
        doc.wasGeneratedBy(geocodes, get_geocodes, endTime)
        doc.wasDerivedFrom(geocodes, resource, get_geocodes, get_geocodes, get_geocodes)

        repo.logout()
                  
        return doc

# geocodes.execute()
'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof