import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class neighborhoods(dml.Algorithm):
    contributor = 'gasparde_ljmcgann'
    reads = []
    writes = ['gasparde_ljmcgann.neighborhoods']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('gasparde_ljmcgann', 'gasparde_ljmcgann')

        # # BOSTON NEIGHBORHOODS data
        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/3525b0ee6e6b427f9aab5d0a1d0a1a28_0.geojson'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        # print(s)
        repo.dropCollection("neighborhoods")
        repo.createCollection("neighborhoods")
        repo['gasparde_ljmcgann.neighborhoods'].insert_one(r)
        repo['gasparde_ljmcgann.neighborhoods'].metadata({'complete': True})
        print(repo['gasparde_ljmcgann.neighborhoods'].metadata())

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
        doc.add_namespace('bdp', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:gasparde_ljmcgann#neighborhoods',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': 'Boston Neighborhoods', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'geojson'})
        get_neighborhoods= doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_neighborhoods, this_script)

        doc.usage(get_neighborhoods, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': '?$format=geojson'
                   }
                  )

        neighborhoods = doc.entity('dat:gasparde_ljmcgann#neighborhoods',
                            {prov.model.PROV_LABEL: 'Crime reports in Boston', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(neighborhoods, this_script)
        doc.wasGeneratedBy(neighborhoods, get_neighborhoods, endTime)
        doc.wasDerivedFrom(neighborhoods, resource, get_neighborhoods, get_neighborhoods, get_neighborhoods)

        repo.logout()

        return doc

"""
# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
if __name__ == '__main__':
    neighborhoods.execute()
    doc = neighborhoods.provenance()
    print(doc.get_provn())
    print(json.dumps(json.loads(doc.serialize()), indent=4))
"""
## eof