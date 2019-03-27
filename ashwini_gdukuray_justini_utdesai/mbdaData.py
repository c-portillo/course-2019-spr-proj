import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class mbdaData(dml.Algorithm):
    contributor = 'ashwini_gdukuray_justini_utdesai'
    reads = []
    writes = ['ashwini_gdukuray_justini_utdesai.mbdaData']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')

        urlNumFirms =     'https://www.mbda.gov/csv_data_export?year=2012&industry=All%20Sectors%20%280%29&minority_group=Total%20Minority&metrics=Actual%20Value&concept=Number%20of%20Firms&firms=All%20Firms'
        urlNumEmployees = 'https://www.mbda.gov/csv_data_export?year=2012&industry=All%20Sectors%20%280%29&minority_group=Total%20Minority&metrics=Actual%20Value&concept=Number%20of%20Paid%20Employees&firms=All%20Firms'

        numFirmsDF = pd.read_csv(urlNumFirms, skiprows=[0,1,2])
        numEmployeesDF = pd.read_csv(urlNumEmployees, skiprows=[0,1,2])

        numFirmsDF = numFirmsDF.rename(index=str, columns={'Value': 'Number of Firms'})
        numEmployeesDF = numEmployeesDF.rename(index=str, columns={'Value': 'Number of Employees'})

        mbdaDF = pd.merge(numFirmsDF, numEmployeesDF, how='inner', on=['State/US'])

        #print(mbdaDF)

        #records = json.loads(mbdaDF.T.to_json()).values()

        repo.dropCollection("mbdaData")
        repo.createCollection("mbdaData")
        repo['ashwini_gdukuray_justini_utdesai.mbdaData'].insert_many(mbdaDF.to_dict('records'))
        repo['ashwini_gdukuray_justini_utdesai.mbdaData'].metadata({'complete': True})
        print(repo['ashwini_gdukuray_justini_utdesai.mbdaData'].metadata())

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

        pass

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://www.mbda.gov/')

        this_script = doc.agent('alg:ashwini_gdukuray_justini_utdesai#mbdaData',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        numFirms = doc.entity('bdp:ashwini_gdukuray_justini_utdesai#numFirmsDF',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        numEmployees = doc.entity('bdp:ashwini_gdukuray_justini_utdesai#numEmployeesDF',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        mbda = doc.entity('dat:ashwini_gdukuray_justini_utdesai#mbdaData',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        act = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(act, this_script)
        doc.usage(act, numFirms, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )
        doc.usage(act, numEmployees, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )

        doc.wasAttributedTo(mbda, this_script)
        doc.wasGeneratedBy(mbda, act, endTime)
        doc.wasDerivedFrom(mbda, numFirms, act, act, act)
        doc.wasDerivedFrom(mbda, numEmployees, act, act, act)

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
