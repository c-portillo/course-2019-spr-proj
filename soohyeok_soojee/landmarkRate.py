import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from shapely.geometry import Point, MultiPolygon, shape

class landmarkRate(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = ['soohyeok_soojee.get_neighborhoods', 'soohyeok_soojee.get_landmarks']
    writes = ['soohyeok_soojee.landmarkRate']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        neighborhoodData = repo['soohyeok_soojee.get_neighborhoods'].find()
        landmarkData = repo['soohyeok_soojee.get_landmarks'].find()

        # select town name and coordinates
        neighborhoods = {}
        rate = {}
        for n in neighborhoodData:
            neighborhoods[n['properties']['Name']] = n['geometry']
            rate[n['properties']['Name']] = 0

        # collect all the locations
        landmarkLocations = []
        a = 0
        for c in landmarkData:
            a += 1
            location = shape(c['geometry']).centroid
            landmarkLocations.append(location)

        for polygon in landmarkLocations:
            for name in neighborhoods:
                if polygon.within(shape(neighborhoods[name])):
                    rate[name] += 1

        repo.dropCollection("landmarkRate")
        repo.createCollection("landmarkRate")
        repo['soohyeok_soojee.landmarkRate'].insert_many([rate])
        repo['soohyeok_soojee.landmarkRate'].metadata({'complete':True})
        print(repo['soohyeok_soojee.landmarkRate'].metadata())

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
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:soohyeok_soojee#landmarkRate', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'get_neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_landmark = doc.entity('dat:soohyeok_soojee#get_landmarks', {prov.model.PROV_LABEL:'get_landmarks', prov.model.PROV_TYPE:'ont:DataSet'})
        get_landmarkRate = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_landmarkRate, this_script)
        doc.usage(get_landmarkRate, resource_neighborhoods, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_landmarkRate, resource_landmark, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        landmarkRate = doc.entity('dat:soohyeok_soojee#landmarkRate', {prov.model.PROV_LABEL:'landmarkRate', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(landmarkRate, this_script)
        doc.wasGeneratedBy(landmarkRate, get_landmarkRate, endTime)
        doc.wasDerivedFrom(landmarkRate, resource_neighborhoods, get_landmarkRate, get_landmarkRate, get_landmarkRate)
        doc.wasDerivedFrom(landmarkRate, resource_landmark, get_landmarkRate, get_landmarkRate, get_landmarkRate)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
landmarkRate.execute()
doc = landmarkRate.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
