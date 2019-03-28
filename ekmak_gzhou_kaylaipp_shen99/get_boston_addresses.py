import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import zillow 
import requests
import xmltodict
import csv


class get_boston_addresses(dml.Algorithm):

    contributor = 'ekmak_gzhou_kaylaipp_shen99'
    reads = []
    writes = ['ekmak_gzhou_kaylaipp_shen99.address_data']

    @staticmethod
    def execute(trial = True):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ekmak_gzhou_kaylaipp_shen99','ekmak_gzhou_kaylaipp_shen99')
        
        # #Retrieve all boston addresses and add to monogo - source: Analyze Boston
        url = 'https://data.boston.gov/api/3/action/datastore_search?resource_id=26933f1b-bcaa-4241-b0f2-7933570fd52d&limit=40000&q=02127'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        r = r['result']['records']
        repo.dropCollection("address_data")
        repo.createCollection("address_data")
        for info in r: 
            repo['ekmak_gzhou_kaylaipp_shen99.address_data'].insert_one(info)
        repo['ekmak_gzhou_kaylaipp_shen99.address_data'].metadata({'complete':True})
        print(repo['ekmak_gzhou_kaylaipp_shen99.address_data'].metadata())
        print('inserted address data')

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
        repo.authenticate('ekmak_gzhou_kaylaipp_shen99','ekmak_gzhou_kaylaipp_shen99')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:ekmak_gzhou_kaylaipp_shen99#get_boston_address_data', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:26933f1b-bcaa-4241-b0f2-7933570fd52d', {'prov:label':'Boston Address Data', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_boston_address_data = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_boston_address_data, this_script)
        doc.usage(get_boston_address_data, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )

        address_data = doc.entity('dat:ekmak_gzhou_kaylaipp_shen99#get_boston_address_data', {prov.model.PROV_LABEL:'Boston Address Data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(address_data, this_script)
        doc.wasGeneratedBy(address_data, get_boston_address_data, endTime)
        doc.wasDerivedFrom(address_data, resource, get_boston_address_data, get_boston_address_data, get_boston_address_data)

        repo.logout()
                  
        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''
# get_boston_addresses.execute()
## eof
