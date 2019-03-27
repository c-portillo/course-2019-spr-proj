import json
import dml
import prov.model
import datetime
import pandas as pd
import uuid


class industryTotal(dml.Algorithm):
    contributor = 'ashwini_gdukuray_justini_utdesai'
    reads = ['ashwini_gdukuray_justini_utdesai.masterList']
    writes = ['ashwini_gdukuray_justini_utdesai.industryTotal']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ashwini_gdukuray_justini_utdesai', 'ashwini_gdukuray_justini_utdesai')

        masterList = repo['ashwini_gdukuray_justini_utdesai.masterList']

        masterListDF = pd.DataFrame(list(masterList.find()))

        # build sum of each industry
        data = {}
        for index, row in masterListDF.iterrows():
            industry = row['Description of Services']
            if (industry in data):
                data[industry] += 1
            else:
                data[industry] = 1

        listOfIndustries = list(data)
        listOfTuples = []
        for ind in listOfIndustries:
            listOfTuples.append((ind, data[ind]))

        industryDF = pd.DataFrame(listOfTuples, columns = ['Industry', 'Number of Businesses'])

        industryDF = industryDF.sort_values(by=['Number of Businesses'], ascending=False)

        #print(industryDF)

        #records = json.loads(industryDF.T.to_json()).values()

        repo.dropCollection("industryTotal")
        repo.createCollection("industryTotal")
        repo['ashwini_gdukuray_justini_utdesai.industryTotal'].insert_many(industryDF.to_dict('records'))
        repo['ashwini_gdukuray_justini_utdesai.industryTotal'].metadata({'complete': True})
        print(repo['ashwini_gdukuray_justini_utdesai.industryTotal'].metadata())

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

        this_script = doc.agent('alg:ashwini_gdukuray_justini_utdesai#industryTotal',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        masterList = doc.entity('dat:ashwini_gdukuray_justini_utdesai#masterList',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataSet',
                               'ont:Extension': 'json'})
        industryTotal = doc.entity('dat:ashwini_gdukuray_justini_utdesai#industryTotal',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataSet',
                               'ont:Extension': 'json'})
        act = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(act, this_script)
        doc.usage(act, masterList, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=Animal+Found&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )

        doc.wasAttributedTo(industryTotal, this_script)
        doc.wasGeneratedBy(industryTotal, act, endTime)
        doc.wasDerivedFrom(industryTotal, masterList, act, act, act)

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
