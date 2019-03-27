import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from math import radians, sqrt, sin, cos, atan2

def product(R, S):
  return [(t,u) for t in R for u in S]

def aggregate(R, f):
  keys = {r[0] for r in R}
  return [(key, f([v for (k,v) in R if k == key])) for key in keys]

def geodistance(la1, lo1, la2, lo2):
  EARTH_R = 6378.0
  la1 = radians(la1)
  lo1 = radians(lo1)
  la2 = radians(la2)
  lo2 = radians(lo2)

  long_dif = lo1 - lo2
  y = sqrt(
      (cos(la2) * sin(long_dif)) ** 2
      + (cos(la1) * sin(la2) - sin(la1) * cos(la2) * cos(long_dif)) ** 2
      )
  x = sin(la1) * sin(la2) + cos(la1) * cos(la2) * cos(long_dif)
  c = atan2(y, x)

  return EARTH_R * c



class transformBikeCrash(dml.Algorithm):
    contributor = 'nhuang54_wud'
    reads = ['nhuang54_wud.crashRecord', 'nhuang54_wud.streetlightLocation']
    writes = ['nhuang54_wud.bikeCrashStreetlight']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('nhuang54_wud', 'nhuang54_wud')

        # Get the data
        crashLocations = repo.nhuang54_wud.crashRecord.find()
        lightLocations = repo.nhuang54_wud.streetlightLocation.find()  


        # Select to only get bike crashes
        bikeCrashes = [t for t in crashLocations if t['"mode_type"'] == 'bike']

        bikeCrashesShort = bikeCrashes[0:20]
        # print(bikeCrashesShort)

        lightLoc = [t for t in lightLocations if t['TYPE'] == 'LIGHT']
        # Product between bike crashes and streetlight locations
        crashLightProduct = product(bikeCrashesShort, lightLoc)

        # Project to add 'distance' column.
        crashLightDistances = [(t[0]['\ufeff"dispatch_ts"'], geodistance(float(t[0]['"lat"']), float(t[0]['"long"\r']), float(t[1]['Lat']), float(t[1]['Long']))) for t in crashLightProduct]

        # Aggregate
        finalSet = aggregate(crashLightDistances, min)

        # Put into dictionary
        finalDict = {}
        for tup in finalSet:
          finalDict[tup[0]] = str(tup[1])

        with open("nhuang54_wud/new_datasets/crashesAndLights.json", 'w') as outfile:
          json.dump(finalDict, outfile)
        
        repo.dropCollection("bikeCrashStreetlight")
        repo.createCollection("bikeCrashStreetlight")
        for key,value in finalDict.items():
          repo['nhuang54_wud.bikeCrashStreetlight'].insert_one({key:value})
        # repo['nhuang54_wud.bikeCrashStreetlight'].insertMany()
        repo['nhuang54_wud.bikeCrashStreetlight'].metadata({'complete':True})
        print(repo['nhuang54_wud.bikeCrashStreetlight'].metadata())

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
        repo.authenticate('nhuang54_wud', 'nhuang54_wud')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:nhuang54_wud#transformBikeCrash', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource1 = doc.entity('dat:nhuang54_wud#streetlight-locations', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        resource2 = doc.entity('dat:nhuang54_wud#crash_open_data', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        
        transform_bikeCrash = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(transform_bikeCrash, this_script)

        doc.usage(transform_bikeCrash, resource1, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Calculation',
                  'ont:Query':''
                  }
                  )
        doc.usage(transform_bikeCrash, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Calculation',
                  'ont:Query':''
                  }
                  )

        bikeCrashStreetlight = doc.entity('dat:nhuang54_wud#bikeCrashStreetlight', {prov.model.PROV_LABEL:'Bike crashes proximity to street lights', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(bikeCrashStreetlight, this_script)
        doc.wasGeneratedBy(bikeCrashStreetlight, transform_bikeCrash, endTime)
        doc.wasDerivedFrom(bikeCrashStreetlight, resource1, transform_bikeCrash, transform_bikeCrash, transform_bikeCrash)
        doc.wasDerivedFrom(bikeCrashStreetlight, resource2, transform_bikeCrash, transform_bikeCrash, transform_bikeCrash)


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

if __name__ == '__main__':
    transformBikeCrash.execute()

## eof
