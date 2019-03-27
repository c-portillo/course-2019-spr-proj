import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from shapely.geometry import Point, MultiPolygon, shape

class transportation(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = ['soohyeok_soojee.get_neighborhoods', 'soohyeok_soojee.get_trainStations', 'soohyeok_soojee.get_busStops']
    writes = ['soohyeok_soojee.transportation']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        neighborhoodData = repo['soohyeok_soojee.get_neighborhoods'].find()
        trainStations = repo['soohyeok_soojee.get_trainStations'].find()
        busStops = repo['soohyeok_soojee.get_busStops'].find()

        # select town name and coordinates
        neighborhoods = {}
        rate = {}
        for n in neighborhoodData:
            neighborhoods[n['properties']['Name']] = n['geometry']
            rate[n['properties']['Name']] = 0

        train = [shape(t['geometry']) for t in trainStations]
        bus = [shape(b['geometry']) for b in busStops]
        mergeData = train + bus

        for point in mergeData:
            for name in neighborhoods:
                if point.within(shape(neighborhoods[name])):
                    rate[name] += 1

        repo.dropCollection("transportation")
        repo.createCollection("transportation")
        repo['soohyeok_soojee.transportation'].insert_many([rate])
        repo['soohyeok_soojee.transportation'].metadata({'complete':True})
        print(repo['soohyeok_soojee.transportation'].metadata())

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
        doc.add_namespace('bod', 'http://bostonopendata-boston.opendata.arcgis.com/datasets')

        this_script = doc.agent('alg:soohyeok_soojee#transportation', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'get_neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_train = doc.entity('dat:soohyeok_soojee#get_trainStations', {prov.model.PROV_LABEL:'get_trainStations', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_bus = doc.entity('dat:soohyeok_soojee#get_busStops', {prov.model.PROV_LABEL:'get_busStops', prov.model.PROV_TYPE:'ont:DataSet'})

        get_transportation = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_transportation, this_script)
        doc.usage(get_transportation, resource_neighborhoods, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_transportation, resource_train, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_transportation, resource_bus, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        transportation = doc.entity('dat:soohyeok_soojee#transportation', {prov.model.PROV_LABEL:'transportation', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(transportation, this_script)
        doc.wasGeneratedBy(transportation, get_transportation, endTime)
        doc.wasDerivedFrom(transportation, resource_neighborhoods, get_transportation, get_transportation, get_transportation)
        doc.wasDerivedFrom(transportation, resource_train, get_transportation, get_transportation, get_transportation)
        doc.wasDerivedFrom(transportation, resource_bus, get_transportation, get_transportation, get_transportation)


        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
transportation.execute()
doc = transportation.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
