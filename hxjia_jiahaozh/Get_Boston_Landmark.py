import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class Get_Boston_Landmark(dml.Algorithm):
    contributor = 'hxjia_jiahaozh'
    reads = []
    writes = ['hxjia_jiahaozh.Boston_Landmarks']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')

        url = "http://bostonopendata-boston.opendata.arcgis.com/datasets/7a7aca614ad740e99b060e0ee787a228_3.csv"
#        response = urllib.request.urlopen(url).read().decode("utf-8")
        bl = pd.read_csv(url)
        new_bl = pd.DataFrame(
            {'Name': bl['Name_of_Pr'],
             'Address': bl['Address'],
             'Neighborhood': bl['Neighborho']
             })
        r = json.loads(new_bl.to_json(orient='records'))
        #s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("Boston_Landmarks")
        repo.createCollection("Boston_Landmarks")
        repo['hxjia_jiahaozh.Boston_Landmarks'].insert_many(r)
        repo['hxjia_jiahaozh.Boston_Landmarks'].metadata({'complete': True})
        print(repo['hxjia_jiahaozh.Boston_Landmarks'].metadata())

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
        repo.authenticate('hxjia_jiahaozh', 'hxjia_jiahaozh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/hxjia_jiahaozh/bostonlandmark')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/hxjia_jiahaozh/landmark')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:hxjia_jiahaozh#get_boston_landmark',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:7a7aca614ad740e99b060e0ee787a228_3',
                              {'prov:label': 'Boston_Landmarks, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_landmarks = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_landmarks, this_script)
        doc.usage(get_landmarks, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Boston+Landmarks&$select=Name,Address,Neighborhood'
                   }
                  )

        landmarks = doc.entity('dat:hxjia_jiahaozh#landmarks',
                          {prov.model.PROV_LABEL: 'Boston Landmarks', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(landmarks, this_script)
        doc.wasGeneratedBy(landmarks, get_landmarks, endTime)
        doc.wasDerivedFrom(landmarks, resource, get_landmarks, get_landmarks, get_landmarks)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# Get_Boston_Landmark.execute()
# doc = Boston_Landmarks.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
