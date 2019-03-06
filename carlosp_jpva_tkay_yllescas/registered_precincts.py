import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class registered_precincts(dml.Algorithm):
    contributor = 'carlosp_jpva_tkay_yllescas'
    reads = []
    writes = ['carlosp_jpva_tkay_yllescas.registered_precincts']

    @staticmethod
    def execute(trial=False):
        print("registered_precincts")
        '''Retrieve some data sets (without API).'''
        startTime = datetime.datetime.now()

        # Set up the database connection
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('carlosp_jpva_tkay_yllescas', 'carlosp_jpva_tkay_yllescas')

        file = 'data/registered_voters_Precinct.json'
        with open(file, "r", encoding="utf8") as datafile:
            json_string = datafile.read()
        r = json.loads(json_string)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("registered_precincts")
        repo.createCollection("registered_precincts")
        repo['carlosp_jpva_tkay_yllescas.registered_precincts'].insert_many(r)
        repo['carlosp_jpva_tkay_yllescas.registered_precincts'].metadata({'complete': True})
        print(repo['carlosp_jpva_tkay_yllescas.registered_precincts'].metadata())

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

        this_script = doc.agent('alg:carlosp_jpva_tkay_yllescas#registered_precincts',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_registered_precincts = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_registered_precincts, this_script)
        doc.usage(get_registered_precincts, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?type=registered_precincts&$select=type,latitude,longitude,OPEN_DT'
                   }
                  )

        registeredPrecincts = doc.entity('dat:carlosp_jpva_tkay_yllescas#registered_precincts',
                                {prov.model.PROV_LABEL: 'Registered Voters by Precinct', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(registeredPrecincts, this_script)
        doc.wasGeneratedBy(registeredPrecincts, get_registered_precincts, endTime)
        doc.wasDerivedFrom(registeredPrecincts, resource, get_registered_precincts, get_registered_precincts, get_registered_precincts)

        repo.logout()

        return doc

#registered_precincts.execute()

'''
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof