import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pymongo
import pandas as pd

class AirBNB_neighborhoods(dml.Algorithm):
    contributor = 'xcao19'
    reads = []
    writes = ['xcao19.neighbourhoods']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')

        url = 'http://data.insideairbnb.com/united-states/ma/boston/2019-01-17/visualisations/neighbourhoods.csv'
        
        df = pd.read_csv(url, encoding = 'ISO-8859-1')
        json_df = df.to_json(orient='records')
        r = json.loads(json_df)
        
        repo.dropCollection("neighborhoods")
        repo.createCollection("neighborhoods")
        repo['xcao19.neighborhoods'].insert_many(r)
        repo['xcao19.neighborhoods'].metadata({'complete':True})

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
        doc.add_namespace('bnb', 'http://insideairbnb.com/get-the-data.html')
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        #Entities
        resource = doc.entity('bnb: neighbourhoods.csv', 
                {prov.model.PROV_TYPE: 'ont:DataResource','ont: Extension': 'csv'})
        neighborhoods = doc.entity('dat: xcao19.neighborhoods', {prov.model.PROV_LABEL: 'airbnb neighborhoods', prov.model.PROV_TYPE: 'ont: DataSet'})

        #Agents
        this_script = doc.agent('alg: xcao19_AirBNB_neighborhoods.py', 
                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': '.py'})

        #Algos/Activities
        get_resource = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        #Prov
        doc.wasAssociatedWith(get_resource, this_script)
        doc.wasAttributedTo(neighborhoods, this_script)
        doc.wasGeneratedBy(neighborhoods, get_resource, endTime)
        doc.wasDerivedFrom(neighborhoods, resource, get_resource, get_resource, get_resource)
        doc.usage(get_resource, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'neighbourhood_group,neighbourhoods'
                   }
                  )
        repo.logout()

        return doc

# AirBNB_neighborhoods.execute()
# doc = AirBNB_neighborhoods.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))