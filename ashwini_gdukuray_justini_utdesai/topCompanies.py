import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class topCompanies(dml.Algorithm):
    contributor = 'ashwini_gdukuray_justini_utdesai'
    reads = []
    writes = ['ashwini_gdukuray_justini_utdesai.topCompanies']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')

        url = 'http://datamechanics.io/data/ashwini_gdukuray_justini_utdesai/Top25Companies.csv'

        data = pd.read_csv(url)

        #print(data)

        #records = json.loads(data.T.to_json()).values()

        repo.dropCollection("topCompanies")
        repo.createCollection("topCompanies")
        repo['ashwini_gdukuray_justini_utdesai.topCompanies'].insert_many(data.to_dict('records'))
        repo['ashwini_gdukuray_justini_utdesai.topCompanies'].metadata({'complete': True})
        print(repo['ashwini_gdukuray_justini_utdesai.topCompanies'].metadata())

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
        doc.add_namespace('alg', 'ashwini_gdukuray_justini_utdesai#topcompanies')  # The scripts are in <folder>#<filename> format.

        #input DataSet
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://datamechanics.io/?prefix=ashwini_gdukuray_justini_utdesai/')

        this_script = doc.agent('alg:ashwini_gdukuray_justini_utdesai#topCompanies',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        topCompaniesPre = doc.entity('bdp:Top25Companies.csv',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        topCompaniesPost = doc.entity('dat:ashwini_gdukuray_justini_utdesai#topCompanies',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        act = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(act, this_script)
        doc.usage(act, topCompaniesPre, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'
                   }
                  )

        doc.wasAttributedTo(topCompaniesPre, this_script)
        doc.wasGeneratedBy(topCompaniesPost, act, endTime)
        doc.wasDerivedFrom(topCompaniesPost, topCompaniesPre, act, act, act)


        repo.logout()

        return doc



# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
'''
topCompanies.execute()
doc = topCompanies.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

'''
## eof
