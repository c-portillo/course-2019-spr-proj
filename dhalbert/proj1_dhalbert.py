import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class example(dml.Algorithm):
    contributor = 'dhalbert'
    reads = []
    writes = ['dhalbert.hub','dhalbert.mbta_station','dhalbert.blue','dhalbert.bluebike_station','dhalbert.crimes','dhalbert.crime_fixed','dhalbert.tls']

    @staticmethod
    def execute(trial = False):
        '''Retrieve some data sets (not using the API here for the sake of simplicity).'''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('dhalbert', 'dhalbert')

        #Dataset 1: Hubway Stations
        url='http://hubwaydatachallenge.org/api/v1/station/?format=json&username=csuksangium&api_key=a94a345a88c6b2fb455227cfacb5612b10b2f0bc'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        rr = json.loads(s)
        repo.dropCollection("hub")
        repo.createCollection("hub")
        repo['dhalbert.hub'].insert_one(rr)
        repo['dhalbert.hub'].metadata({'complete':True})
        print(repo['dhalbert.hub'].metadata())

        #Dataset 2: Traffic Lights in Boston
        url='http://datamechanics.io/data/Traffic_Signals%20(2).geojson'
        response3 = urllib.request.urlopen(url).read().decode("utf-8")
        tl_json = json.loads(response3)
        repo.dropCollection("tls")
        repo.createCollection("tls")
        repo['dhalbert.tls'].insert_one(rr)
        repo['dhalbert.tls'].metadata({'complete':True})
        print(repo['dhalbert.tls'].metadata())


        #Dataset 3: MBTA Stops
        #Transformation 1 & 2: Combine MBTA Stops with Hubway Stops to determine distance, Comebine Traffic Lights to determine density
        #
        #  This dataset contains all the traffic lights, hubway stations and MBTA stops in the given border.
        #
        url='http://datamechanics.io/data/Traffic_Signals%20(2).geojson'
        hubway_url = 'http://hubwaydatachallenge.org/api/v1/station/?format=json&username=csuksangium&api_key=a94a345a88c6b2fb455227cfacb5612b10b2f0bc'
        mbta_url = 'https://api-v3.mbta.com/stops'
        response1 = urllib.request.urlopen(mbta_url).read().decode("utf-8")
        response2 = urllib.request.urlopen(hubway_url).read().decode("utf-8")
        response3 = urllib.request.urlopen(url).read().decode("utf-8")

        mbta_json = json.loads(response1)
        hubway_json = json.loads(response2)
        tl_json = json.loads(response3)

        #ID, type, latitudes, longitudes
        hubway_mbta = {'Entries':[]}
        hubway_mbta['Entries'] += [{'Id':0000,'Type':'mbta','coordinates':[10,5]}]

        for i in range(len(hubway_json['objects'])):
            # Filtering out some data that I would not like to use
            #       - Box Around Boston
            #       Coordinates found using https://www.latlong.net/
            if ((hubway_json['objects'][i]['point']['coordinates'][1]) < 42.422130 and (hubway_json['objects'][i]['point']['coordinates'][0]) > -71.160146):
                hubway_mbta['Entries'] += [{'ID':i,'Type':'Hubway','Latitudes':hubway_json['objects'][i]['point']['coordinates'][1],'Longitudes':hubway_json['objects'][i]['point']['coordinates'][0]}]

        for i in range(len(list(mbta_json['data']))):
            # Filtering out some data that I would not like to use
            #       - Box Around Boston
            #       Coordinates found using https://www.latlong.net/
            if ((mbta_json['data'][i]['attributes']['longitude']) > -71.160146 and (mbta_json['data'][i]['attributes']['latitude']) < 42.422130):
                hubway_mbta['Entries'] += [{'ID':i + len(hubway_json['objects']),'Type':'MBTA Stops','Latitudes':mbta_json['data'][i]['attributes']['latitude'],'Longitudes':mbta_json['data'][i]['attributes']['longitude']}]

        for i in range(len(tl_json['features'])):
            # Filtering out some data that I would not like to use
            #       - Box Around Boston
            #       Coordinates found using https://www.latlong.net/
            if ((tl_json['features'][0]['geometry']['coordinates'][1]) < 42.422130 and (tl_json['features'][0]['geometry']['coordinates'][0]) > -71.160146):
                hubway_mbta['Entries'] += [{'ID':i,'Type':'Traffic Lights','Latitudes':tl_json['features'][0]['geometry']['coordinates'][1],'Longitudes':tl_json['features'][0]['geometry']['coordinates'][0]}]

        repo.dropCollection("mbta_station")
        repo.createCollection("mbta_station")
        repo['dhalbert.mbta_station'].insert_one(hubway_mbta)
        repo['dhalbert.mbta_station'].metadata({'complete':True})
        print(repo['dhalbert.mbta_station'].metadata())

        #Dataset 4: Bluebike(Hubway) More informative data
        url='https://member.bluebikes.com/data/stations.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        rr = json.loads(s)
        repo.dropCollection("blue")
        repo.createCollection("blue")
        repo['dhalbert.blue'].insert_one(rr)
        repo['dhalbert.blue'].metadata({'complete':True})
        print(repo['dhalbert.blue'].metadata())

        #Transformation 3: Combine MBTA Stops with Empty BlueBikes(Hubway) Racks to see which d
        bluebike_url = 'https://member.bluebikes.com/data/stations.json'
        mbta_url2 = 'https://api-v3.mbta.com/stops'
        response3 = urllib.request.urlopen(mbta_url).read().decode("utf-8")
        response4 = urllib.request.urlopen(bluebike_url).read().decode("utf-8")

        mbta_json2 = json.loads(response3)
        bluebike_json = json.loads(response4)

        #ID, type, latitudes, longitudes
        bluebike_mbta = {'Entries':[]}
        bluebike_mbta['Entries'] += [{'Id':0000,'Type':'mbta','coordinates':[10,5]}]

        #for i in range(1):
        #    print(bluebike_json['stations'][i]['la'])

        for i in range(len(bluebike_json['stations'])):
            # Filtering out some data that I would not like to use
            #       - Box Around Boston
            #       - Calculating Empty Bike Racks
            #       Coordinates found using https://www.latlong.net/
            if ((bluebike_json['stations'][i]['la']) < 42.422130 and (bluebike_json['stations'][i]['lo']) > -71.160146 and (bluebike_json['stations'][i]['ba']) == 0):
                bluebike_mbta['Entries'] += [{'ID':i,'Type':'Bluebike','Latitudes':bluebike_json['stations'][i]['la'],'Longitudes':bluebike_json['stations'][i]['lo']}]

        for i in range(len(list(mbta_json['data']))):

            # Filtering out some data that I would not like to use
            #       - Box Around Boston
            #       Coordinates found using https://www.latlong.net/
            if ((mbta_json['data'][i]['attributes']['longitude']) > -71.160146 and (mbta_json['data'][i]['attributes']['latitude']) < 42.422130):
                bluebike_mbta['Entries'] += [{'ID':i + len(bluebike_json['stations']),'Type':'MBTA Stops','Latitudes':mbta_json['data'][i]['attributes']['latitude'],'Longitudes':mbta_json['data'][i]['attributes']['longitude']}]
        repo.dropCollection("bluebike_station")
        repo.createCollection("bluebike_station")
        repo['dhalbert.bluebike_station'].insert_one(bluebike_mbta)
        repo['dhalbert.bluebike_station'].metadata({'complete':True})
        print(repo['dhalbert.bluebike_station'].metadata())


        #Dataset 5: Crime data for Boston
        url='http://datamechanics.io/data/crimes_boston.json'
        response = urllib.request.urlopen(url).read().decode("utf-8")
        r = json.loads(response)
        s = json.dumps(r, sort_keys=True, indent=2)
        rr = json.loads(s)
        repo.dropCollection("crimes")
        repo.createCollection("crimes")
        repo['dhalbert.crimes'].insert_one(rr)
        repo['dhalbert.crimes'].metadata({'complete':True})
        print(repo['dhalbert.crimes'].metadata())

        #Transformation 4: Make Crime dataset more legible for purposes including:
        #   - Only include robberies 
        crime_url = 'http://datamechanics.io/data/crimes_boston.json'
        response5 = urllib.request.urlopen(crime_url).read().decode("utf-8")

        crime_json = json.loads(response5)

        #ID, type, latitudes, longitudes
        crime_data = {'Entries':[]}

        for i in range(len(crime_json['records'])):
            if ((crime_json['records'][i][2]) == crime_json['records'][1][2] or (crime_json['records'][i][2]) == crime_json['records'][0][2]):
                crime_data['Entries'] += [{'ID':i,'Type':'Crime','Type':crime_json['records'][i][2],'Coordinates':crime_json['records'][i][19],'Time':crime_json['records'][i][6]}]
     
        repo.dropCollection("crime_fixed")
        repo.createCollection("crime_fixed")
        repo['dhalbert.crime_fixed'].insert_one(crime_data)
        repo['dhalbert.crime_fixed'].metadata({'complete':True})
        print(repo['dhalbert.crime_fixed'].metadata())




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
        repo.authenticate('dhalbert', 'dhalbert')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

        this_script = doc.agent('alg:dhalbert#example', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})

        get_hub = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_mbta = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_streetlight = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_crime = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_crime_fixed = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_bluebike = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        get_blue = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.usage(get_hub, resource, startTime, None,
        {prov.model.PROV_TYPE:'ont:Retrieval',
            'ont:Query':'?type=Hubway+Station&$select=meta,objects'
            }
            )
        doc.usage(get_crime, resource, startTime, None,
        {prov.model.PROV_TYPE:'ont:Retrieval',
            'ont:Query':'?type=Crime&$select=meta,objects'
            }
            )
        doc.usage(get_blue, resource, startTime, None,
        {prov.model.PROV_TYPE:'ont:Retrieval',
            'ont:Query':'?type=Blue&$select=meta,objects'
            }
            )
        doc.usage(get_mbta, resource, startTime, None,
            {prov.model.PROV_TYPE:'ont:Retrieval',
            'ont:Query':'?type=MBTA+Stop&$select=links,included,data,links,id,attributes'
            }
            )
        doc.usage(get_streetlight, resource, startTime, None,
            {prov.model.PROV_TYPE:'ont:Retrieval',
            'ont:Query':'?type=Streetlight+Location&$select=the_geom,OBJECTID,TYPE,Lat,Long'
            }
            )
        doc.usage(get_bluebike, resource, startTime, None,
            {prov.model.PROV_TYPE:'ont:Retrieval',
            'ont:Query':'?type=Bluebike+Location&$select=links,included,data,links,attributes,stations,Lat,Long'
            }
            )
        doc.usage(get_crime_fixed, resource, startTime, None,
            {prov.model.PROV_TYPE:'ont:Retrieval',
            'ont:Query':'?type=Crimes+Fixed&$select=links,included,id,type'
            }
            )

        hub = doc.entity('dat:dhalbert#hub', {prov.model.PROV_LABEL:'Hubway Stations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(hub, this_script)
        doc.wasGeneratedBy(hub, get_hub, endTime)
        doc.wasDerivedFrom(hub, resource, get_hub, get_hub, get_hub)

        blue2 = doc.entity('dat:dhalbert#blue', {prov.model.PROV_LABEL:'Bluebike Statistics', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(hub, this_script)
        doc.wasGeneratedBy(hub, get_hub, endTime)
        doc.wasDerivedFrom(hub, resource, get_hub, get_hub, get_hub)

        bluebike = doc.entity('dat:dhalbert#bluebike_mbta', {prov.model.PROV_LABEL:'Bluebike Stations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(hub, this_script)
        doc.wasGeneratedBy(hub, get_hub, endTime)
        doc.wasDerivedFrom(hub, resource, get_hub, get_hub, get_hub)

        mbta = doc.entity('dat:dhalbert#mbta_station', {prov.model.PROV_LABEL:'MBTA Stations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(mbta, this_script)
        doc.wasGeneratedBy(mbta, get_mbta, endTime)
        doc.wasDerivedFrom(mbta, resource, get_mbta, get_mbta, get_mbta)

        streetlight = doc.entity('dat:dhalbert#tls', {prov.model.PROV_LABEL:'Streetlight locations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(streetlight, this_script)
        doc.wasGeneratedBy(streetlight, get_streetlight, endTime)
        doc.wasDerivedFrom(streetlight, resource, get_streetlight, get_streetlight, get_streetlight)

        crime = doc.entity('dat:dhalbert#crime', {prov.model.PROV_LABEL:'Crime rates and location', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(crime, this_script)
        doc.wasGeneratedBy(crime, get_crime, endTime)
        doc.wasDerivedFrom(crime, resource, get_crime, get_crime, get_crime)

        crime_fixed2 = doc.entity('dat:dhalbert#crime_fixed', {prov.model.PROV_LABEL:'Crime rates and location', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(crime, this_script)
        doc.wasGeneratedBy(crime, get_crime, endTime)
        doc.wasDerivedFrom(crime, resource, get_crime, get_crime, get_crime)





        repo.logout()
                  
        return doc


# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
example.execute()
doc = example.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof