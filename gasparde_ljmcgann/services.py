import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class services(dml.Algorithm):
    contributor = 'gasparde_ljmcgann'
    reads = []
    writes = ['gasparde_ljmcgann.lost', 'gasparde_ljmcgann.found']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('gasparde_ljmcgann', 'gasparde_ljmcgann')

        # # 311 SERVICE REQUESTS
        url = 'https://data.boston.gov/datastore/odata3.0/2968e2c0-d479-49ba-a884-4ef523ada3c0?$format=json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        # print(s)
        repo.dropCollection("services")
        repo.createCollection("services")
        repo['gasparde_ljmcgann.services'].insert_many(r["value"])
        repo['gasparde_ljmcgann.services'].metadata({'complete': True})
        print(repo['gasparde_ljmcgann.services'].metadata())

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
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:gasparde_ljmcgann#services',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_services = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_services, this_script)
        doc.wasAssociatedWith(get_services, this_script)
        doc.usage(get_services, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?$format=json'
                   }
                  )

        services = doc.entity('dat:gasparde_ljmcgann#services',
                              {prov.model.PROV_LABEL: 'Service Request in Boston', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(services, this_script)
        doc.wasGeneratedBy(services, get_services, endTime)
        doc.wasDerivedFrom(services, resource, get_services, get_services, get_services)

        repo.logout()

        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
if __name__ == '__main__':
    services.execute()
    doc = services.provenance()
    print(doc.get_provn())
    print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
