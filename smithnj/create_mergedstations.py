import json
import dml
import prov.model
import uuid
import pandas as pd
import datetime
import geopandas

############################################
# create_mergedstations.py
# Script for merging L-station GeoSpatial Data with Community Area Number GeoSpatial Data
############################################

class create_mergedstations(dml.Algorithm):
    contributor = 'smithnj'
    reads = []
    writes = ['smithnj.merged_stations']

    @staticmethod
    def execute(trial=False):

        startTime = datetime.datetime.now()
        # ---[ Connect to Database ]---------------------------------
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('smithnj', 'smithnj')
        repo_name = 'smithnj.merged_stations'
        # ---[ Grab Data ]-------------------------------------------
        communityareas = geopandas.read_file(
            'https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON')
        stationloc = geopandas.read_file('http://datamechanics.io/data/smithnj/CTA_RailStations.geojson')
        # ---[ Create Data ]-----------------------------------------
        merged = geopandas.sjoin(communityareas, stationloc, how="inner", op='within')
        # ---[ Write Data to JSON ]----------------------------------
        data = merged.to_json()
        loaded = json.loads(data)
        # ---[ MongoDB Insertion ]-------------------------------------------
        repo.dropCollection('merged_stations')
        repo.createCollection('merged_stations')
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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont',
                          'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:smithnj#merged_stations',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
        communityareas = doc.entity('dat:smithnj#communityareas',
                                     {'prov:label': 'Chicago Community Areas Data',
                                      prov.model.PROV_TYPE: 'ont:DataSet'})
        stationlocation = doc.entity('dat:smithnj#stations', {'prov:label': 'Chicago L-Station Location',
                                                   prov.model.PROV_TYPE: 'ont:DataSet'})
        merge = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(merge, this_script)
        doc.usage(merge, communityareas, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})
        doc.usage(merge, stationlocation, startTime, None, {prov.model.PROV_TYPE: 'ont:Computation'})

        merged_stations_with_geo = doc.entity('dat:smithnj#merged_stations', {
            prov.model.PROV_LABEL: 'Chicago L Stations',
            prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(merge, this_script)
        doc.wasGeneratedBy(merged_stations_with_geo, merge, endTime)
        doc.wasDerivedFrom(merged_stations_with_geo, communityareas)
        doc.wasDerivedFrom(merged_stations_with_geo, stationlocation)

        repo.logout()

        return doc
