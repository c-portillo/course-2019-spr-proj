import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pymongo
import pandas as pd

class crimes(dml.Algorithm):
    contributor = 'xcao19'
    reads = []
    writes = ['xcao19.crimes']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')

        url = 'https://data.boston.gov/dataset/6220d948-eae2-4e4b-8723-2dc8e67722a3/resource/12cb3883-56f5-47de-afa5-3b1cf61b257b/download/tmpwvgcmcba.csv'
        
        df = pd.read_csv(url, encoding = 'ISO-8859-1')
        json_df = df.to_json(orient='records')
        r = json.loads(json_df)
        
        repo.dropCollection("crime")
        repo.createCollection("crime")
        repo['xcao19.crime'].insert_many(r)
        repo['xcao19.crime'].metadata({'complete':True})

        repo.logout()
        endTime = datetime.datetime.now()
        return {"start":startTime, "end":endTime}
    
   
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
        '''
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('bdg', 'https://data.boston.gov/dataset')
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        #Entities
        resource = doc.entity('bdg: tmpb3tkd2to.csv', 
                {prov.model.PROV_TYPE: 'ont:DataResource',
                'ont: Extension': 'csv'})
        crime = doc.entity('dat: xcao19.crime', {prov.model.PROV_LABEL: 'crime data', prov.model.PROV_TYPE: 'ont: DataSet'})

        #Agents
        this_script = doc.agent('alg: xcao19_crimes.py', 
                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': '.py'})

        #Algos/Activities
        get_resource = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        #Prov
        doc.wasAssociatedWith(get_resource, this_script)
        doc.wasAttributedTo(crime, this_script)
        doc.wasGeneratedBy(crime, get_resource, endTime)
        doc.usage(get_resource, resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query': 'incident_number,offense_code,offence_code_group,offence_description,district,reporting_area,shooting,occured_on_date,year,month,day_of_week,hour,ucr_part,street,lat,long,location'
                   }
                  )
        doc.wasDerivedFrom(crime, resource, get_resource, get_resource, get_resource)
        repo.logout()

        return doc

# crimes.execute()
# doc = crime.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
