# writes to database
# congressional districts
# not using

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class non_registered_cd(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = []
    writes = ['carlosp_jpva_tkay_yllescas.non_registered_cd']

    @staticmethod
    def execute(trial=False):
        print("non_registered_cd")
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        file = 'data/non_registered_CD.json'
        with open(file, "r", encoding="utf8") as datafile:
            json_string = datafile.read()
        r = json.loads(json_string)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("non_registered_cd")
        repo.createCollection("non_registered_cd")
        repo['carlosp_jpva_tkay_yllescas.non_registered_cd'].insert_many(r)
        repo['carlosp_jpva_tkay_yllescas.non_registered_cd'].metadata({'complete': True})
        print(repo['carlosp_jpva_tkay_yllescas.non_registered_cd'].metadata())

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
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#non_registered_cd',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_non_registered_cd = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_non_registered_cd, this_script)
        doc.usage(get_non_registered_cd, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=non_registered_cd&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )

        non_registeredCD = doc.entity('dat:carlosp_jpva_tkay_yllescas#registered_cd',
                                {prov.model.PROV_LABEL: 'Registered Voters by CD', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(non_registeredCD, this_script)
        doc.wasGeneratedBy(non_registeredCD, get_non_registered_cd, endTime)
        doc.wasDerivedFrom(non_registeredCD, resource, get_non_registered_cd, get_non_registered_cd, get_non_registered_cd)

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
