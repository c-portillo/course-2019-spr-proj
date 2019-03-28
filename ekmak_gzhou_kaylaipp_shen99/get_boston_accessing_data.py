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


class get_boston_accessing_data(dml.Algorithm):

    contributor = 'ekmak_gzhou_kaylaipp_shen99'
    reads = []
    writes = ['ekmak_gzhou_kaylaipp_shen99.accessing_data']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ekmak_gzhou_kaylaipp_shen99','ekmak_gzhou_kaylaipp_shen99')

        # #Retrieve boston tax acessing and add to mongo - source: Analyze Boston
        url = 'https://data.boston.gov/api/3/action/datastore_search?resource_id=fd351943-c2c6-4630-992d-3f895360febd&limit=40000&q=02127'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        r = r['result']['records']
        repo.dropCollection("accessing_data")
        repo.createCollection("accessing_data")
        for info in r: 
            repo['ekmak_gzhou_kaylaipp_shen99.accessing_data'].insert_one(info)
        repo['ekmak_gzhou_kaylaipp_shen99.accessing_data'].metadata({'complete':True})
        print(repo['ekmak_gzhou_kaylaipp_shen99.accessing_data'].metadata())
        print('inserted accessing data')

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

        this_script = doc.agent('alg:ekmak_gzhou_kaylaipp_shen99#get_boston_accessing_data', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:fd351943-c2c6-4630-992d-3f895360febd', {'prov:label':'Boston Accessing Data', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_boston_accessing_data = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_boston_accessing_data, this_script)
        doc.usage(get_boston_accessing_data, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )

        accessing_data = doc.entity('dat:ekmak_gzhou_kaylaipp_shen99#get_boston_accessing_data', {prov.model.PROV_LABEL:'Boston Accessing Data', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(accessing_data, this_script)
        doc.wasGeneratedBy(accessing_data, get_boston_accessing_data, endTime)
        doc.wasDerivedFrom(accessing_data, resource, get_boston_accessing_data, get_boston_accessing_data, get_boston_accessing_data)
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
# get_boston_accessing_data.execute()
# doc = get_boston_accessing_data.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
## eof
