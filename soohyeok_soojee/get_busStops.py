import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class get_busStops(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = []
    writes = ['soohyeok_soojee.get_busStops']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/2c00111621954fa08ff44283364bba70_0.geojson'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("get_busStops")
        repo.createCollection("get_busStops")
        repo['soohyeok_soojee.get_busStops'].insert_many(r['features'])
        repo['soohyeok_soojee.get_busStops'].metadata({'complete':True})
        print(repo['soohyeok_soojee.get_busStops'].metadata())

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

        this_script = doc.agent('alg:soohyeok_soojee#get_busStops', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bod:busStops', {'prov:label':'Bus Stops', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
        get_bus = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_bus, this_script)
        doc.usage(get_bus, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        busStops = doc.entity('dat:soohyeok_soojee#get_busStops', {prov.model.PROV_LABEL:'Bus Stops in Boston', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(busStops, this_script)
        doc.wasGeneratedBy(busStops, get_bus, endTime)
        doc.wasDerivedFrom(busStops, resource, get_bus, get_bus, get_bus)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
get_busStops.execute()
doc = get_busStops.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
