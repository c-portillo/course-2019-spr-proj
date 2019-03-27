import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class secretaryCommonwealth(dml.Algorithm):
    contributor = 'ashwini_gdukuray_justini_utdesai'
    reads = []
    writes = ['ashwini_gdukuray_justini_utdesai.secretary']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')

        url = 'https://cs-people.bu.edu/dharmesh/spark/businesses.csv'

        data = pd.read_csv(url)

        # Standardize dataset
        data = data.rename(index=str, columns={"SDO Cert. Date": "SDO Cert Date"})

        #records = json.loads(data.T.to_json()).values()

        repo.dropCollection("secretary")
        repo.createCollection("secretary")
        repo['ashwini_gdukuray_justini_utdesai.secretary'].insert(data.to_dict('records'))
        repo['ashwini_gdukuray_justini_utdesai.secretary'].metadata({'complete': True})
        print(repo['ashwini_gdukuray_justini_utdesai.secretary'].metadata())

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
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://cs-people.bu.edu/dharmesh/spark/')

        this_script = doc.agent('alg:ashwini_gdukuray_justini_utdesai#secretaryCommonwealth',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:#businesses.csv',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        resource2 = doc.entity('dat:ashwini_gdukuray_justini_utdesai#secretary',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        act = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(resource2, this_script)
        doc.usage(act, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )

        doc.wasAttributedTo(resource, this_script)
        doc.wasGeneratedBy(resource2, act, endTime)
        doc.wasDerivedFrom(resource2, resource, act, act, act)


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

## eof
