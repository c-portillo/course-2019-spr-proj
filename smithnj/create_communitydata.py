import json
import dml
import prov.model
import uuid
import pandas as pd
import datetime
import geopandas

############################################
# create_communitydata.py
# Script for merging Census Socioeconomic Hardship data with Community Geospatial Data
############################################

class create_communitydata(dml.Algorithm):
    contributor = 'smithnj'
    reads = []
    writes = ['smithnj.communitydata']

    @staticmethod
    def execute(trial=False):

        startTime = datetime.datetime.now()
        # ---[ Connect to Database ]---------------------------------
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('smithnj', 'smithnj')
        repo_name = 'smithnj.communitydata'
        # ---[ Grab Data ]-------------------------------------------
        communityareas = geopandas.read_file(
            'https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON')
        census = pd.read_json('http://data.cityofchicago.org/resource/kn9c-c2s2.json')
        # ---[ Merge Data ]-------------------------------------------
        communityareas['area_numbe'] = communityareas['area_numbe'].convert_objects(convert_numeric=True)
        merged = communityareas.merge(census, left_on='area_numbe', right_on='ca')
        merged.drop(['per_capita_income_', 'percent_aged_16_unemployed', 'percent_aged_25_without_high_school_diploma', 'percent_aged_under_18_or_over_64', 'percent_households_below_poverty', 'percent_of_housing_crowded'], axis=1, inplace=True)
        # ---[ Write Data to JSON ]----------------------------------
        data = merged.to_json()
        loaded = json.loads(data)
        # ---[ MongoDB Insertion ]-------------------------------------------
        repo.dropCollection('communitydata')
        repo.createCollection('communitydata')
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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:smithnj#communitydata', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        community_areas = doc.entity('dat:smithnj#communityareas', {'prov:label':'Chicago Community Areas Data', prov.model.PROV_TYPE:'ont:DataSet'})
        census = doc.entity('dat:smithnj#census', {'prov:label':'Chicago Socioeconomic Hardship Census Data', prov.model.PROV_TYPE:'ont:DataSet'})
        merge = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(merge, this_script)
        doc.usage(merge, community_areas, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})
        doc.usage(merge, census, startTime, None, {prov.model.PROV_TYPE:'ont:Computation'})

        community_areas_with_hardship = doc.entity('dat:smithnj#communitydata', {prov.model.PROV_LABEL:'Chicago Socioeconomic Hardship Data with Community Area Number', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(community_areas_with_hardship, this_script)
        doc.wasGeneratedBy(community_areas_with_hardship, merge, endTime)
        doc.wasDerivedFrom(community_areas_with_hardship, census)
        doc.wasDerivedFrom(community_areas_with_hardship, community_areas)

        repo.logout()

        return doc