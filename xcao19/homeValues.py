import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class homeValues(dml.Algorithm):
    contributor = 'xcao19'
    reads = []
    writes = ['xcao19.homeValues']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')

        url = 'http://files.zillowstatic.com/research/public/Neighborhood/Neighborhood_Zhvi_2bedroom.csv'
        df = pd.read_csv(url, encoding = 'ISO-8859-1')
        json_df = df.to_json(orient='records')
        r = json.loads(json_df)
        repo.dropCollection("homeValues")
        repo.createCollection("homeValues")
        repo['xcao19.homeValues'].insert_many(r)
        repo['xcao19.homeValues'].metadata({'complete':True})

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
        doc.add_namespace('zil', 'https://www.zillow.com/research/data/#bulk')
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        #Entities
        resource = doc.entity('zil: Neighborhood_Zhvi_2bedroom.csv', 
                {prov.model.PROV_TYPE: 'ont:DataResource',
                'ont: Extension': 'csv'})
        homeValues = doc.entity('dat: xcao19.homeValues', {prov.model.PROV_LABEL: 'homeValues', prov.model.PROV_TYPE: 'ont: DataSet'})

        #Agents
        this_script = doc.agent('alg: xcao19_homeValues.py', 
                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': '.py'})

        #Algos/Activities
        get_resource = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        #Prov
        doc.wasAssociatedWith(get_resource, this_script)
        doc.wasAttributedTo(homeValues, this_script)
        doc.wasGeneratedBy(homeValues, get_resource, endTime)
        doc.usage(get_resource, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'RegionID,RegionName,City,State,Metro,CountyName,SizeRank,<Year,Month>'
                   }
                  )
        doc.wasDerivedFrom(homeValues, resource, get_resource, get_resource, get_resource)
        repo.logout()

        return doc

# homeValues.execute()
# doc = homeValues.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))