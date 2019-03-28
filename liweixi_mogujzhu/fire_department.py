import urllib.request
import json
import dml
import prov.model
import datetime
import uuid


class fire_department(dml.Algorithm):
    contributor = 'liweixi_mogjzhu'
    reads = []
    writes = ['liweixi_mogujzhu.fire_department']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        print("Get Boston fire department...")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')

        url = 'https://opendata.arcgis.com/datasets/092857c15cbb49e8b214ca5e228317a1_2.geojson'
        response = urllib.request.urlopen(url).read().decode("utf-8")

        r = json.loads(response)
        print(r["features"][0])
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("fire_department")
        repo.createCollection("fire_department")
        repo['liweixi_mogujzhu.fire_department'].insert_many(r['features'])
        repo['liweixi_mogujzhu.fire_department'].metadata({'complete': True})
        print(repo['liweixi_mogujzhu.fire_department'].metadata())

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
        doc.add_namespace('bdp', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/fire-departments')

        this_script = doc.agent('alg:liweixi_mogujzhu#fire_department',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:liweixi_mogujzhu#fire_department',
                              {'prov:label': 'Boston Fire Department', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'geojson'})
        get_fire_department = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_fire_department, this_script)

        fire_department = doc.entity('dat:liweixi_mogujzhu#fire_department',
                          {prov.model.PROV_LABEL: 'Boston Fire Department', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(fire_department, this_script)
        doc.wasGeneratedBy(fire_department, get_fire_department, endTime)
        doc.wasDerivedFrom(fire_department, resource, get_fire_department, get_fire_department, get_fire_department)

        repo.logout()

        return doc


# '''
# # This is example code you might use for debugging this module.
# # Please remove all top-level function calls before submitting.
# '''
# fire_department.execute()
# doc = fire_department.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
#
# ## eof