import urllib.request
import pandas as pd
import json
import dml
import prov.model
import datetime
import uuid
import io
import csv


class building_and_property_violations(dml.Algorithm):
    contributor = 'liweixi_mogjzhu'
    reads = []
    writes = ['liweixi_mogujzhu.building_and_property_violations']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        print("Getting building and property violations...")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')

        url = 'https://data.boston.gov/dataset/5e634724-fe64-4762-9648-b4ceb3da5510/resource/90ed3816-5e70-443c-803d-9a71f44470be/download/tmpopimg_l0.csv'
        df = pd.read_csv(url)
        building = json.loads(df.to_json(orient='records'))
        print(building[0])
        # s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("building_and_property_violations")
        repo.createCollection("building_and_property_violations")
        repo['liweixi_mogujzhu.building_and_property_violations'].insert_many(building)
        repo['liweixi_mogujzhu.building_and_property_violations'].metadata({'complete': True})
        print(repo['liweixi_mogujzhu.building_and_property_violations'].metadata())

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
        doc.add_namespace('bdp', 'https://data.boston.gov/dataset/code-enforcement-building-and-property-violations')

        this_script = doc.agent('alg:liweixi_mogujzhu#building_and_property_violations',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:liweixi_mogujzhu#building_and_property_violations',
                              {'prov:label': 'Boston Building And Property Violations', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_building = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_building, this_script)
        doc.usage(get_building, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'
                   }
                  )

        building_property = doc.entity('dat:liweixi_mogujzhu#building_and_property_violations',
                          {prov.model.PROV_LABEL: 'Boston Building And Property Violations', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(building_property, this_script)
        doc.wasGeneratedBy(building_property, get_building, endTime)
        doc.wasDerivedFrom(building_property, resource, get_building, get_building, get_building)

        repo.logout()

        return doc


# '''
# # This is example code you might use for debugging this module.
# # Please remove all top-level function calls before submitting.
# '''
# building_and_property_violations.execute()
# doc = building_and_property_violations.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
#
# ## eof