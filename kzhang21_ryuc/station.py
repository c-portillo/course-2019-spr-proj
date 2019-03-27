import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd
from ast import literal_eval as make_tuple


class station(dml.Algorithm):
    contributor = 'kzhang21_ryuc'
    reads = []
    writes = ['kzhang21_ryuc.station']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')

        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/e5a0066d38ac4e2abbc7918197a4f6af_6.csv'
        response = pd.read_csv(url, header=0)

        # select relevant columnns
        data_stations = response[['NAME', 'NEIGHBORHOOD', 'ZIP']].copy()

        # rename to appropriate names
        data_stations.columns = ['District', 'Neighborhood', 'Zip']

        # eliminate null districts
        data_stations.dropna(inplace=True)

        # response = urllib.request.urlopen(url).read().decode("utf-8")
        # r = json.loads(response)
        r = json.loads(data_stations.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)

        repo.dropCollection("station")
        repo.createCollection("station")
        repo['kzhang21_ryuc.station'].insert_many(r)
        repo['kzhang21_ryuc.station'].metadata({'complete': True})
        print(repo['kzhang21_ryuc.station'].metadata())

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
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        # additional resource
        doc.add_namespace('station',
                          'http://bostonopendata-boston.opendata.arcgis.com/datasets/e5a0066d38ac4e2abbc7918197a4f6af_6.csv')

        this_script = doc.agent('alg:kzhang21_ryuc#station',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:station',
                              {'prov:label': 'Station, Station List', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})

        get_station = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_station, this_script)
        doc.usage(get_station, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  }
                  )

        station = doc.entity('dat:kzhang21_ryuc#station', {prov.model.PROV_LABEL:'Station District', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(station, this_script)
        doc.wasGeneratedBy(station, get_station, endTime)
        doc.wasDerivedFrom(station, resource, get_station, get_station, get_station)

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
# Station.execute()
# doc = Station.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
