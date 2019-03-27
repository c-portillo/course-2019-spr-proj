import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import pandas

class retrieve(dml.Algorithm):
    contributor = 'zhangyb'
    reads = []
    writes = ['zhangyb.mbta_station',
              'zhangyb.hub_station',
              'zhangyb.street_light_location',
              'zhangyb.crime_report',
              'zhangyb.parking_meter_location']

    @staticmethod
    def execute(trial = False):    
        # Setting up MongoDB
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zhangyb', 'zhangyb')

        startTime = datetime.datetime.now()

        # 1: Hubway Stations (http://hubwaydatachallenge.org/api/v1)
        service = dml.auth['services']['hubway']['service']
        username = dml.auth['services']['hubway']['username']
        key = dml.auth['services']['hubway']['key']
        url = service + "station/?format=json&username=" + username + "&api_key=" + key
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("hub_station")
        repo.createCollection("hub_station")
        repo['zhangyb.hub_station'].insert_one(r)
        repo['zhangyb.hub_station'].metadata({'complete':True})
        print(repo['zhangyb.hub_station'].metadata())

        # 2: MBTA Stations (https://api-v3.mbta.com)
        service = dml.auth['services']['mbta']['service']
        url = service + 'stops'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("mbta_station")
        repo.createCollection("mbta_station")
        repo['zhangyb.mbta_station'].insert_one(r)
        repo['zhangyb.mbta_station'].metadata({'complete':True})
        print(repo['zhangyb.mbta_station'].metadata())

        # 3: Street Lights Locations (https://data.boston.gov/dataset/52b0fdad-4037-460c-9c92-290f5774ab2b/resource/c2fcc1e3-c38f-44ad-a0cf-e5ea2a6585b5/download/streetlight-locations.csv)
        url= dml.auth['services']['streetlight']['service']
        response = pandas.read_csv(url, encoding = "utf-8")
        response = response[['the_geom','OBJECTID','TYPE','Lat','Long']].copy()
        r = json.loads(response.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("street_light_location")
        repo.createCollection("street_light_location")
        repo['zhangyb.street_light_location'].insert_many(r)
        repo['zhangyb.street_light_location'].metadata({'complete':True})
        print(repo['zhangyb.street_light_location'].metadata())

        # 4: Crime Report (https://data.boston.gov/dataset/6220d948-eae2-4e4b-8723-2dc8e67722a3/resource/12cb3883-56f5-47de-afa5-3b1cf61b257b/download/tmpxjqz5gin.csv)
        url = dml.auth['services']['crimereport']['service']
        response = pandas.read_csv(url, encoding = "utf-8")
        response = response[['incident_number', 'year', 'month', 'lat', 'long', 'location']].copy()
        r = json.loads(response.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("crime_report")
        repo.createCollection("crime_report")
        repo['zhangyb.crime_report'].insert_many(r)
        repo['zhangyb.crime_report'].metadata({'complete':True})
        print(repo['zhangyb.crime_report'].metadata())

        # 5: Parking Meter Locations (https://opendata.arcgis.com/datasets/962da9bb739f440ba33e746661921244_9.csv)
        url = dml.auth['services']['parkingmeter']['service']
        response = pandas.read_csv(url, encoding = "utf-8")
        r = json.loads(response.to_json(orient='records'))
        s = json.dumps(r, sort_keys=True, indent=2)
        repo.dropCollection("parking_meter_location")
        repo.createCollection("parking_meter_location")
        repo['zhangyb.parking_meter_location'].insert_many(r)
        repo['zhangyb.parking_meter_location'].metadata({'complete':True})
        print(repo['zhangyb.parking_meter_location'].metadata())

        #repo.logout()

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
        repo.authenticate('zhangyb', 'zhangyb')
        
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/zhangyb/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/zhangyb/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('hub', 'http://hubwaydatachallenge.org/api/v1/')
        doc.add_namespace('mbta', 'https://api-v3.mbta.com/')
        doc.add_namespace('bos', 'https://data.boston.gov/dataset/')
        doc.add_namespace('arc', 'https://opendata.arcgis.com/datasets/')

        this_script = doc.agent('alg:zhangyb#retrieve',{prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

        resource1 = doc.entity('hub:station', {'prov:label':'Hubway Stations', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_hub = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_hub, this_script)
        doc.usage(get_hub, resource1, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})
        
        resource2 = doc.entity('mbta:stops', {'prov:label':'MBTA Stations', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_mbta = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_mbta, this_script)
        doc.usage(get_mbta, resource2, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        resource3 = doc.entity('bos:streetlight-locations', {'prov:label':'Street Light Locations', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_street_light = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_street_light, this_script)
        doc.usage(get_street_light, resource3, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query':'?type=Street+Light+Locations&$select=the_geom,OBJECTID,TYPE,Lat,Long'})

        resource4 = doc.entity('bos:tmpxjqz5gin', {'prov:label':'Crime Reports', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_crime_report = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_crime_report, this_script)
        doc.usage(get_crime_report, resource4, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval',
                   'ont:Query':'?type=Crime+Reports&$select=incident_number,lat,long,location'})

        resource5 = doc.entity('arc:962da9bb739f440ba33e746661921244_9', {'prov:label':'Parking Meter Locations', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
        get_parking_meter = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_parking_meter, this_script)
        doc.usage(get_parking_meter, resource5, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'})

        hub = doc.entity('dat:zhangyb#hub_station', {prov.model.PROV_LABEL:'Hubway Stations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(hub, this_script)
        doc.wasGeneratedBy(hub, get_hub, endTime)
        doc.wasDerivedFrom(hub, resource1, get_hub, get_hub, get_hub)

        mbta = doc.entity('dat:zhangyb#mbta_station', {prov.model.PROV_LABEL:'MBTA Stations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(mbta, this_script)
        doc.wasGeneratedBy(mbta, get_mbta, endTime)
        doc.wasDerivedFrom(mbta, resource2, get_mbta, get_mbta, get_mbta)

        street_light = doc.entity('dat:zhangyb#street_light_location', {prov.model.PROV_LABEL:'Street Light Locations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(street_light, this_script)
        doc.wasGeneratedBy(street_light, get_street_light, endTime)
        doc.wasDerivedFrom(street_light, resource3, get_street_light, get_street_light, get_street_light)

        crime_report = doc.entity('dat:zhangyb#crime_report', {prov.model.PROV_LABEL:'Crime Reports', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(crime_report, this_script)
        doc.wasGeneratedBy(crime_report, get_crime_report, endTime)
        doc.wasDerivedFrom(crime_report, resource4, get_crime_report, get_crime_report, get_crime_report)

        parking_meter = doc.entity('dat:zhangyb#parking_meter_location', {prov.model.PROV_LABEL:'Parking Meter Locations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(parking_meter, this_script)
        doc.wasGeneratedBy(parking_meter, get_parking_meter, endTime)
        doc.wasDerivedFrom(parking_meter, resource5, get_parking_meter, get_parking_meter, get_parking_meter)
        
        #repo.logout()

        return doc

'''
retrieve.execute()
doc = retrieve.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

#eof




        


       


