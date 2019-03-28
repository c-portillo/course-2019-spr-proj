import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pymongo
import pandas as pd

class boston_homevalue_neighkey(dml.Algorithm):
    contributor = 'xcao19'
    reads = ['xcao19.neighborhoods', 'xcao19.homevalues','xcao19.boston_homevalue']
    writes = ['xcao19.boston_homevalue','xcao19.boston_homevalue_neighkey']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')


       
        #Selection
        Boston_vals = repo['xcao19.homeValues'].find({"City": "Boston"}, {"_id": 0, "RegionName": 1, "2019-01": 1})
        
        repo.dropCollection('boston_homevalue')
        repo.createCollection('boston_homevalue')
        repo['xcao19.boston_homevalue'].insert_many(Boston_vals)
        repo['xcao19.boston_homevalue'].metadata({'complete':True})
        
        pipeline = [
                    {"$lookup": 
                        {
                            "from": "xcao19.boston_homevalue",
                            "localField": "neighbourhood",
                            "foreignField": "RegionName",
                            "as": "joined_neighborhood"
                        }

                    }
                ]

        #Outer join / Aggregation
        res = repo['xcao19.neighborhoods'].aggregate(pipeline)        
        # repo.dropCollection("average_homeValue")
        # repo.dropCollection("average_homeValue.metadata")
        # repo.dropCollection("average_homeValue_neighkey")
        # repo.dropCollection("average_homeValue_neighkey.metadata")
        repo.dropCollection("boston_homevalue_neighkey")
        repo.createCollection("boston_homevalue_neighkey")
        repo['xcao19.boston_homevalue_neighkey'].insert_many(res)
        repo['xcao19.boston_homevalue_neighkey'].metadata({'complete':True})

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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        neighborhoods = doc.entity('dat:xcao19_neighborhoods', 
            {prov.model.PROV_LABEL: 'dat: xcao19_neighborhoods', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})
        homevalues = doc.entity('dat:xcao19_homeValues', 
            {prov.model.PROV_LABEL: 'dat: xcao19_homeValues', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})
        boston_homevalue = doc.entity('dat:xcao19_boston_homevalue', 
            {prov.model.PROV_LABEL: 'dat: xcao19_boston_homevalue', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})
        boston_homevalue_neighkey = doc.entity('dat:xcao19_boston_homevalue_neighkey', 
            {prov.model.PROV_LABEL: 'dat: xcao19_boston_homevalue_neighkey', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})

        this_script = doc.agent('alg: xcao19_boston_homevalue_neighkey.py', 
                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        transform = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime, {prov.model.PROV_TYPE: 'ont: Computation'})

        doc.wasDerivedFrom(boston_homevalue, homevalues,transform, transform, transform)
        doc.wasDerivedFrom(boston_homevalue, neighborhoods,transform, transform, transform)
        doc.wasAttributedTo(boston_homevalue, this_script)
        doc.wasGeneratedBy(boston_homevalue, transform)

        doc.wasDerivedFrom(boston_homevalue_neighkey,boston_homevalue)
        doc.wasDerivedFrom(boston_homevalue_neighkey,neighborhoods)
        doc.wasAttributedTo(boston_homevalue_neighkey,this_script)
        doc.wasGeneratedBy(boston_homevalue_neighkey,transform)

        doc.wasAssociatedWith(transform,this_script) 
        doc.usage(transform, neighborhoods, startTime, None, {prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.usage(transform, homevalues, startTime, None, {prov.model.PROV_TYPE: 'ont:DataSet'})

        return doc

# boston_homevalue_neighkey.execute()
# doc = boston_homevalue_neighkey.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
