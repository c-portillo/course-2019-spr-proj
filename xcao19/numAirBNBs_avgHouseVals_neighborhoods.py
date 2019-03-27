import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pymongo
import pandas as pd

class numAirBNBs_avgHouseVals_neighborhoods(dml.Algorithm):
    contributor = 'xcao19'
    reads = ['xcao19.homeValues', 'xcao19.listings']
    writes = ['xcao19.numAirBNBs_avgHouseVals_neighborhoods']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')


        #Aggregate number of listings per neighborhood

        pipeline = [{"$group": {"_id": "$neighbourhood", "num_airbnbs": {"$sum": 1}}}]

        #Aggregate
        numAirbnbs = list(repo['xcao19.listings'].aggregate(pipeline))
        homeValues = list(repo['xcao19.homeValues'].find())

        ##Outer join on neighborhoods
        res = []
        for e1 in numAirbnbs:
            for e2 in homeValues:
                if e1['_id'] == e2['RegionName']:
                    #Project
                    res.append({'neighborhood': e2['RegionName'], 'numAirbnbs': e1['num_airbnbs'], 'averageHomeValue': e2['2019-01']})

        repo.dropCollection("numAirBNBs_avgHouseVals_neighborhoods")
        repo.createCollection("numAirBNBs_avgHouseVals_neighborhoods")
        repo['xcao19.numAirBNBs_avgHouseVals_neighborhoods'].insert_many(res)
        repo['xcao19.numAirBNBs_avgHouseVals_neighborhoods'].metadata({'complete':True})
        
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

        homevalues = doc.entity('dat:xcao19_homeValues', 
            {prov.model.PROV_LABEL: 'dat: xcao19_homeValues', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})
        airbnb_listings = doc.entity('dat:xcao19_listings', 
            {prov.model.PROV_LABEL: 'dat: xcao19_listings', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})
        numAirBNBs_avgHouseVals_neighborhoods = doc.entity('dat:xcao19_numAirBNBs_avgHouseVals_neighborhoods', 
            {prov.model.PROV_LABEL: 'dat: xcao19_numAirBNBs_avgHouseVals_neighborhoods', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})

        this_script = doc.agent('alg: xcao19_numAirBNBs_avgHouseVals_neighborhoods.py', 
                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        execute = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime, {prov.model.PROV_TYPE: 'ont: Computation'})

        doc.wasDerivedFrom(numAirBNBs_avgHouseVals_neighborhoods, homevalues, execute, execute, execute)
        doc.wasDerivedFrom(numAirBNBs_avgHouseVals_neighborhoods, airbnb_listings, execute, execute, execute)
        doc.wasAttributedTo(numAirBNBs_avgHouseVals_neighborhoods, this_script)
        doc.wasGeneratedBy(numAirBNBs_avgHouseVals_neighborhoods, execute)

        doc.wasAssociatedWith(execute,this_script) 

        doc.usage(execute, homevalues, startTime, None, {prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.usage(execute, airbnb_listings, startTime, None, {prov.model.PROV_TYPE: 'ont:DataSet'})

        return doc

# numAirBNBs_avgHouseVals_neighborhoods.execute()
# doc = numAirBNBs_avgHouseVals_neighborhoods.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
