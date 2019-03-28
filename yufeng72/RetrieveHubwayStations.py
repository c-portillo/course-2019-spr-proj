import csv
import io
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class RetrieveHubwayStations(dml.Algorithm):
    contributor = 'yufeng72'
    reads = []
    writes = ['yufeng72.hubwayStations']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('yufeng72', 'yufeng72')

        url = 'https://s3.amazonaws.com/hubway-data/Hubway_Stations_as_of_July_2017.csv'
        response = urllib.request.urlopen(url)
        r = csv.reader(io.StringIO(response.read().decode('utf-8')), delimiter=',')
        r_parse = []
        for row in r:
            temp = {'StationID': row[0], 'Address': row[1], 'Latitude': row[2], 'Longitude': row[3],
                    'Municipality': row[4], 'publiclyExposed': row[5], 'DockNum': row[6]}
            r_parse.append(temp)
        r_parse.remove(r_parse[0])

        repo.dropCollection("hubwayStations")
        repo.createCollection("hubwayStations")
        repo['yufeng72.hubwayStations'].insert_many(r_parse)
        repo['yufeng72.hubwayStations'].metadata({'complete': True})
        print(repo['yufeng72.hubwayStations'].metadata())

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
        doc.add_namespace('bdp', 'https://s3.amazonaws.com/hubway-data/')

        this_script = doc.agent('alg:yufeng72#RetrieveHubwayStations',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        resource = doc.entity('bdp:Hubway_Stations_as_of_July_2017',
                              {'prov:label': 'Hubway Stations', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})

        get_hubwayStations = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_hubwayStations, this_script)
        doc.usage(get_hubwayStations, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'select=StationID,Address,Latitude,Longitude,Municipality,publiclyExposed,DockNum'
                   }
                  )

        hubwayStations = doc.entity('dat:yufeng72#hubwayStations',
                          {prov.model.PROV_LABEL: 'Hubway Stations', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(hubwayStations, this_script)
        doc.wasGeneratedBy(hubwayStations, get_hubwayStations, endTime)
        doc.wasDerivedFrom(hubwayStations, resource, get_hubwayStations, get_hubwayStations, get_hubwayStations)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
RetrieveHubwayStations.execute()
doc = RetrieveHubwayStations.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
