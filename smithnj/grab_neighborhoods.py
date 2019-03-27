import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import geopandas

############################################
# grab_neighborhoods.py
# Script for collecting Chicago Community Areas
############################################

class grab_neighborhoods(dml.Algorithm):
    contributor = 'smithnj'
    reads = []
    writes = ['smithnj.communityareas']

    @staticmethod
    def execute(trial=False):

        startTime = datetime.datetime.now()
        # ---[ Connect to Database ]---------------------------------
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('smithnj', 'smithnj')
        repo_name = 'smithnj.communityareas'
        # ---[ Grab Data ]-------------------------------------------
        df = geopandas.read_file(
            'https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON').to_json()
        loaded = json.loads(df)
        # ---[ MongoDB Insertion ]-------------------------------------------
        repo.dropCollection('communityareas')
        repo.createCollection('communityareas')
        print('done')
        repo[repo_name].insert_one(loaded)
        repo[repo_name].metadata({'complete': True})
        # ---[ Finishing Up ]-------------------------------------------
        print(repo[repo_name].metadata())
        repo.logout()
        endTime = datetime.datetime.now()
        return {"start": startTime, "end": endTime}

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

            this_script = doc.agent('alg:smithnj#communityareas',
                                    {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
            resource = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

            get_communityareas = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

            doc.wasAssociatedWith(get_communityareas, this_script)
            doc.usage(get_communityareas, resource, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
            doc.wasAttributedTo(get_communityareas, this_script)
            doc.wasGeneratedBy(get_communityareas, resource, endTime)
            doc.wasDerivedFrom(get_communityareas, resource)

            repo.logout()

            return doc