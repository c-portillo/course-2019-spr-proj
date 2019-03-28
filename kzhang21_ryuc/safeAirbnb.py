import urllib.request
import json
import csv
import dml
import prov.model
import datetime
import uuid
import pandas as pd 

class safeAirbnb(dml.Algorithm):
    contributor = 'kzhang21_ryuc'
    reads = ['kzhang21_ryuc.airbnb', 'kzhang21_ryuc.crimeLoc']
    writes = ['kzhang21_ryuc.safeAirbnb']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')

        #retrieve data sets
        airbnbData = pd.DataFrame(repo.kzhang21_ryuc.airbnb.find())
        crimeData = pd.DataFrame(repo.kzhang21_ryuc.crimeLoc.find())

        #map neighborhood to zipcode 
        nZip = {}
        for index,row in airbnbData.iterrows():
            key = row['Zip']
            if key not in nZip:
                nZip[key] = row['Neighborhood']
        
        #add edit neighborhood column for crime dataset to match airbnb
        crimeData['Zip'] = crimeData['Zip'].apply(lambda x: str(x).zfill(5))
        crimeData['Neighborhood'] = crimeData['Zip'].map(nZip)

        #map neighborhood to total crime
        totalCrime = {}
        for index,row in crimeData.iterrows():
            totalCrime[row['Neighborhood']] = totalCrime.get(row['Neighborhood'],0) +row['Crime']

        #fill total crime column for airbnb data
        airbnbData['Total_Crime'] = airbnbData['Neighborhood'].map(totalCrime)


        #drop id column that was created by mongodb
        airbnbData.drop(['_id'], axis = 1, inplace = True)
        #sort by neighborhood
        airbnbData.sort_values(by=['Neighborhood'], inplace = True)
        
        r = json.loads(airbnbData.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)
        
        repo.dropCollection("safeAirbnb")
        repo.createCollection("safeAirbnb")
        repo['kzhang21_ryuc.safeAirbnb'].insert_many(r)
        repo['kzhang21_ryuc.safeAirbnb'].metadata({'complete':True})
        print(repo['kzhang21_ryuc.safeAirbnb'].metadata())

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
        doc.add_namespace('airbnb', 'http://datamechanics.io/data/airbnb_listing.csv')
        doc.add_namespace('crime',
                          'https://data.boston.gov/dataset/6220d948-eae2-4e4b-8723-2dc8e67722a3/resource/12cb3883-56f5-47de-afa5-3b1cf61b257b/download/tmpxjqz5gin.csv')
        doc.add_namespace('station',
                          'http://bostonopendata-boston.opendata.arcgis.com/datasets/e5a0066d38ac4e2abbc7918197a4f6af_6.csv')

        this_script = doc.agent('alg:kzhang21_ryuc#safeairbnb', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('dat:kzhang21_ryuc#airbnb', {'prov:label':'Airbnb, Location Search', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_place = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_place, this_script)
        doc.usage(get_place, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )

        safeairbnb = doc.entity('dat:kzhang21_ryuc#safeairbnb', {prov.model.PROV_LABEL:'Place Found', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(safeairbnb, this_script)
        doc.wasGeneratedBy(safeairbnb, get_place, endTime)
        doc.wasDerivedFrom(safeairbnb, resource, get_place, get_place, get_place)

        repo.logout()
                  
        return doc

# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.

# SafeAirbnb.execute()
# doc = SafeAirbnb.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof