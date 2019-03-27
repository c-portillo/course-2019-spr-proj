import urllib.request
import json
import csv
import dml
import prov.model
import datetime
import uuid
import pandas as pd 

class airbnb(dml.Algorithm):
    contributor = 'kzhang21_ryuc'
    reads = ['kzhang21_ryuc.play']
    writes = ['kzhang21_ryuc.airbnb']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')

        #read in csv file
        url = 'http://datamechanics.io/data/airbnb_listing.csv'
        data = pd.read_csv(url, header=0)
        #select relevant columns
        data_airbnb = data[['name','host_id', 'host_name', 'neighbourhood', 'latitude',  'longitude',	'room_type',  
                          'price', 'minimum_nights', 'number_of_reviews',	'availability_365']].copy()
        #change column to appropriate names
        data_airbnb.rename(columns={'name': 'Name', 'neighbourhood': 'Neighborhood', 
                                    'latitude': 'Latitude', 'longitude': 'Longitude'}, inplace=True)
        
        #sort by neighborhood
        data_airbnb.sort_values(by=['Neighborhood'], inplace = True)

        #add zip column to airbnb
        entData = pd.DataFrame(repo.kzhang21_ryuc.play.find())
        entData.sort_values(by=['Neighborhood'], inplace = True)

        #map zipcode to neighborhood 
        nZip = {}
        for index,row in entData.iterrows():
            key = row['Neighborhood']
            if key not in nZip:
                nZip[key] = row['Zip']

        
        #make common neighbohood name
        airbnb_n = data_airbnb[['Neighborhood']].copy()
        airbnb_n.drop_duplicates(inplace=False)
        neighbor = {}
        for index,row in airbnb_n.iterrows():
            if row['Neighborhood'] not in neighbor:
                for key in nZip:
                    if row['Neighborhood'] in key:
                        neighbor[row['Neighborhood']] = key
        
        

        #add zip column to airbnb
        data_airbnb['Neighborhood'] =  data_airbnb['Neighborhood'].map(neighbor)
        data_airbnb['Zip'] = data_airbnb['Neighborhood'].map(nZip)

        r = json.loads(data_airbnb.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)

        repo.dropCollection("airbnb")
        repo.createCollection("airbnb")
        repo['kzhang21_ryuc.airbnb'].insert_many(r)
        repo['kzhang21_ryuc.airbnb'].metadata({'complete':True})
        print(repo['kzhang21_ryuc.airbnb'].metadata())
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
        doc.add_namespace('airbnb', 'http://datamechanics.io/data/')

        this_script = doc.agent('alg:kzhang21_ryuc#airbnb', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('airbnb:airbnb_listing.csv', {'prov:label':'Airbnb, Location Search', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_place = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_place, this_script)
        doc.usage(get_place, resource, startTime, None,{prov.model.PROV_TYPE:'ont:Retrieval'})

        airbnb = doc.entity('dat:kzhang21_ryuc#airbnb', {prov.model.PROV_LABEL:'Airbnb Listings', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(airbnb, this_script)
        doc.wasGeneratedBy(airbnb, get_place, endTime)
        doc.wasDerivedFrom(airbnb, resource, get_place, get_place, get_place)

        repo.logout()
                  
        return doc

# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# Airbnb.execute()
# doc = Airbnb.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof