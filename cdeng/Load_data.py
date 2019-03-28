## This python file is under cdeng file

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

import pandas as pd
import csv
import io
import requests
# import urllib
# import data_processing


class Load_data(dml.Algorithm):
    contributor = 'cdeng'

    # reads = []
    # writes = []

    # This is the first algorithm need to execute, it reads nothing and write all the data set. 
    reads = []
    writes = ['cdeng.stations_info', 'cdeng.bike_trip', 'cdeng.Boston_bike_lane', 
    'cdeng.Cambridge_bike_lane']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        # (username, password)
        repo.authenticate('cdeng', 'cdeng')

        ################################### Put data into MongoDB ###################################
        print('Algorithm 1: load data')

        # Loading station data
        print("1. Load station data here...")
        url = 'https://s3.amazonaws.com/hubway-data/Hubway_Stations_as_of_July_2017.csv' 
        response = urllib.request.urlopen(url).read().decode("utf-8")
        content_df = pd.read_csv(io.StringIO(response))
        content_df_dict = content_df.to_dict(orient = 'records')

        repo.dropCollection("cdeng.stations_info")
        repo.createCollection("cdeng.stations_info")
        repo['cdeng.stations_info'].insert_many(content_df_dict)


        print("2. Load 201801 bike trip data here...")
        url = 'http://datamechanics.io/data/201801_hubway_tripdata.csv' # This data is found by myself
        response = urllib.request.urlopen(url).read().decode("utf-8")
        content_df_trip0118 = pd.read_csv(io.StringIO(response))
        content_df_trip0118_dict = content_df_trip0118.to_dict(orient = 'records')

        
        print("3. Load 201802 bike trip data here...")
        url = 'http://datamechanics.io/data/201802_hubway_tripdata.csv' # This data is found by myself
        response = urllib.request.urlopen(url).read().decode("utf-8")
        content_df_trip0218 = pd.read_csv(io.StringIO(response))
        content_df_trip0218_dict = content_df_trip0218.to_dict(orient = 'records')

        repo.dropCollection("cdeng.bike_trip")
        repo.createCollection("cdeng.bike_trip")
        repo["cdeng.bike_trip"].insert_many(content_df_trip0118_dict)
        repo["cdeng.bike_trip"].insert_many(content_df_trip0218_dict)

        print("4. Load Boston bike lane data here...")
        url = 'http://bostonopendata-boston.opendata.arcgis.com/datasets/d02c9d2003af455fbc37f550cc53d3a4_0.csv'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        content_df = pd.read_csv(io.StringIO(response))
        content_df_dict = content_df.to_dict(orient = 'records')

        repo.dropCollection("cdeng.Boston_bike_lane")
        repo.createCollection("cdeng.Boston_bike_lane")
        repo['cdeng.Boston_bike_lane'].insert_many(content_df_dict)


        print("5. Load Cambridge bike lane data here...")
        url = 'https://data.cambridgema.gov/api/views/6nf3-vbnd/rows.csv'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        content_df = pd.read_csv(io.StringIO(response))
        content_df_dict = content_df.to_dict(orient = 'records')

        repo.dropCollection("cdeng.Cambridge_bike_lane")
        repo.createCollection("cdeng.Cambridge_bike_lane")
        repo['cdeng.Cambridge_bike_lane'].insert_many(content_df_dict)
        print("Data loading done!")
        ################################### Data Loading Finish ###################################

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
        repo.authenticate('cdeng', 'cdeng')

        ################################### Finish data rprovenance here
        print("Finish data provenance here...")

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') 
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') 
        doc.add_namespace('log', 'http://datamechanics.io/log/') 

        doc.add_namespace('bdp', 'http://datamechanics.io/data/')
        doc.add_namespace('bdp2', 'https://s3.amazonaws.com/hubway-data')
        doc.add_namespace('bdp3', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')
        doc.add_namespace('bdp4', 'https://data.cambridgema.gov/api/')
        

        this_script = doc.agent('alg:cdeng#Load_data', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

        resource1 = doc.entity('bdp:201801_hubway_tripdata', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        resource2 = doc.entity('bdp:201802_hubway_tripdata', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        resource3 = doc.entity('bdp2:Hubway_Stations_as_of_July_2017', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        resource4 = doc.entity('bdp3:d02c9d2003af455fbc37f550cc53d3a4_0', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        resource5 = doc.entity('bdp4:views/6nf3-vbnd/rows', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        

        get_stations_info = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_bike_trip = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_Bos_bikelane = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_Cam_bikelane = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_stations_info, this_script)
        doc.wasAssociatedWith(get_bike_trip, this_script)
        doc.wasAssociatedWith(get_Bos_bikelane, this_script)
        doc.wasAssociatedWith(get_Cam_bikelane, this_script)

        doc.usage(get_bike_trip, resource1, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        doc.usage(get_bike_trip, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        doc.usage(get_stations_info, resource3, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        doc.usage(get_Bos_bikelane, resource4, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':''
                  }
                  )

        doc.usage(get_Cam_bikelane, resource5, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval',
                  'ont:Query':'?accessType=DOWNLOAD'
                  }
                  )


        bike_trip = doc.entity('dat:cdeng#bike_trip', {prov.model.PROV_LABEL:'bike_trip', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(bike_trip, this_script)
        doc.wasGeneratedBy(bike_trip, get_bike_trip, endTime)
        doc.wasDerivedFrom(bike_trip, resource1, get_bike_trip, get_bike_trip, get_bike_trip)
        doc.wasDerivedFrom(bike_trip, resource2, get_bike_trip, get_bike_trip, get_bike_trip)

        stations_info = doc.entity('dat:cdeng#stations_info', {prov.model.PROV_LABEL:'stations_info', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(stations_info, this_script)
        doc.wasGeneratedBy(stations_info, get_stations_info, endTime)
        doc.wasDerivedFrom(stations_info, resource3, get_stations_info, get_stations_info, get_stations_info)

        Bos_bikelane = doc.entity('dat:cdeng#Boston_bike_lane', {prov.model.PROV_LABEL:'Boston_bike_lane', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(Bos_bikelane, this_script)
        doc.wasGeneratedBy(Bos_bikelane, get_Bos_bikelane, endTime)
        doc.wasDerivedFrom(Bos_bikelane, resource4, get_Bos_bikelane, get_Bos_bikelane, get_Bos_bikelane)

        Cam_bike_lane = doc.entity('dat:cdeng#Cambridge_bike_lane', {prov.model.PROV_LABEL:'Cambridge_bike_lane', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(Cam_bike_lane, this_script)
        doc.wasGeneratedBy(Cam_bike_lane, get_Cam_bikelane, endTime)
        doc.wasDerivedFrom(Cam_bike_lane, resource4, get_Cam_bikelane, get_Cam_bikelane, get_Cam_bikelane)

        ###################################
        repo.logout()      
        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.

# print('\n\n####################Begin playground####################\n\n')
# Load_data.execute()
# doc = Load_data.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
# print('\n\n####################End playground####################\n\n')







## eof