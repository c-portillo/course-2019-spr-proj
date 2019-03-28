import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class policeStation(dml.Algorithm):
    contributor = 'xcao19'
    reads = []
    writes = ['xcao19.policeStation']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')

        url = "https://data.boston.gov/datastore/dump/0b2be5cb-89c6-4328-93be-c54ba723f8db?q=&sort=_id+asc&fields=X%2CY%2COBJECTID%2CBLDG_ID%2CBID%2CADDRESS%2CPOINT_X%2CPOINT_Y%2CNAME%2CNEIGHBORHOOD%2CCITY%2CZIP%2CFT_SQFT%2CSTORY_HT%2CPARCEL_ID&filters=%7B%7D&format=csv"
        df = pd.read_csv(url, encoding = 'ISO-8859-1')
        json_df = df.to_json(orient='records')
        r = json.loads(json_df)
        repo.dropCollection("policeStation")
        repo.createCollection("policeStation")
        repo['xcao19.policeStation'].insert_many(r)
        repo['xcao19.policeStation'].metadata({'complete':True})

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
        resource = doc.entity('bdg: Boston_Police_Stations.csv', 
                {prov.model.PROV_TYPE: 'ont:DataResource',
                'ont: Extension': 'csv'})
        policeStation = doc.entity('dat: xcao19.policeStation', {prov.model.PROV_LABEL: 'policeStation', prov.model.PROV_TYPE: 'ont: DataSet'})
        #Agents
        this_script = doc.agent('alg: xcao19_policeStation.py', 
                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': '.py'})

        #Algos/Activities
        get_resource = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        #Prov
        doc.wasAssociatedWith(get_resource, this_script)
        doc.usage(get_resource, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'X, Y, OBJECTID, BLDG_ID, BID, ADDRESS, POINT_X, POINT_Y, NAME, NEIGHBORHOOD, CITY, BOSTON, ZIP, FT_SQFT, STORY_HT, PARCEL_ID'
                   }
                  )
        doc.wasAttributedTo(policeStation, this_script)
        doc.wasGeneratedBy(policeStation, get_resource, endTime)
        doc.wasDerivedFrom(policeStation, resource, get_resource, get_resource, get_resource)

        repo.logout()

        return doc

# policeStation.execute()
# doc = policeStation.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
