import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class crime(dml.Algorithm):
    contributor = 'jkmoy_mfflynn'
    reads = []
    writes = ['jkmoy_mfflynn.crime']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('jkmoy_mfflynn', 'jkmoy_mfflynn')

        url = 'https://data.boston.gov/datastore/odata3.0/12cb3883-56f5-47de-afa5-3b1cf61b257b?$format=json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        r = r['value']
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("jkmoy_mfflynn.crime")
        repo.createCollection("jkmoy_mfflynn.crime")
        repo['jkmoy_mfflynn.crime'].insert_many(r)

        '''
        #2nd data set that goes with this
        url = 'https://data.boston.gov/datastore/odata3.0/ba5ed0e2-e901-438c-b2e0-4acfc3c452b9?$format=json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo['jkmoy_mfflynn.crime'].insert_many(r)
        '''
        
        repo['jkmoy_mfflynn.crime'].metadata({'complete':True})
        print(repo['jkmoy_mfflynn.crime'].metadata())

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
        repo.authenticate('jkmoy_mfflynn', 'jkmoy_mfflynn')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:jkmoy_mfflynn#crime', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:crimes', {'prov:label':'Boston Crimes', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_crime = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_crime, this_script)
        doc.usage(get_crime, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'})

        crime = doc.entity('dat:jkmoy_mfflynn#crime', {prov.model.PROV_LABEL:'Crimes of Boston', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(crime, this_script)
        doc.wasGeneratedBy(crime, get_crime, endTime)
        doc.wasDerivedFrom(crime, resource, get_crime, get_crime, get_crime)

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

## eof
