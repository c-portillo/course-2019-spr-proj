import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import requests

class mbta_stops(dml.Algorithm):
    contributor = 'zui_sarms'
    reads = []
    writes = ['zui_sarms.mbta_stops']

    @staticmethod
    def execute(trial=False):
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zui_sarms', 'zui_sarms')

        url = 'https://api-v3.mbta.com/stops'
        response = requests.request('GET', url)
        r = response.json()
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("mbta_stops")
        repo.createCollection("mbta_stops")
        repo['zui_sarms.mbta_stops'].insert_many(r["data"])
        repo['zui_sarms.mbta_stops'].metadata({'complete':True})
        print(repo['zui_sarms.mbta_stops'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zui_sarms', 'zui_sarms')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:zui_sarms#mbta_stops', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:MBTA BOSTON', {'prov:label': '200, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_stops = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_stops, this_script)
        doc.usage(get_stops, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'
                   }
                  )

        mbta_stops = doc.entity('dat:zui_sarms#mbta_stops', {prov.model.PROV_LABEL: 'MBTA Stops', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(mbta_stops, this_script)
        doc.wasGeneratedBy(mbta_stops, get_stops, endTime)
        doc.wasDerivedFrom(mbta_stops, resource, get_stops, get_stops, get_stops)

        repo.logout()

        return doc

## eof