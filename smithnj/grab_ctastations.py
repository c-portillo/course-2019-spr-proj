import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

############################################
# grab_ctastations.py
# Script for collecting CTA Stations data
############################################

class grab_ctastations(dml.Algorithm):
    contributor = 'smithnj'
    reads = []
    writes = ['smithnj.ctastats']

    @staticmethod
    def execute(trial=False):

        startTime = datetime.datetime.now()

        # ---[ Connect to Database ]---------------------------------
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('smithnj', 'smithnj')
        repo_name = 'smithnj.ctastats'
        # ---[ Grab Data ]-------------------------------------------
        df = pd.read_csv('http://datamechanics.io/data/smithnj/smithnj/CTA_Ridership_Totals.csv').to_json(orient='records')
        loaded = json.loads(df)
        # ---[ MongoDB Insertion ]-------------------------------------------
        repo.dropCollection('ctastats')
        repo.createCollection('ctastats')
        print('done')
        repo[repo_name].insert_many(loaded)
        repo[repo_name].metadata({'complete': True})
        # ---[ Finishing Up ]-------------------------------------------
        print(repo[repo_name].metadata())
        repo.logout()
        endTime = datetime.datetime.now()

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('smithnj', 'smithnj')
        doc.add_namespace('alg',
                          'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat',
                          'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofchicago.org/api/views/t2qc-9pjd/rows.csv?accessType=DOWNLOAD')

        this_script = doc.agent('alg:smithnj#ctastats',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        resource = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        get_stationstats = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_stationstats, this_script)
        doc.usage(get_stationstats, resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.wasAttributedTo(get_stationstats, this_script)
        doc.wasGeneratedBy(get_stationstats, resource, endTime)
        doc.wasDerivedFrom(get_stationstats, resource)

        repo.logout()

        return doc
