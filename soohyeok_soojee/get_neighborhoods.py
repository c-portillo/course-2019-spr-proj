import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class get_neighborhoods(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = []
    writes = ['soohyeok_soojee.get_neighborhoods']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/3525b0ee6e6b427f9aab5d0a1d0a1a28_0.geojson'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("get_neighborhoods")
        repo.createCollection("get_neighborhoods")
        repo['soohyeok_soojee.get_neighborhoods'].insert_many(r['features'])
        repo['soohyeok_soojee.get_neighborhoods'].metadata({'complete':True})
        print(repo['soohyeok_soojee.get_neighborhoods'].metadata())

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
        doc.add_namespace('bod', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bod:neighborhoods', {'prov:label':'Boston Neighborhoods', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
        get_nighbors = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_nighbors, this_script)
        doc.usage(get_nighbors, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'Neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(neighborhoods, this_script)
        doc.wasGeneratedBy(neighborhoods, get_nighbors, endTime)
        doc.wasDerivedFrom(neighborhoods, resource, get_nighbors, get_nighbors, get_nighbors)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
get_neighborhoods.execute()
doc = get_neighborhoods.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
