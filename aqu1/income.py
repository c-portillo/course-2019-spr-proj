import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class income(dml.Algorithm):
    contributor = 'aqu1'
    reads = []
    writes = ['aqu1.income_data']
    
    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        # Dataset 4: Vulnerable Groups in Boston 
        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/34f2c48b670d4b43a617b1540f20efe3_0.csv'
        income = pd.read_csv(url)

        income = income.groupby('Name').sum() # aggregate data for 23 neighborhoods of Boston
        income['prop_low_income'] = income.Low_to_No / income.POP100_RE # projection: new column for proportion of people who have low income
        income = pd.DataFrame(income)
        income = json.loads(income.to_json(orient = 'records'))

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aqu1', 'aqu1')
        
        repo.dropCollection("income_data")
        repo.createCollection("income_data")
        repo['aqu1.income_data'].insert_many(income)
        
        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}
        
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aqu1', 'aqu1')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bod', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/') # Boston Open Data 
        
        this_script = doc.agent('alg:aqu1#', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        # Income Report 
        resource_income = doc.entity('bod:34f2c48b670d4b43a617b1540f20efe3_0.csv', {'prov:label':'Low Income Population', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_income = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_income, this_script)
        doc.usage(get_income, resource_income, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})

        income = doc.entity('dat:aqu1#income_data', {prov.model.PROV_LABEL:'Low Income Population', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(income, this_script)
        doc.wasGeneratedBy(income, get_income, endTime)
        doc.wasDerivedFrom(income, resource_income, get_income, get_income, get_income)
        
        repo.logout()

        return doc   