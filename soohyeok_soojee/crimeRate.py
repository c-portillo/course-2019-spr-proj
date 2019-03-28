import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from shapely.geometry import Point, MultiPolygon, shape

class crimeRate(dml.Algorithm):
    contributor = 'soohyeok_soojee'
    reads = ['soohyeok_soojee.get_neighborhoods', 'soohyeok_soojee.get_crimeData']
    writes = ['soohyeok_soojee.crimeRate']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('soohyeok_soojee', 'soohyeok_soojee')

        neighborhoodData = repo['soohyeok_soojee.get_neighborhoods'].find()
        crimeData = repo['soohyeok_soojee.get_crimeData'].find()

        # select town name and coordinates
        neighborhoods = {}
        rate = {}
        for n in neighborhoodData:
            neighborhoods[n['properties']['Name']] = n['geometry']
            rate[n['properties']['Name']] = 0

        # collect all the locations
        crimeLocations = []
        for c in crimeData:
            location = c['location'][1:-1]
            location2 = tuple(map(float, location.split(',')))
            crimeLocations.append(location2[::-1])

        for point in crimeLocations:
            for name in neighborhoods:
                if Point(point).within(shape(neighborhoods[name])):
                    rate[name] += 1

        repo.dropCollection("crimeRate")
        repo.createCollection("crimeRate")
        repo['soohyeok_soojee.crimeRate'].insert_many([rate])
        repo['soohyeok_soojee.crimeRate'].metadata({'complete':True})
        print(repo['soohyeok_soojee.crimeRate'].metadata())

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

        this_script = doc.agent('alg:soohyeok_soojee#crimeRate', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource_neighborhoods = doc.entity('dat:soohyeok_soojee#get_neighborhoods', {prov.model.PROV_LABEL:'get_neighborhoods', prov.model.PROV_TYPE:'ont:DataSet'})
        resource_crimes = doc.entity('dat:soohyeok_soojee#get_crimeData', {prov.model.PROV_LABEL:'get_crimeData', prov.model.PROV_TYPE:'ont:DataSet'})
        get_crimeRate = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_crimeRate, this_script)
        doc.usage(get_crimeRate, resource_neighborhoods, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )
        doc.usage(get_crimeRate, resource_crimes, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        crimeRate = doc.entity('dat:soohyeok_soojee#crimeRate', {prov.model.PROV_LABEL:'crimeRate', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(crimeRate, this_script)
        doc.wasGeneratedBy(crimeRate, get_crimeRate, endTime)
        doc.wasDerivedFrom(crimeRate, resource_neighborhoods, get_crimeRate, get_crimeRate, get_crimeRate)
        doc.wasDerivedFrom(crimeRate, resource_crimes, get_crimeRate, get_crimeRate, get_crimeRate)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
crimeRate.execute()
doc = crimeRate.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
