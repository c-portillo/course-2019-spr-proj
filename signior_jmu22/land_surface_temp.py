

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd
from datapackage import Package, Resource

class land_surface_temp(dml.Algorithm):
  contributor = 'signior_jmu22'
  reads = []
  writes = ['signior_jmu22.land_surface_temp']

  @staticmethod
  def execute(trial = False):
    startTime = datetime.datetime.now()

    # Set up database connection
    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('signior_jmu22', 'signior_jmu22')

    package = Package('https://datahub.io/core/global-temp-anomalies/datapackage.json') # grabs data package object from datahub.io

    raw_data = package.get_resource('global-temp-annual_csv').read(keyed=True, cast=False) # grabs specific dataset (global temp annual)

    df = pd.DataFrame(raw_data) # adds raw data to a pandas dataframe
    new_df = df.filter(['Year', 'Land'], axis=1) # filters out year and land (only values we care about because we already have ocean temp)
    
    land_temp_dict = new_df.to_dict(orient='records')
    
    # below block adds the dataset to the repo collection
    repo.dropCollection("land_surface_temp")
    repo.createCollection("land_surface_temp")
    repo['signior_jmu22.land_surface_temp'].insert_many(land_temp_dict)
    repo['signior_jmu22.land_surface_temp'].metadata({'complete': True})

    print(repo['signior_jmu22.land_surface_temp'].metadata())

    repo.logout()

    endTime = datetime.datetime.now()
    return {"start": startTime, "end": endTime}
    
    
  
  @staticmethod
  def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('signior_jmu22', 'signior_jmu22')
    doc.add_namespace('alg', 'http://datamechanics.io/algorithm/signior_jmu22') # The scripts are in <folder>#<filename> format
    doc.add_namespace('dat', 'http://datamechanics.io/data/signior_jmu22' ) # The datasets are in <user>#<collection> format
    doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retreival', 'Query', or 'Computation'
    doc.add_namespace('log', 'http://datamechanics.io/log/')

    this_script = doc.agent('alg:signior_jmu22#land_surface_temp', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
    resource = doc.entity('dat:global_temp_anomalies', {'prov:label': 'Global Temperature Anomalies', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
    get_land_surface_temp = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
    doc.wasAssociatedWith(get_land_surface_temp, this_script)
    doc.usage(get_land_surface_temp, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retreival'})

    land_surface_temp = doc.entity('dat:signior_jmu22#land_surface_temp', {prov.model.PROV_LABEL: 'Global Temp Anomalies', prov.model.PROV_TYPE:'ont:DataSet'})
    doc.wasAttributedTo(land_surface_temp, this_script)
    doc.wasGeneratedBy(land_surface_temp, get_land_surface_temp,endTime)
    doc.wasDerivedFrom(land_surface_temp, resource, get_land_surface_temp, get_land_surface_temp, get_land_surface_temp)

    repo.logout()

    return doc






#comment this out before submitting, just for testing purposes
# land_surface_temp.execute()
# doc = land_surface_temp.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))