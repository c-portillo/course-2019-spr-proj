import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class education(dml.Algorithm):
    contributor = 'aqu1'
    reads = []
    writes = ['aqu1.education_data']
    
    @staticmethod
    def execute(trial = False):
        startTime = datetime.datetime.now()
        # Dataset 3: Educational Attainment for People Ages 25+
        url = 'https://data.boston.gov/dataset/8202abf2-8434-4934-959b-94643c7dac18/resource/bb0f26f8-e472-483c-8f0c-e83048827673/download/educational-attainment-age-25.csv'
        education = pd.read_csv(url)

        # select for education attainment in 2000s
        education = education[education.Decade == 2000] 
        # projection: remove % from percent of population column
        education['Percent of Population'] = education['Percent of Population'].apply(lambda p: str(p)[:-1]) 
        education = pd.DataFrame(education)
        education = json.loads(education.to_json(orient = 'records'))
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aqu1', 'aqu1')

        repo.dropCollection("education_data")
        repo.createCollection("education_data")
        repo['aqu1.education_data'].insert_many(education)
        
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
        doc.add_namespace('bdp', 'https://data.boston.gov/dataset/') # Boston Data Portal

        this_script = doc.agent('alg:aqu1#', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        # Education Attainment Report
        resource_education = doc.entity('bdp:8202abf2-8434-4934-959b-94643c7dac18/resource/bb0f26f8-e472-483c-8f0c-e83048827673/download/educational-attainment-age-25.csv', {'prov:label':'Education Attainment', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_education = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_education, this_script)
        doc.usage(get_education, resource_education, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
      
        education = doc.entity('dat:aqu1#education_data', {prov.model.PROV_LABEL:'Education Attainment', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(education, this_script)
        doc.wasGeneratedBy(education, get_education, endTime)
        doc.wasDerivedFrom(education, resource_education, get_education, get_education, get_education)
        
        repo.logout()

        return doc