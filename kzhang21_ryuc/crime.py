import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd
from ast import literal_eval as make_tuple

class crime(dml.Algorithm):
    contributor = 'kzhang21_ryuc'
    reads = []
    writes = ['kzhang21_ryuc.crime']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')

        url = 'https://data.boston.gov/dataset/6220d948-eae2-4e4b-8723-2dc8e67722a3/resource/12cb3883-56f5-47de-afa5-3b1cf61b257b/download/tmpxjqz5gin.csv'
        response = pd.read_csv(url, header=0)

        # select relevant columnns
        data_crime = response[['district', 'offense_code', 'year', 'month']].copy()

        # rename to appropriate names
        data_crime.columns = ['District', 'Offense', 'Year', 'Month']

        #eliminate null districts
        data_crime.dropna(inplace=True)

        #response = urllib.request.urlopen(url).read().decode("utf-8")
        #r = json.loads(response)
        r = json.loads(data_crime.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)

        repo.dropCollection("crime")
        repo.createCollection("crime")
        repo['kzhang21_ryuc.crime'].insert_many(r)
        repo['kzhang21_ryuc.crime'].metadata({'complete':True})
        print(repo['kzhang21_ryuc.crime'].metadata())

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
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        # additional resource
        doc.add_namespace('crime', 'https://data.boston.gov/dataset/')

        this_script = doc.agent('alg:kzhang21_ryuc#crime', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('crime:6220d948-eae2-4e4b-8723-2dc8e67722a3/resource/12cb3883-56f5-47de-afa5-3b1cf61b257b/download/tmpxjqz5gin.csv', {'prov:label':'Crime, Crime Records', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        #get_found = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        #get_lost = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        #doc.wasAssociatedWith(get_found, this_script)
        #doc.wasAssociatedWith(get_lost, this_script)
        get_district = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_district, this_script)
        doc.usage(get_district, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        crime = doc.entity('dat:kzhang21_ryuc#crime', {prov.model.PROV_LABEL:'Crime District', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(crime, this_script)
        doc.wasGeneratedBy(crime, get_district, endTime)
        doc.wasDerivedFrom(crime, resource, get_district, get_district, get_district)

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
# crime.execute()
# doc = crime.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
