# writes demographics_by_towns to database
# shows race data per town (all of mass)
# not using

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import json
import pandas as pd
from pprint import pprint
class demographics_by_towns(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = []
    writes = ['carlosp_jpva_tkay_yllescas.demographics_by_towns']

    @staticmethod
    def get_data():
        with open('demographics_by_towns.json') as f:
            data = json.load(f)
            return data
        



    @staticmethod
    def execute(trial = False):
        print("demographics_by_towns")
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        d_t = demographics_by_towns


        url = "http://datamechanics.io/data/carlosp_jpva_tkay_yllescas/demographics_by_towns.json"
        response = urllib.request.urlopen(url).read().decode("utf-8")
        d_t_json = json.loads(response)
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        
        s = json.dumps(d_t_json , sort_keys=True, indent=2)
        repo.dropCollection("demographics_by_towns")
        repo.createCollection("demographics_by_towns")
        repo['carlosp_jpva_tkay_yllescas.demographics_by_towns'].insert_many(d_t_json)
        repo['carlosp_jpva_tkay_yllescas.demographics_by_towns'].metadata({'complete':True})
        print(repo['carlosp_jpva_tkay_yllescas.demographics_by_towns'].metadata())


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
#        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('bdp', 'http://datamechanics.io/data/carlosp_jpva_tkay_yllescas/demographics_by_towns.json')

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#demographics_by_town', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_demographics_by_town = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_demographics_by_town, this_script)
        doc.usage(get_demographics_by_town, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?type=Demographics+By+Town&$select=type,latitude,longitude,OPEN_DT'
                  }
                  )
        demographics_by_town = doc.entity('dat:carlosp_jpva_tkay_yllescas#demographics_by_town', {prov.model.PROV_LABEL:'Demographics by Town', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(demographics_by_town, this_script)
        doc.wasGeneratedBy(demographics_by_town, get_demographics_by_town, endTime)
        doc.wasDerivedFrom(demographics_by_town, resource, get_demographics_by_town, get_demographics_by_town, get_demographics_by_town)

        repo.logout()
                  
        return doc

#d_t = demographics_by_towns
#
#d_t.execute()

## eof