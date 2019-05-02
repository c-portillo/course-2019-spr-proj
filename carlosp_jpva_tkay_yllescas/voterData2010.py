
import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import json
import pandas as pd
from pprint import pprint

class voterData2010(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = []
    writes = ['carlosp_jpva_tkay_yllescas.voterData2010']


    @staticmethod
    def get_data():
        with open('voterData2010.json') as f:
            data = json.load(f)
            return data


    @staticmethod
    def execute(trial = False):
        print("voterData2010")
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        d_t = voterData2010


        url = "http://datamechanics.io/data/carlosp_jpva_tkay_yllescas/voterData2010.json"
        response = urllib.request.urlopen(url).read().decode("utf-8")
        d_t_json = json.loads(response)
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')


        s = json.dumps(d_t_json , sort_keys=True, indent=2)
        repo.dropCollection("voterData2010")
        repo.createCollection("voterData2010")
        repo['carlosp_jpva_tkay_yllescas.voterData2010'].insert_many(d_t_json)
        repo['carlosp_jpva_tkay_yllescas.voterData2010'].metadata({'complete':True})
        print(repo['carlosp_jpva_tkay_yllescas.voterData2010'].metadata())


        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}


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
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        #        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('bdp', 'http://datamechanics.io/data/carlosp_jpva_tkay_yllescas/voterData2010.json')

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#voterData2010',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_voterData2010 = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_voterData2010, this_script)
        doc.usage(get_voterData2010, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=voterData2010&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )
        voterData2010 = doc.entity('dat:carlosp_jpva_tkay_yllescas#voterData2010',
                                          {prov.model.PROV_LABEL: 'Voter Data 2010',
                                           prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(voterData2010, this_script)
        doc.wasGeneratedBy(voterData2010, get_voterData2010, endTime)
        doc.wasDerivedFrom(voterData2010, resource, get_voterData2010, get_voterData2010,
                           get_voterData2010)

        repo.logout()

        return doc

