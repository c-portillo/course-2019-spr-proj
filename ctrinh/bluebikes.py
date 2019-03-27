import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class bluebikes(dml.Algorithm):
    contributor = 'ctrinh'
    reads = []
    writes = ['ctrinh.bluebikes']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ctrinh', 'ctrinh')

        url1 = 'http://datamechanics.io/data/bluebikes-2018-01.csv'
        df1 = pd.read_csv(url1)

        url2 = 'http://datamechanics.io/data/bluebikes-2018-02.csv'
        df2 = pd.read_csv(url2)

        url3 = 'http://datamechanics.io/data/bluebikes-2018-03.csv'
        df3 = pd.read_csv(url3)

        url4 = 'http://datamechanics.io/data/bluebikes-2018-04.csv'
        df4 = pd.read_csv(url4)

        url5 = 'http://datamechanics.io/data/bluebikes-2018-05.csv'
        df5 = pd.read_csv(url5)

        url6 = 'http://datamechanics.io/data/bluebikes-2018-06.csv'
        df6 = pd.read_csv(url6)

        url7 = 'http://datamechanics.io/data/bluebikes-2018-07.csv'
        df7 = pd.read_csv(url7)

        url8 = 'http://datamechanics.io/data/bluebikes-2018-08.csv'
        df8 = pd.read_csv(url8)

        url9 = 'http://datamechanics.io/data/bluebikes-2018-09.csv'
        df9 = pd.read_csv(url9)

        url10 = 'http://datamechanics.io/data/bluebikes-2018-10.csv'
        df10 = pd.read_csv(url10)

        url11 = 'http://datamechanics.io/data/bluebikes-2018-11.csv'
        df11 = pd.read_csv(url11)

        url12 = 'http://datamechanics.io/data/bluebikes-2018-12.csv'
        df12 = pd.read_csv(url12)

        df1.append(df2)
        df1.append(df3)
        df1.append(df4)
        df1.append(df5)
        df1.append(df6)
        df1.append(df7)
        df1.append(df8)
        df1.append(df9)
        df1.append(df10)
        df1.append(df11)
        df1.append(df12)

        df = df1.filter(['tripduration', 'starttime', 'stoptime'])
        r = df.to_dict(orient='records')

        repo.dropCollection("bluebikes")
        repo.createCollection("bluebikes")
        repo['ctrinh.bluebikes'].insert_many(r)
        repo['ctrinh.bluebikes'].metadata({'complete':True})
        print(repo['ctrinh.bluebikes'].metadata())

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('ctrinh', 'ctrinh')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('dmc', 'http://datamechanics.io/data/')

        this_script = doc.agent('alg:ctrinh#bluebikes', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dmc:bluebikes-2018-$.csv', {'prov:label':'Bluebikes Trip History', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        get_bluebikes = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_bluebikes, this_script)
        doc.usage(get_bluebikes, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'}
                  )

        bluebikes = doc.entity('dat:ctrinh#bluebikes', {prov.model.PROV_LABEL:'Bluebikes Trip Duration', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(bluebikes, this_script)
        doc.wasGeneratedBy(bluebikes, get_bluebikes, endTime)
        doc.wasDerivedFrom(bluebikes, resource, get_bluebikes, get_bluebikes, get_bluebikes)

        repo.logout()

        return doc

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
bluebikes.execute()
doc = bluebikes.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof
