import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class ocean_surface_temp(dml.Algorithm):
  contributor = 'signior_jmu22'
  reads = []
  writes = ['signior_jmu22.ocean_surface_temp']

  @staticmethod
  def execute(trial = False):
    startTime = datetime.datetime.now()

    # Set up database connection
    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('signior_jmu22', 'signior_jmu22')

    url = 'http://datamechanics.io/data/signior_jmu22/sea_surface_temp_anomaly.csv'
    df = pd.read_csv(url)
    new_df = df.filter(['Year', 'Annual anomaly'], axis=1)
    # print(new_df.head(5)) #uncomment this to see structure
    ocean_temp_dict = new_df.to_dict(orient='records')
    
    repo.dropCollection("ocean_surface_temp")
    repo.createCollection("ocean_surface_temp")
    repo['signior_jmu22.ocean_surface_temp'].insert_many(ocean_temp_dict)
    repo['signior_jmu22.ocean_surface_temp'].metadata({'complete': True})

    print(repo['signior_jmu22.power_plants'].metadata())

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


    this_script = doc.agent('alg:signior_jmu22#ocean_surface_temp', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
    resource = doc.entity('dat:sea_surface_temp_anomalies', {'prov:label': 'Sea Surface Temperature Anomalies', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
    get_sea_surface_temp = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
    doc.wasAssociatedWith(get_sea_surface_temp, this_script)
    doc.usage(get_sea_surface_temp, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retreival'})

    sea_surface_temp = doc.entity('dat:signior_jmu22#sea_surface_temp', {prov.model.PROV_LABEL: 'Sea Surface Temperature Anomalies', prov.model.PROV_TYPE:'ont:DataSet'})
    doc.wasAttributedTo(sea_surface_temp, this_script)
    doc.wasGeneratedBy(sea_surface_temp, get_sea_surface_temp,endTime)
    doc.wasDerivedFrom(sea_surface_temp, resource, get_sea_surface_temp, get_sea_surface_temp, get_sea_surface_temp)

    repo.logout()

    return doc






# comment this when submitting, this is purely for testing purposes
ocean_surface_temp.execute()
# doc = ocean_surface_temp.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))