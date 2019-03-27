import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd 
from ast import literal_eval as make_tuple

class food(dml.Algorithm):
    contributor = 'kzhang21_ryuc'
    reads = []
    writes = ['kzhang21_ryuc.food']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')

        #analyze boston food businesses data set
        #read in csv file
        url = 'https://data.boston.gov/dataset/03693648-2c62-4a2c-a4ec-48de2ee14e18/resource/4582bec6-2b4f-4f9e-bc55-cbaa73117f4c/download/tmper3diw4s.csv'
        data = pd.read_csv(url, header=0)
        #select relevant columns
        data_food = data[['businessname','descript', 'address', 'city', 'state', 'zip', 'location']].copy()
        #change column to appropriate names
        data_food.columns = ['Name', 'Description', 'Street', 'City', 'State', 'Zip', 'Location']
        #eliminate records with no location
        data_food = data_food[data_food['Location'] != '(0.000000000, 0.000000000)']
        #eliminate all null locations
        data_food.dropna(inplace=True)
        #separate longtitude and latitude 
        food_temp = data_food['Location'].tolist()
        food_location = [make_tuple(x) for x in food_temp]
        food_long = [x[1] for x in food_location]
        food_lat = [x[0] for x in food_location]
        data_food['Latitude'] = food_lat
        data_food['Longitude'] = food_long
        data_food = data_food.drop(['Location'], axis=1)

        r = json.loads(data_food.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)

        repo.dropCollection("food")
        repo.createCollection("food")
        repo['kzhang21_ryuc.food'].insert_many(r)
        repo['kzhang21_ryuc.food'].metadata({'complete':True})
        print(repo['kzhang21_ryuc.food'].metadata())
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
        doc.add_namespace('food', 'https://data.boston.gov/dataset/')

        this_script = doc.agent('alg:kzhang21_ryuc#food', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('food:03693648-2c62-4a2c-a4ec-48de2ee14e18/resource/4582bec6-2b4f-4f9e-bc55-cbaa73117f4c/download/tmper3diw4s.csv', {'prov:label':'Food, Food Search', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_place = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_place, this_script)
        doc.usage(get_place, resource, startTime, None,{prov.model.PROV_TYPE:'ont:Retrieval'})

        food = doc.entity('dat:kzhang21_ryuc#food', {prov.model.PROV_LABEL:'Food Found', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(food, this_script)
        doc.wasGeneratedBy(food, get_place, endTime)
        doc.wasDerivedFrom(food, resource, get_place, get_place, get_place)

        repo.logout()
                  
        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# Food.execute()
# doc = Food.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof