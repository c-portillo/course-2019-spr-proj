import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import urllib.request
import pandas as pd

class carbon_emissions(dml.Algorithm):
  contributor = 'signior_jmu22'
  reads = []
  writes = ['signior_jmu22.carbon_emissions']

  @staticmethod
  def execute(trial = False):
    startTime = datetime.datetime.now()

    # Set up database connection
    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('signior_jmu22', 'signior_jmu22')

    url = 'http://datamechanics.io/data/signior_jmu22/carbon_emissions.csv' # grab dataset from datamechanics.io
    df = pd.read_csv(url, sep='\t')
    filter_values = ['Country Name']
    for i in range(1960, 2015):
      filter_values.append(str(i))
    new_df = df.filter(filter_values)
    carbon_emissions_dict = new_df.to_dict(orient='records')

    repo.dropCollection("carbon_emissions")
    repo.createCollection("carbon_emissions")
    repo['signior_jmu22.carbon_emissions'].insert_many(carbon_emissions_dict)
    repo['signior_jmu22.carbon_emissions'].metadata({'complete': True})

    print(repo['signior_jmu22.carbon_emissions'].metadata())

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

    this_script = doc.agent('alg:signior_jmu22#carbon_emissions', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
    resource = doc.entity('dat:carbon_emissions', {'prov:label': 'Carbon Emissions by Country 1960 - 2014', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'csv'})
    get_carbon_emissions = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
    doc.wasAssociatedWith(get_carbon_emissions, this_script)
    doc.usage(get_carbon_emissions, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retreival'})
    
    carbon_emissions = doc.entity('dat:signior_jmu22#carbon_emissions', {prov.model.PROV_LABEL: 'Carbon Emissions by Country', prov.model.PROV_TYPE: 'ont:DataSet'})
    doc.wasAttributedTo(carbon_emissions, this_script)
    doc.wasGeneratedBy(carbon_emissions, get_carbon_emissions, endTime)
    doc.wasDerivedFrom(carbon_emissions, resource, get_carbon_emissions, get_carbon_emissions, get_carbon_emissions)

    repo.logout()


    return doc



# comment this when submitting, just for testing purposes
carbon_emissions.execute()
# doc = carbon_emissions.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
  