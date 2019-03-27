import urllib.request
import csv
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

'''
Goal: Combines dataset of entertainment and food businesses.
Purpose: Reduce redundancy and create general data set of places to go
'''
def product(R, S):
    return [(t,u) for t in R for u in S]

class eatNplay(dml.Algorithm):
    contributor = 'kzhang21_ryuc'
    reads = ['kzhang21_ryuc.food', 'kzhang21_ryuc.play']
    writes = ['kzhang21_ryuc.eatNplay']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')

        #retrieve data sets
        foodData = pd.DataFrame(repo.kzhang21_ryuc.food.find())
        entData = pd.DataFrame(repo.kzhang21_ryuc.play.find())

        #map neighborhood to zipcode 
        nZip = {}
        for index,row in entData.iterrows():
            key = row['Zip']
            if key not in nZip:
                nZip[key] = row['Neighborhood']


        #add neighborhood column to food places
        foodData['Neighborhood'] = foodData['Zip'].map(nZip)
        
        #merge the two datasets
        frames = [foodData, entData]
        result = pd.concat(frames)
        #drop id column that was created by mongodb
        result.drop(['_id'], axis = 1, inplace = True)
        #drop duplicates
        result.drop_duplicates(result.columns.difference(['Description']), inplace = True)
        #sort by neighborhood
        result.sort_values(by=['Neighborhood'], inplace = True)
        
        r = json.loads(result.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)
        
        repo.dropCollection("eatNplay")
        repo.createCollection("eatNplay")
        repo['kzhang21_ryuc.eatNplay'].insert_many(r)
        repo['kzhang21_ryuc.eatNplay'].metadata({'complete':True})
        print(repo['kzhang21_ryuc.eatNplay'].metadata())

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

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        #additional resource
        doc.add_namespace('food', 'http://datamechanics.io/data/boston_food.csv')
        doc.add_namespace('ent', 'http://datamechanics.io/data/boston_entertainment.csv')

        this_script = doc.agent('alg:kzhang21_ryuc#eatNplay', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:kzhang21_ryuc#eat', {'prov:label':'Food Search', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_lit = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_lit, this_script)
        doc.usage(get_lit, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )

        eatNplay = doc.entity('dat:kzhang21_ryuc#eatNplay', {prov.model.PROV_LABEL:'Play Found', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(eatNplay, this_script)
        doc.wasGeneratedBy(eatNplay, get_lit, endTime)
        doc.wasDerivedFrom(eatNplay, resource, get_lit, get_lit, get_lit)

        repo.logout()
                  
        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# EatNPlay.execute()
# doc = EatNPlay.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof