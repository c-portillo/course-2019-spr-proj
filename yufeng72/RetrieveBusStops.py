import csv
import io
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class RetrieveBusStops(dml.Algorithm):
    contributor = 'yufeng72'
    reads = []
    writes = ['yufeng72.busStops']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('yufeng72', 'yufeng72')

        url = 'http://datamechanics.io/data/yufeng72/Bus_Stops.csv'
        response = urllib.request.urlopen(url)
        r = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter=',')
        r_parse = []
        for row in r:
            temp = {'latitude': row[0], 'longitude': row[1], 'geometry': row[3], 'OBJECTID': row[4], 'STOP_ID': row[5],
                    'STOP_NAME': row[6], 'TOWN': row[7], 'TOWN_ID': row[8]}
            r_parse.append(temp)
        r_parse.remove(r_parse[0])

        repo.dropCollection("busStops")
        repo.createCollection("busStops")
        repo['yufeng72.busStops'].insert_many(r_parse)
        repo['yufeng72.busStops'].metadata({'complete': True})
        print(repo['yufeng72.busStops'].metadata())

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

        this_script = doc.agent('alg:yufeng72#RetrieveBusStops',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource = doc.entity('bdp:Bus_Stops',
                              {'prov:label': 'Bus Stops', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})

        get_busStops = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_busStops, this_script)
        doc.usage(get_busStops, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'select=latitude,longitude,OBJECTID,STOP_ID,STOP_NAME,TOWN,TOWN_ID'
                   }
                  )

        busStops = doc.entity('dat:yufeng72#busStops',
                          {prov.model.PROV_LABEL: 'Bus Stops', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(busStops, this_script)
        doc.wasGeneratedBy(busStops, get_busStops, endTime)
        doc.wasDerivedFrom(busStops, resource, get_busStops, get_busStops, get_busStops)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
RetrieveBusStops.execute()
doc = RetrieveBusStops.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
