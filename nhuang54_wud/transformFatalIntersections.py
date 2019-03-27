import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from math import radians, sqrt, sin, cos, atan2

def product(R, S):
  return [(t,u) for t in R for u in S]

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

class transformFatalIntersections(dml.Algorithm):
    contributor = 'nhuang54_wud'
    reads = ['nhuang54_wud.bikeFatality', 'nhuang54_wud.trafficSignal']
    writes = ['nhuang54_wud.bikeFatalityTrafficSignal']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('nhuang54_wud', 'nhuang54_wud')

        # Get the data
        fatalityLocations = repo.nhuang54_wud.bikeFatality.find()
        trafficLocations = repo.nhuang54_wud.trafficSignal.find()

        # Select fatalities at intersections
        intersectionFatalities = [t for t in fatalityLocations if t['"location_type"'] == 'Intersection']

        # Put traffic locations in an array
        trafficArray = [t for t in trafficLocations if t['Y'] != '']

        # Project Intersections
        intersectionProjected = [(t['\ufeff"date_time"'], t['"street"'], t['"xstreet1"'], t['"xstreet2"'], float(t['"long"']), float(t['"lat"\r'])) for t in intersectionFatalities]

        # Project Traffic Lights: location, x, y
        trafficProjected = [(t['Location'], float(t['\ufeffX']), float(t['Y'])) for t in trafficArray]

        # Product between the two sets
        intersectionTrafficProduct = product(intersectionProjected, trafficProjected)

        # Project to show distance between the death and every traffic light
        intersectionTrafficDistances = [(t[0], t[1], geodistance(t[0][4], t[0][5], t[1][1], t[1][2])) for t in intersectionTrafficProduct]

        # Put into dictionary
        finalDict = {}
        counter = 0;
        for tup in intersectionTrafficDistances:
          finalDict[str(counter)] = str(tup)
          counter += 1

        with open("nhuang54_wud/new_datasets/intersectionFatalitiesDistances.json", 'w') as outfile:
          json.dump(finalDict, outfile)

        repo.dropCollection("bikeFatalityTrafficSignal")
        repo.createCollection("bikeFatalityTrafficSignal")

        for key,value in finalDict.items():
          repo['nhuang54_wud.bikeFatalityTrafficSignal'].insert_one({key:value})

        repo['nhuang54_wud.bikeFatalityTrafficSignal'].metadata({'complete':True})
        print(repo['nhuang54_wud.bikeFatalityTrafficSignal'].metadata())

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

        ##### add in code for provenance

        this_script = doc.agent('alg:nhuang54_wud#transformFatalIntersections', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource1 = doc.entity('dat:nhuang54_wud#fatality_open_data', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        resource2 = doc.entity('dat:nhuang54_wud#Traffic_Signals', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})

        transform_fatalIntersections = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(transform_fatalIntersections, this_script)

        doc.usage(transform_fatalIntersections, resource1, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Calculation',
                  'ont:Query':''
                  }
                  )
        doc.usage(transform_fatalIntersections, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Calculation',
                  'ont:Query':''
                  }
                  )

        bikeFatalityTrafficSignal= doc.entity('dat:nhuang54_wud#bikeFatalityTrafficSignal', {prov.model.PROV_LABEL:'Deaths proximity to intersections', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(bikeFatalityTrafficSignal, this_script)
        doc.wasGeneratedBy(bikeFatalityTrafficSignal, transform_fatalIntersections, endTime)
        doc.wasDerivedFrom(bikeFatalityTrafficSignal, resource1, transform_fatalIntersections, transform_fatalIntersections, transform_fatalIntersections)
        doc.wasDerivedFrom(bikeFatalityTrafficSignal, resource2, transform_fatalIntersections, transform_fatalIntersections, transform_fatalIntersections)


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
    transformFatalIntersections.execute();

## eof
