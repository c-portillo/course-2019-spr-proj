import json
import dml
import prov.model
import datetime
import uuid
from math import *


class Transformation3(dml.Algorithm):
    contributor = 'yufeng72'
    reads = ['yufeng72.collegeUniversities','yufeng72.tripData']
    writes = ['yufeng72.tripToSchool']

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
        tripData = getCollection('tripData')
        r = []
        for row1 in collegesUniversities:
            if (int(row1['NumStudent']) > 0) and (row1['Latitude'] is not None) and (row1['Longitude'] is not None):
                tripToSchoolCount = 0
                Lat_A = float(row1['Latitude'])
                Lng_A = float(row1['Longitude'])
                for row2 in tripData:
                    if (row2['end station latitude'] is not None) and (row2['end station longitude'] is not None):
                        Lat_B = float(row2['end station latitude'])
                        Lng_B = float(row2['end station longitude'])
                    dist = calcDistance(Lat_A, Lng_A, Lat_B, Lng_B)
                    if dist < 0.3:  # 300m
                        tripToSchoolCount += 1
                newRow = {'Name': row1['Name'], 'NumStudent': row1['NumStudent'], 'Latitude': row1['Latitude'],
                          'Longitude': row1['Longitude'], 'tripToSchool': tripToSchoolCount}
                r.append(newRow)

        repo.dropCollection('tripToSchool')
        repo.createCollection('tripToSchool')
        repo['yufeng72.tripToSchool'].insert_many(r)
        repo['yufeng72.tripToSchool'].metadata({'complete': True})
        print(repo['yufeng72.tripToSchool'].metadata())

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

        this_script = doc.agent('alg:yufeng72#Transformation3',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        collegesUniversities = doc.entity('dat:yufeng72#collegesUniversities',
                                          {prov.model.PROV_LABEL: 'Colleges and Universities',
                                           prov.model.PROV_TYPE: 'ont:DataSet'})

        tripData = doc.entity('dat:yufeng72#tripData',
                              {prov.model.PROV_LABEL: 'Trip Data', prov.model.PROV_TYPE: 'ont:DataSet'})

        get_tripToSchool = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_tripToSchool, this_script)
        doc.used(get_tripToSchool, collegesUniversities, startTime)
        doc.used(get_tripToSchool, tripData, startTime)

        tripToSchool = doc.entity('dat:yufeng72#tripToSchool',
                                    {prov.model.PROV_LABEL: 'Count All Bike Trips to Colleges and Universities',
                                     prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(tripToSchool, this_script)
        doc.wasGeneratedBy(tripToSchool, get_tripToSchool, endTime)
        doc.wasDerivedFrom(tripToSchool, collegesUniversities, get_tripToSchool, get_tripToSchool,
                           get_tripToSchool)
        doc.wasDerivedFrom(tripToSchool, tripData, get_tripToSchool, get_tripToSchool,
                           get_tripToSchool)
        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
Transformation3.execute()
doc = Transformation3.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof
