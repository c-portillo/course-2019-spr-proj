import urllib.request
import csv
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd
from ast import literal_eval as make_tuple 

class entertainment(dml.Algorithm):
    contributor = 'kzhang21_ryuc'
    reads = []
    writes = ['kzhang21_ryuc.play']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kzhang21_ryuc', 'kzhang21_ryuc')

        #analyze boston enterrainment data set
        #read in csv file
        url = 'http://datamechanics.io/data/boston_entertainment.csv'
        data = pd.read_csv(url, header=0)
        #select relevant columns
        data_entertainment = data[['BUSINESSNAME','LICCATDESC', 'Neighborhood', 'Address', 'CITY', 'STATE', 'ZIP', 'Location']].copy()
        #change column to appropriate names
        data_entertainment.columns = ['Name', 'Description', 'Neighborhood', 'Street', 'City', 'State', 'Zip', 'Location']
        #properly formate Zip code so it will be easier to merge
        data_entertainment['Zip'] = data_entertainment['Zip'].apply(lambda x: x.zfill(5))
        #eliminate all null locations
        data_entertainment.dropna(inplace=True)
        #separate longtitude and latitude 
        ent_temp = data_entertainment['Location'].tolist()
        ent_location = [make_tuple(x) for x in ent_temp]
        ent_long = [x[1] for x in ent_location]
        ent_lat = [x[0] for x in ent_location]
        data_entertainment['Latitude'] = ent_lat
        data_entertainment['Longitude'] = ent_long
        data_entertainment = data_entertainment.drop(['Location'], axis=1)
        
        r = json.loads(data_entertainment.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)
        
        repo.dropCollection("play")
        repo.createCollection("play")
        repo['kzhang21_ryuc.play'].insert_many(r)
        repo['kzhang21_ryuc.play'].metadata({'complete':True})
        print(repo['kzhang21_ryuc.play'].metadata())

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
        doc.add_namespace('ent', 'http://datamechanics.io/data/')

        this_script = doc.agent('alg:kzhang21_ryuc#play', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('ent:boston_entertainment.csv', {'prov:label':'Entertainment, Entertainment Search', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_place = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_place, this_script)
        doc.usage(get_place, resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval'
                  }
                  )

        play = doc.entity('dat:kzhang21_ryuc#play', {prov.model.PROV_LABEL:'Play Found', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(play, this_script)
        doc.wasGeneratedBy(play, get_place, endTime)
        doc.wasDerivedFrom(play, resource, get_place, get_place, get_place)

        repo.logout()
                  
        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
# Entertainment.execute()
# doc = Entertainment.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))


## eof