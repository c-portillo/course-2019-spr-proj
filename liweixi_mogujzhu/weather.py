import urllib.request
import pandas as pd
import json
import dml
import prov.model
import datetime
import uuid
import io
import csv


class weather(dml.Algorithm):
    contributor = 'liweixi_mogjzhu'
    reads = []
    writes = ['liweixi_mogujzhu.weather']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        print("Getting boston weather...")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('liweixi_mogujzhu', 'liweixi_mogujzhu')

        url = 'http://datamechanics.io/data/boston_weather.csv'
        df = pd.read_csv(url)
        boston_w = df.loc[df['NAME'] == "BOSTON, MA US"]
        boston_w = json.loads(boston_w.to_json(orient='records'))
        # s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("weather")
        repo.createCollection("weather")
        repo['liweixi_mogujzhu.weather'].insert_many(boston_w)
        repo['liweixi_mogujzhu.weather'].metadata({'complete': True})
        print(repo['liweixi_mogujzhu.weather'].metadata())

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
        doc.add_namespace('bdp', 'https://www.ncdc.noaa.gov/cdo-web/')

        this_script = doc.agent('alg:liweixi_mogujzhu#weather',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('dat:liweixi_mogujzhu#weather',
                              {'prov:label': 'Boston Weather', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'csv'})
        get_weather = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_weather, this_script)

        weather = doc.entity('dat:liweixi_mogujzhu#weather',
                          {prov.model.PROV_LABEL: 'Boston Weather', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(weather, this_script)
        doc.wasGeneratedBy(weather, get_weather, endTime)
        doc.wasDerivedFrom(weather, resource, get_weather, get_weather, get_weather)

        repo.logout()

        return doc


# '''
# # This is example code you might use for debugging this module.
# # Please remove all top-level function calls before submitting.
# '''
# weather.execute()
# doc = weather.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
#
# ## eof