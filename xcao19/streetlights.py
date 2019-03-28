import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pymongo
import pandas as pd

class streetlights(dml.Algorithm):
    contributor = 'xcao19'
    reads = []
    writes = ['xcao19.streetlights']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')

        url = 'https://data.boston.gov/dataset/52b0fdad-4037-460c-9c92-290f5774ab2b/resource/c2fcc1e3-c38f-44ad-a0cf-e5ea2a6585b5/download/streetlight-locations.csv'
        
        df = pd.read_csv(url, encoding = 'ISO-8859-1')
        json_df = df.to_json(orient='records')
        r = json.loads(json_df)
        
        repo.dropCollection("streetlights")
        repo.createCollection("streetlights")
        repo['xcao19.streetlights'].insert_many(r)
        repo['xcao19.streetlights'].metadata({'complete':True})

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
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('bdg', 'https://data.boston.gov/dataset')
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        #Entities
        resource = doc.entity('bdg: streetlight-locations.csv', 
                {prov.model.PROV_TYPE: 'ont:DataResource',
                'ont: Extension': 'csv'})
        streetlights = doc.entity('dat: xcao19.streetlights', {prov.model.PROV_LABEL: 'streetlights', prov.model.PROV_TYPE: 'ont: DataSet'})

        #Agents
        this_script = doc.agent('alg: xcao19_streetlights.py', 
                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': '.py'})

        #Algos/Activities
        get_resource = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        #Prov
        doc.wasAssociatedWith(get_resource, this_script)
        doc.wasAttributedTo(streetlights, this_script)
        doc.wasGeneratedBy(streetlights, get_resource, endTime)
        doc.usage(get_resource, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'the_geom,OBJECTID,TYPE,Lat,Long'
                   }
                  )
        doc.wasDerivedFrom(streetlights, resource, get_resource, get_resource, get_resource)
        repo.logout()

        return doc

# streetlights.execute()
# doc = streetlights.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
