import csv
import io
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class RetrieveTripData(dml.Algorithm):
    contributor = 'yufeng72'
    reads = []
    writes = ['yufeng72.tripData']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('yufeng72', 'yufeng72')

        url = 'http://datamechanics.io/data/yufeng72/Bluebikes_Tripdata_201809.csv'
        response = urllib.request.urlopen(url)
        r = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter=',')
        r_parse = []
        for row in r:
            temp = {'tripduration': row[0], 'starttime': row[1], 'stoptime': row[2], 'start station id': row[3],
                    'start station name': row[4], 'start station latitude': row[5], 'start station longitude': row[6],
                    'end station id': row[7], 'end station name': row[8], 'end station latitude': row[9],
                    'end station longitude': row[10], 'bikeid': row[11], 'usertype': row[12], 'birth year': row[13],
                    'gender': row[14]}
            r_parse.append(temp)
        r_parse.remove(r_parse[0])

        repo.dropCollection("tripData")
        repo.createCollection("tripData")
        repo['yufeng72.tripData'].insert_many(r_parse)
        repo['yufeng72.tripData'].metadata({'complete': True})
        print(repo['yufeng72.tripData'].metadata())

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
        doc.add_namespace('bdp', 'http://datamechanics.io/data/yufeng72/')

        this_script = doc.agent('alg:yufeng72#RetrieveTripData',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource = doc.entity('bdp:Bluebikes_Tripdata_201809',
                              {'prov:label': 'Trip Data', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})

        get_tripData = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_tripData, this_script)
        doc.usage(get_tripData, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'select=tripduration,starttime,stoptime,start station id,end station id,bikeid,...'
                   }
                  )

        tripData = doc.entity('dat:yufeng72#tripData',
                          {prov.model.PROV_LABEL: 'Trip Data', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(tripData, this_script)
        doc.wasGeneratedBy(tripData, get_tripData, endTime)
        doc.wasDerivedFrom(tripData, resource, get_tripData, get_tripData, get_tripData)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
RetrieveTripData.execute()
doc = RetrieveTripData.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
