import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd

class mbta_stops(dml.Algorithm):
    contributor = 'aqu1'
    reads = []
    writes = ['aqu1.mbta_stops_data']
    
    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()
        # Dataset 5: MBTA Bus Stops
        url = 'https://opendata.arcgis.com/datasets/2c00111621954fa08ff44283364bba70_0.csv?outSR=%7B%22wkid%22%3A102100%2C%22latestWkid%22%3A3857%7D'
        bus_stops = pd.read_csv(url)

        # Dataset 6: MBTA T stops 
        url = 'http://maps-massgis.opendata.arcgis.com/datasets/a9e4d01cbfae407fbf5afe67c5382fde_2.csv'
        t_stops = pd.read_csv(url)

        # Merge latitude and longitudes of all bus and T-stops in Boston
        bus = pd.concat([bus_stops.stop_lat, bus_stops.stop_lon], axis = 1) # select columns
        bus.columns = ['Latitude', 'Longitude']
        train = pd.concat([t_stops.Y, t_stops.X], axis = 1) # select columns
        train.columns = ['Latitude', 'Longitude']
        public_stops = bus.append(train) # aggregate data 
        public_stops = pd.DataFrame(public_stops)
        public_stops = json.loads(public_stops.to_json(orient = 'records'))
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('aqu1', 'aqu1')
        
        repo.dropCollection("mbta_stops_data")
        repo.createCollection("mbta_stops_data")
        repo['aqu1.mbta_stops_data'].insert_many(public_stops)
        
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
        doc.add_namespace('agh', 'https://opendata.arcgis.com/datasets/') # Arc GIS Hub

        this_script = doc.agent('alg:aqu1#', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        
        # MBTA Stops Report
        resource_bus_stops = doc.entity('agh:2c00111621954fa08ff44283364bba70_0.csv?outSR=%7B%22wkid%22%3A102100%2C%22latestWkid%22%3A3857%7D', {'prov:label':'MBTA Bus Stops', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        resource_t_stops = doc.entity('agh:a9e4d01cbfae407fbf5afe67c5382fde_2.csv', {'prov:label':'MBTA T-Stops', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_stops = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_stops, this_script)
        doc.usage(get_stops, resource_bus_stops, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
        doc.usage(get_stops, resource_t_stops, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})

        mbta_stops = doc.entity('dat:aqu1#mbta_stops_data', {prov.model.PROV_LABEL:'MBTA Stops', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(mbta_stops, this_script)
        doc.wasGeneratedBy(mbta_stops, get_stops, endTime)
        doc.wasDerivedFrom(mbta_stops, resource_bus_stops, get_stops, get_stops, get_stops)
        doc.wasDerivedFrom(mbta_stops, resource_t_stops, get_stops, get_stops, get_stops)
        
        repo.logout()

        return doc