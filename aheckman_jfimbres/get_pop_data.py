import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd


class get_pop_data(dml.Algorithm):
    contributor = 'aheckman_jfimbres'
    reads = []
    writes = ['aheckman_jfimbres.partisan_map', 'aheckman_jfimbres.census']

    @staticmethod
    def execute(trial=False):
        '''Retrieve the csv style data sets on pop data from Yale climate communications and the Census Bureau.'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aheckman_jfimbres', 'aheckman_jfimbres')

        url = 'https://gallery.mailchimp.com/78464048a89f4b58b97123336/files/a5bf9b45-49fa-4020-a91a-ee2c6af9be93/PartisanMapData_20190218.01.csv'
        df = pd.read_csv(url)
        response = df.to_json(orient='records')
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("partisan_map")
        repo.createCollection("partisan_map")
        repo['aheckman_jfimbres.partisan_map'].insert_many(r)

        url = 'https://www2.census.gov/programs-surveys/popest/datasets/2010-2017/state/asrh/scprc-est2017-18+pop-res.csv'
        df = pd.read_csv(url)
        response = df.to_json(orient='records')
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("census")
        repo.createCollection("census")
        repo['aheckman_jfimbres.census'].insert_many(r)

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
        repo.authenticate('aheckman_jfimbres', 'aheckman_jfimbres')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        this_script = doc.agent('alg:aheckman_jfimbres#get_pop_data',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.entity('bdp:wc8w-nujj',
                              {'prov:label': '311, Service Requests', prov.model.PROV_TYPE: 'ont:DataResource',
                               'ont:Extension': 'json'})
        get_partisan_map = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_census = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_partisan_map, this_script)
        doc.wasAssociatedWith(get_census, this_script)

        doc.usage(get_partisan_map, resource, startTime, None)
        doc.usage(get_census, resource, startTime, None)

        partisan_map = doc.entity('dat:aheckman_jfimbres#partisan_map',
                          {prov.model.PROV_LABEL: 'Partisan Map Data', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(partisan_map, this_script)
        doc.wasGeneratedBy(partisan_map, get_partisan_map, endTime)
        doc.wasDerivedFrom(partisan_map, resource, get_partisan_map)

        census = doc.entity('dat:aheckman_jfimbres#census',
                           {prov.model.PROV_LABEL: 'Census Data', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(census, this_script)
        doc.wasGeneratedBy(census, get_census, endTime)
        doc.wasDerivedFrom(census, resource, get_census)

        repo.logout()

        return doc


get_pop_data.execute()
## eof