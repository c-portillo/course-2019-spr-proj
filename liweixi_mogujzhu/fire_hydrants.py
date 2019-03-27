import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class fire_hydrants(dml.Algorithm):
    contributor = 'liweixi_mogjzhu'
    reads = []
    writes = ['liweixi_mogujzhu.fire_hydrants']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        print('Getting Boston fire hydrants...')
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')

        url = 'https://opendata.arcgis.com/datasets/1b0717d5b4654882ae36adc4a20fd64b_0.geojson'
        response = urllib.request.urlopen(url).read().decode("utf-8")

        r = json.loads(response)
        print(r["features"][0])
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("fire_hydrants")
        repo.createCollection("fire_hydrants")
        repo['liweixi_mogujzhu.fire_hydrants'].insert_many(r["features"])
        repo['liweixi_mogujzhu.fire_hydrants'].metadata({'complete': True})
        print(repo['liweixi_mogujzhu.fire_hydrants'].metadata())

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
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/fire-hydrants')

        this_script = doc.agent('alg:liweixi_mogujzhu#fire_hydrants',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:liweixi_mogujzhu#fire_hydrants',
                              {'prov:label': 'Boston Fire Hydrants', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'geojson'})
        get_fire_hydrants = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_fire_hydrants, this_script)


        fire_hydrants = doc.entity('dat:liweixi_mogujzhu#fire_hydrants',
                          {prov.model.PROV_LABEL: 'Boston Fire Hydrants', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(fire_hydrants, this_script)
        doc.wasGeneratedBy(fire_hydrants, get_fire_hydrants, endTime)
        doc.wasDerivedFrom(fire_hydrants, resource, get_fire_hydrants, get_fire_hydrants, get_fire_hydrants)
        repo.logout()

        return doc


# '''
# # This is example code you might use for debugging this module.
# # Please remove all top-level function calls before submitting.
# '''
# fire_hydrants.execute()
# doc = fire_hydrants.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
#
# ## eof