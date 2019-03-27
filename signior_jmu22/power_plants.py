import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd






class power_plants(dml.Algorithm):
  contributor = 'signior_jmu22'
  reads = []
  writes = ['signior_jmu22.power_plants']

  @staticmethod
  def execute(trial = False):
    startTime = datetime.datetime.now()

    # Set up database connection
    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('signior_jmu22', 'signior_jmu22')

    url = 'http://datamechanics.io/data/signior_jmu22/global_power_plant_database.csv'
    df = pd.read_csv(url)
    new_df = df.filter(['country_long', 'fuel1', 'fuel2', 'fuel3', 'fuel4', 'commissioning_year'], axis=1)
    power_plants_dict = new_df.to_dict(orient='records')
    
    repo.dropCollection("power_plants")
    repo.createCollection("power_plants")
    repo['signior_jmu22.power_plants'].insert_many(power_plants_dict)
    repo['signior_jmu22.power_plants'].metadata({'complete': True})

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

    this_script = doc.agent('alg:signior_jmu22#power_plants', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
    resource = doc.entity('dat:signior_jmu22#power_plants', {'prov:label': 'global_power_plants_database', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
    get_power_plants_info = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
    doc.wasAssociatedWith(get_power_plants_info, this_script)
    doc.usage(get_power_plants_info, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retreival'})

    power_plants_info = doc.entity('dat:signior_jmu22#power_plants', {prov.model.PROV_LABEL: 'Sea Surface Temperature Anomalies', prov.model.PROV_TYPE:'ont:DataSet'})
    doc.wasAttributedTo(power_plants_info, this_script)
    doc.wasGeneratedBy(power_plants_info, get_power_plants_info,endTime)
    doc.wasDerivedFrom(power_plants_info, resource, get_power_plants_info, get_power_plants_info, get_power_plants_info)

    repo.logout()

    return doc






# comment this out when submitting, just for testing
# power_plants.execute()
# doc = power_plants.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))