import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class health(dml.Algorithm):
    contributor = 'gasparde_ljmcgann'
    reads = []
    writes = ['gasparde_ljmcgann.health']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('gasparde_ljmcgann', 'gasparde_ljmcgann')

        # # 500 Cities: Local Data for Better Health, 2018 release
        url = 'https://chronicdata.cdc.gov/resource/csmm-fdhi.geojson'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        # print(s)
        repo.dropCollection("health")
        repo.createCollection("health")
        repo['gasparde_ljmcgann.health'].insert_one(r)
        repo['gasparde_ljmcgann.health'].metadata({'complete': True})
        print(repo['gasparde_ljmcgann.health'].metadata())

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
        repo.authenticate('gasparde_ljmcgann', 'gasparde_ljmcgann')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://chronicdata.cdc.gov/resource/')

        this_script = doc.agent('alg:gasparde_ljmcgann#health',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '500 Cities: Local Data for Better Health, 2018 release', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'geojson'})
        get_health = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_health, this_script)

        doc.usage(get_health, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   }
                  )

        health = doc.entity('dat:gasparde_ljmcgann#health',
                                   {prov.model.PROV_LABEL: '500 Cities: Local Data for Better Health, 2018 release ',
                                    prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(health, this_script)
        doc.wasGeneratedBy(health, get_health, endTime)
        doc.wasDerivedFrom(health, resource, get_health, get_health, get_health)

        repo.logout()

        return doc

"""
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
if __name__ == '__main__':
    health.execute()
    doc = health.provenance()
    print(doc.get_provn())
    print(json.dumps(json.loads(doc.serialize()), indent=4))
"""
## eof