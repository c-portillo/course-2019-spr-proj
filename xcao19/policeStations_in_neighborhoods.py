import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pymongo
import pandas as pd

class policeStations_in_neighborhoods(dml.Algorithm):
    contributor = 'xcao19'
    reads = ['xcao19.neighborhoods', 'xcao19.policeStation','xcao19.listings','temp']
    writes = ['temp','xcao19.policeStations_in_neighborhoods']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('xcao19', 'xcao19')

        stations = list(repo['xcao19.policeStation'].find())
        airbnb_neighborhoods = list(repo['xcao19.neighborhoods'].find())

        print((airbnb_neighborhoods[0]))
        print(stations[0])
        joined = []
        for n in airbnb_neighborhoods:
            for station in stations:
                if n['neighbourhood'] == station['NEIGHBORHOOD']:
                    joined.append({'neighborhood': n['neighbourhood'], 
                    'policeStation lat/long': [station['Y'], station['X']]})

        repo.dropCollection("temp")
        repo.createCollection("temp")  
        repo['xcao19.temp'].insert_many(joined)
        #Aggregate the Longitude and Latitude coordinates of Airbnbs that exist in a neighborhood with a police Station
        longlat_agg = [
                    {"$lookup": 
                        {
                            "from": "xcao19.listings",
                            "localField": "neighbourhood",
                            "foreignField": "neighbourhood",
                            "as": "air_bnbs"
                        }

                    }
                ]
              
        res = repo['xcao19.temp'].aggregate(longlat_agg)
        repo.dropCollection("policeStations_in_neighborhoods")
        repo.createCollection("policeStations_in_neighborhoods")
        repo['xcao19.policeStations_in_neighborhoods'].insert_many(res)
        repo['xcao19.policeStations_in_neighborhoods'].metadata({'complete':True})
        
        repo.dropCollection('temp')
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
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')  # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/')  # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')  # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/')  # The event log.

        neighborhoods = doc.entity('dat:xcao19_neighborhoods', 
            {prov.model.PROV_LABEL: 'dat: xcao19_neighborhoods', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})
        airbnb_listings = doc.entity('dat:xcao19_listings', 
            {prov.model.PROV_LABEL: 'dat: xcao19_listings', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})
        police_stations = doc.entity('dat:xcao19_policeStation', 
            {prov.model.PROV_LABEL: 'dat: xcao19_policeStation', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})

        temp = doc.entity('dat:xcao19_temp', 
            {prov.model.PROV_LABEL: 'dat: xcao19_temp', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})

        policeStations_in_neighborhoods = doc.entity('dat:xcao19_policeStations_in_neighborhoods', 
            {prov.model.PROV_LABEL: 'dat: xcao19_policeStations_in_neighborhoods', prov.model.PROV_TYPE: 'ont: DataSource', 'ont: Extension': 'json'})

        this_script = doc.agent('alg: xcao19_policeStations_in_neighborhoods.py', 
                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        execute = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime, {prov.model.PROV_TYPE: 'ont: Computation'})

        doc.wasDerivedFrom(temp, police_stations, execute, execute, execute)
        doc.wasDerivedFrom(temp, neighborhoods, execute, execute, execute)
        doc.wasAttributedTo(temp, this_script)
        doc.wasGeneratedBy(temp,execute)

        doc.wasDerivedFrom(policeStations_in_neighborhoods, airbnb_listings, execute, execute, execute)
        doc.wasDerivedFrom(policeStations_in_neighborhoods, temp, execute, execute, execute)
        doc.wasAttributedTo(policeStations_in_neighborhoods, this_script)
        doc.wasGeneratedBy(policeStations_in_neighborhoods, execute)

        doc.wasAssociatedWith(execute,this_script) 

        doc.usage(execute, neighborhoods, startTime, None, {prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.usage(execute, police_stations, startTime, None, {prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.usage(execute, airbnb_listings, startTime, None, {prov.model.PROV_TYPE: 'ont:DataSet'})

        return doc

# policeStations_in_neighborhoods.execute()
# doc = policeStations_in_neighborhoods.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))