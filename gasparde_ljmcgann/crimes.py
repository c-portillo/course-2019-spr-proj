import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class crimes(dml.Algorithm):
    contributor = 'gasparde_ljmcgann'
    reads = []
    writes = ['gasparde_ljmcgann.crimes']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('gasparde_ljmcgann', 'gasparde_ljmcgann')

        # # Getting crime data from boston.gov
        url = 'https://data.boston.gov/datastore/odata3.0/12cb3883-56f5-47de-afa5-3b1cf61b257b?$format=json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        # print(s)
        repo.dropCollection("crimes")
        repo.createCollection("crimes")
        repo['gasparde_ljmcgann.crimes'].insert_many(r["value"])
        repo['gasparde_ljmcgann.crimes'].metadata({'complete': True})
        print(repo['gasparde_ljmcgann.crimes'].metadata())

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
        doc.add_namespace('bdp', 'https://data.boston.gov/datastore/odata3.0/')

        this_script = doc.agent('alg:gasparde_ljmcgann#crimes',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': 'CRIME INCIDENT REPORTS', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_crimes = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_crimes, this_script)

        doc.usage(get_crimes, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?$format=json'
                   }
                  )

        crimes = doc.entity('dat:gasparde_ljmcgann#found',
                           {prov.model.PROV_LABEL: 'Crime reports in Boston', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(crimes, this_script)
        doc.wasGeneratedBy(crimes, get_crimes, endTime)
        doc.wasDerivedFrom(crimes, resource, get_crimes, get_crimes, get_crimes)

        repo.logout()

        return doc

"""
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
if __name__ == '__main__':
    crimes.execute()
    doc = crimes.provenance()
    print(doc.get_provn())
    print(json.dumps(json.loads(doc.serialize()), indent=4))
"""
## eof