import json
import pandas as pd
import dml
import prov.model
import datetime
import pandas as pd
import uuid

class massHousingData(dml.Algorithm):
    contributor = 'ashwini_gdukuray_justini_utdesai'
    reads = []
    writes = ['ashwini_gdukuray_justini_utdesai.massHousing']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''

        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')

        #url = 'https://www.masshousing.com/portal/server.pt/gateway/PTARGS_0_2_2662_236_0_43/http%3B/MHWEBAPP03.mhdom.com/MWBE_WebFrontEnd/Common/Download/Excel/xlbe1493710218.xls'
        url = 'http://datamechanics.io/data/ashwini_gdukuray_justini_utdesai/massHousing.csv'

        data = pd.read_csv(url)

        #records = json.loads(data.T.to_json()).values()

        repo.dropCollection("massHousing")
        repo.createCollection("massHousing")
        repo['ashwini_gdukuray_justini_utdesai.massHousing'].insert_many(data.to_dict('records'))
        repo['ashwini_gdukuray_justini_utdesai.massHousing'].metadata({'complete': True})
        print(repo['ashwini_gdukuray_justini_utdesai.massHousing'].metadata())

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
        doc.add_namespace('bdp', 'http://datamechanics.io/?prefix=ashwini_gdukuray_justini_utdesai/')

        this_script = doc.agent('alg:ashwini_gdukuray_justini_utdesai#massHousingData',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        massHousingPre = doc.entity('bdp:massHousing.csv',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'xlsx'})
        massHousingPost = doc.entity('dat:ashwini_gdukuray_justini_utdesai#massHousing',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        act = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(act, this_script)
        doc.usage(act, massHousingPre, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   }
                  )

        doc.wasAttributedTo(massHousingPre, this_script)
        doc.wasGeneratedBy(massHousingPost, act, endTime)
        doc.wasDerivedFrom(massHousingPost, massHousingPre, act, act, act)


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
