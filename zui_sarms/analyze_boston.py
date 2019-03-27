import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class analyze_boston(dml.Algorithm):
    contributor = 'zui_sarms'
    reads = []
    writes = ['zui_sarms.landmarks', 'zui_sarms.parks']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zui_sarms', 'zui_sarms')

        url = 'http://datamechanics.io/data/landmarks.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("landmarks")
        repo.createCollection("landmarks")
        repo['zui_sarms.landmarks'].insert_many(r)
        repo['zui_sarms.landmarks'].metadata({'complete': True})
        print(repo['zui_sarms.landmarks'].metadata())

        url = 'http://datamechanics.io/data/parks.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("parks")
        repo.createCollection("parks")
        repo['zui_sarms.parks'].insert_many(r)
        repo['zui_sarms.parks'].metadata({'complete': True})
        print(repo['zui_sarms.parks'].metadata())

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

        this_script = doc.agent('alg:zui_sarms#analyze_boston', {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:Analyze Boston',{'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'json'})
        get_landmarks = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_parks = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_landmarks, this_script)
        doc.wasAssociatedWith(get_parks, this_script)
        doc.usage(get_parks, resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval'})
        doc.usage(get_landmarks, resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Retrieval'})

        parks = doc.entity('dat:zui_sarms#parks', {prov.model.PROV_LABEL: 'Open Space', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(parks, this_script)
        doc.wasGeneratedBy(parks, get_parks, endTime)
        doc.wasDerivedFrom(parks, resource, get_parks, get_parks, get_parks)

        landmarks = doc.entity('dat:zui_sarms#landmarks', {prov.model.PROV_LABEL: 'Boston Landmarks', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(landmarks, this_script)
        doc.wasGeneratedBy(landmarks, get_landmarks, endTime)
        doc.wasDerivedFrom(landmarks, resource, get_landmarks, get_landmarks, get_landmarks)

        repo.logout()

        return doc

## eof