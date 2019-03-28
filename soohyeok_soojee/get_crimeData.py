import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import ssl

class get_crimeData(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = []
    writes = ['soohyeok_soojee.get_crimeData']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        url = 'https://data.boston.gov/api/3/action/datastore_search?resource_id=12cb3883-56f5-47de-afa5-3b1cf61b257b&limit=5000'
        context = ssl._create_unverified_context()
        response = urllib.request.urlopen(url, context=context).read().decode("utf-8")
        r = json.loads(response)['result']['records']
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("get_crimeData")
        repo.createCollection("get_crimeData")
        repo['soohyeok_soojee.get_crimeData'].insert_many(r)
        repo['soohyeok_soojee.get_crimeData'].metadata({'complete':True})
        print(repo['soohyeok_soojee.get_crimeData'].metadata())

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
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('dbg', 'https://data.boston.gov/datastore/odata3.0/')

        this_script = doc.agent('alg:soohyeok_soojee#get_crimeData', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dbg:crimes', {'prov:label':'Crime Incident Reports', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_crime = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_crime, this_script)
        doc.usage(get_crime, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        crimeData = doc.entity('dat:soohyeok_soojee#get_crimeData', {prov.model.PROV_LABEL:'Crime Incident Reports in Boston', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(crimeData, this_script)
        doc.wasGeneratedBy(crimeData, get_crime, endTime)
        doc.wasDerivedFrom(crimeData, resource, get_crime, get_crime, get_crime)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
get_crimeData.execute()
doc = get_crimeData.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
