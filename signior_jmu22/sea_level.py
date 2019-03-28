import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class sea_level(dml.Algorithm):
  contributor = 'signior_jmu22'
  reads = []
  writes = ['signior_jmu22.sea_level']

  @staticmethod
  def execute(trial = False):
    startTime = datetime.datetime.now()

    # Set up database connection
    client = dml.pymongo.MongoClient()
    repo = client.repo
    repo.authenticate('signior_jmu22', 'signior_jmu22')

    url = "ftp://ftp.csiro.au/legresy/gmsl_files/CSIRO_Alt_yearly.csv"
    df = pd.read_csv(url)
    
    
    sea_level_dict = df.to_dict(orient='records')
    # print(sea_level_dict)
    
    repo.dropCollection("sea_level")
    repo.createCollection("sea_level")
    repo['signior_jmu22.sea_level'].insert_many(sea_level_dict)
    repo['signior_jmu22.sea_level'].metadata({'complete': True})

    print(repo['signior_jmu22.sea_level'].metadata())

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

    this_script = doc.agent('alg:signior_jmu22#sea_level', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})
    resource = doc.entity('dat:sea_level_change', {'prov:label': 'Sea Level Change Yearly', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
    get_sea_level= doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
    doc.wasAssociatedWith(get_sea_level, this_script)
    doc.usage(get_sea_level, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retreival'})

    sea_level = doc.entity('dat:signior_jmu22#sea_level', {prov.model.PROV_LABEL: 'Sea Level Change', prov.model.PROV_TYPE:'ont:DataSet'})
    doc.wasAttributedTo(sea_level, this_script)
    doc.wasGeneratedBy(sea_level, get_sea_level,endTime)
    doc.wasDerivedFrom(sea_level, resource, get_sea_level, get_sea_level, get_sea_level)

    repo.logout()

    return doc






# comment this out when submitting, just for testing
# sea_level.execute()
# doc = sea_level.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))