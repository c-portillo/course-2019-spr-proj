import json
import dml
import prov.model
import datetime
import uuid
from math import *


class Transformation2(dml.Algorithm):
    contributor = 'yufeng72'
    reads = ['yufeng72.collegeUniversities','yufeng72.hubwayStations']
    writes = ['yufeng72.stationNearbySchool']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('yufeng72', 'yufeng72')

        def getCollection(db):
            list = []
            for i in repo['yufeng72.' + db].find():
                list.append(i)
            return list

        def calcDistance(Lat_A, Lng_A, Lat_B, Lng_B):
            ra = 6378.140
            rb = 6356.755
            flatten = (ra - rb) / ra
            rad_lat_A = radians(Lat_A)
            rad_lng_A = radians(Lng_A)
            rad_lat_B = radians(Lat_B)
            rad_lng_B = radians(Lng_B)
            pA = atan(rb / ra * tan(rad_lat_A))
            pB = atan(rb / ra * tan(rad_lat_B))
            xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
            c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
            c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
            dr = flatten / 8 * (c1 - c2)
            distance = ra * (xx + dr)
            return distance

        collegesUniversities = getCollection('collegesUniversities')
        hubwayStations = getCollection('hubwayStations')
        r = []
        for row1 in collegesUniversities:
            if (int(row1['NumStudent']) > 0) and (row1['Latitude'] is not None) and (row1['Longitude'] is not None):
                hubwayStationCount = 0
                Lat_A = float(row1['Latitude'])
                Lng_A = float(row1['Longitude'])
                for row2 in hubwayStations:
                    if (row2['Latitude'] is not None) and (row2['Longitude'] is not None):
                        Lat_B = float(row2['Latitude'])
                        Lng_B = float(row2['Longitude'])
                    dist = calcDistance(Lat_A, Lng_A, Lat_B, Lng_B)
                    if dist < 0.3:  # 300m
                        hubwayStationCount += 1
                newRow = {'Name': row1['Name'], 'NumStudent': row1['NumStudent'], 'Latitude': row1['Latitude'],
                          'Longitude': row1['Longitude'], 'HubwayStationNearby': hubwayStationCount}
                r.append(newRow)

        repo.dropCollection('stationNearbySchool')
        repo.createCollection('stationNearbySchool')
        repo['yufeng72.stationNearbySchool'].insert_many(r)
        repo['yufeng72.stationNearbySchool'].metadata({'complete': True})
        print(repo['yufeng72.stationNearbySchool'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('yufeng72', 'yufeng72')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet',
        # 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:yufeng72#Transformation2',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        collegesUniversities = doc.entity('dat:yufeng72#collegesUniversities',
                                          {prov.model.PROV_LABEL: 'Colleges and Universities',
                                           prov.model.PROV_TYPE: 'ont:DataSet'})

        hubwayStations = doc.entity('dat:yufeng72#hubwayStations',
                                    {prov.model.PROV_LABEL: 'Hubway Stations', prov.model.PROV_TYPE: 'ont:DataSet'})

        get_stationNearbySchool = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_stationNearbySchool, this_script)
        doc.used(get_stationNearbySchool, collegesUniversities, startTime)
        doc.used(get_stationNearbySchool, hubwayStations, startTime)

        stationNearbySchool = doc.entity('dat:yufeng72#stationNearbySchool',
                                    {prov.model.PROV_LABEL: 'Count Hubway Stations nearby Colleges and Universities',
                                     prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(stationNearbySchool, this_script)
        doc.wasGeneratedBy(stationNearbySchool, get_stationNearbySchool, endTime)
        doc.wasDerivedFrom(stationNearbySchool, collegesUniversities, get_stationNearbySchool, get_stationNearbySchool,
                           get_stationNearbySchool)
        doc.wasDerivedFrom(stationNearbySchool, hubwayStations, get_stationNearbySchool, get_stationNearbySchool,
                           get_stationNearbySchool)
        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
Transformation2.execute()
doc = Transformation2.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
