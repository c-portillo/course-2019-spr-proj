import json
import dml
import prov.model
import datetime
import uuid


class Transformation1(dml.Algorithm):
    contributor = 'yufeng72'
    reads = ['yufeng72.busStops','yufeng72.collegeUniversities']
    writes = ['yufeng72.possiblePlaces']

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

        busStops = getCollection('busStops')
        busStopsNew = []
        for row in busStops:
            if ('BOSTON' in row['TOWN']) and (row['latitude'] is not None) and (row['longitude'] is not None):
                newRow = {'Name': row['STOP_NAME'], 'Type': 'Bus Stop', 'Latitude': row['latitude'],
                          'Longitude': row['longitude']}
                busStopsNew.append(newRow)

        collegesUniversities = getCollection('collegesUniversities')
        collegesUniversitiesNew = []
        for row in collegesUniversities:
            if (row['Latitude'] is not None) and (row['Longitude'] is not None):
                newRow = {'Name': row['Name'], 'Type': 'College&University', 'Latitude': row['Latitude'],
                          'Longitude': row['Longitude']}
                collegesUniversitiesNew.append(newRow)

        def union(R, S):
            return R + S

        r = union(busStopsNew, collegesUniversitiesNew)

        repo.dropCollection('possiblePlaces')
        repo.createCollection('possiblePlaces')
        repo['yufeng72.possiblePlaces'].insert_many(r)
        repo['yufeng72.possiblePlaces'].metadata({'complete': True})
        print(repo['yufeng72.possiblePlaces'].metadata())

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

        this_script = doc.agent('alg:yufeng72#Transformation1',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        busStops = doc.entity('dat:yufeng72#busStops',
                              {prov.model.PROV_LABEL: 'Bus Stops', prov.model.PROV_TYPE: 'ont:DataSet'})

        collegesUniversities = doc.entity('dat:yufeng72#collegesUniversities',
                                          {prov.model.PROV_LABEL: 'Colleges and Universities',
                                           prov.model.PROV_TYPE: 'ont:DataSet'})

        get_possiblePlaces = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_possiblePlaces, this_script)
        doc.used(get_possiblePlaces, busStops, startTime)
        doc.used(get_possiblePlaces, collegesUniversities, startTime)

        possiblePlaces = doc.entity('dat:yufeng72#possiblePlaces',
                                    {prov.model.PROV_LABEL: 'Possible Places for Bikes',
                                     prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(possiblePlaces, this_script)
        doc.wasGeneratedBy(possiblePlaces, get_possiblePlaces, endTime)
        doc.wasDerivedFrom(possiblePlaces, busStops, get_possiblePlaces, get_possiblePlaces, get_possiblePlaces)
        doc.wasDerivedFrom(possiblePlaces, collegesUniversities, get_possiblePlaces, get_possiblePlaces,
                           get_possiblePlaces)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
Transformation1.execute()
doc = Transformation1.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
