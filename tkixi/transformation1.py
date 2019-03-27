import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import requests 

# pip install opencage
from opencage.geocoder import OpenCageGeocode
from pprint import pprint


# Are the hubway stations in an area where it is bike friendly (hubway station street == bike lane street)
class transformation1(dml.Algorithm):
    contributor = 'tkixi'
    reads = ['tkixi.boston_bikes', 'tkixi.boston_hubway']
    writes = ['tkixi.hubway_network']

    @staticmethod
    def execute(trial = False):

        def select(R, s):
            return [t for t in R if s(t)]
        def project(R, p):
            return [p(t) for t in R]

        # gets rid of values that don't make sense: installed at year 0
        def ridOf0(t):
            return t['installed'] != 0

        print("in transformation 1")
        
        startTime = datetime.datetime.now()
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('tkixi', 'tkixi')

        bl = repo.tkixi.boston_bikes
        bh = repo.tkixi.boston_hubway


        # Boston Bike Network 
        # InstalledAt, Street Name
        bikeNetwork = bl.find()
        print("###PRINTED BIKE NETWORK###")

        # project for street name and date of installment
        bike_filter = lambda x: {'street': x['STREET_NAM'],
                                    'installed': x['InstallDat']}
        bike_project = project(bikeNetwork, bike_filter)
        # remove duplicate streets
        no_dupes = [i for n, i in enumerate(bike_project) if i not in bike_project[n + 1:]]

        # select to get rid of entries with installed at year 0
        clean_data = select(no_dupes, ridOf0)
        bike_data = clean_data
        # data is list



        # Boston Hubway Station
        # Convert lat lng to street name
        hubwayStation = bh.find()
        print("###PRINTED HUBWAY STATIONS###")
        api_key = dml.auth['services']['openCagePortal']['api_key']
        geocoder = OpenCageGeocode(api_key)

        # dictionary of street names with hubway stations in Boston
        selected = {}
        api_limit = 0
        for x in hubwayStation:
            lat = x['Latitude']
            lng = x['Longitude']
            api_limit+=1
            results = geocoder.reverse_geocode(lat, lng)

            if 'road' in results[0]['components']:
                street = results[0]['components']['road']
                selected.update({street: 1})
            if api_limit >= 2500: # exceed api requests per day
                break
            # print(results)
            # print(selected)
            
        print("Length of selected", len(selected))
        print("unique streets",len(bike_data))

        # compare dictionary of hubway station street names with bike network data
        hubwayNetwork = []
        # hasHubwayStation = 1 is yes and 0 is no
        # print('bike data', len(bike_data))
        for x in bike_data:
            # print(x)
            if x['street'] in selected:
                # print('x',x)
                x.update({'hasHubwayStation': 1})
                hubwayNetwork.append(x)
            else:
                x.update({'hasHubwayStation': 0})
                hubwayNetwork.append(x)
        # print(hubwayNetwork)

                

        repo.dropCollection("tkixi.hubway_network")
        repo.createCollection("tkixi.hubway_network")

        repo['tkixi.hubway_network'].insert_many(hubwayNetwork)
        print("Done with Transformation 1")

        repo.logout()
        endTime = datetime.datetime.now()
        return {"start":startTime, "end":endTime}



    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('tkixi', 'tkixi')
        
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/?prefix=tkixi/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')
        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
        doc.add_namespace('cdp', 'https://data.cambridgema.gov/resource/')
        
        
        this_script = doc.agent('alg:tkixi#transformation1', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource1 = doc.entity('dat:tkixi#bikeNetwork', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        resource2 = doc.entity('dat:tkixi#hubwayStation', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        
        transformation1 = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(transformation1, this_script)

        doc.usage(transformation1, resource1, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Calculation',
                  'ont:Query':''
                  }
                  )
        doc.usage(transformation1, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Calculation',
                  'ont:Query':''
                  }
                  )

        bikelaneHubway = doc.entity('dat:tkixi#bikelaneHubway', {prov.model.PROV_LABEL:'Analyzes all bike lanes and if they have a Hubway Station on the same street', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(bikelaneHubway, this_script)
        doc.wasGeneratedBy(bikelaneHubway, transformation1, endTime)
        doc.wasDerivedFrom(bikelaneHubway, resource1, transformation1, transformation1, transformation1)
        doc.wasDerivedFrom(bikelaneHubway, resource2, transformation1, transformation1, transformation1)


        repo.logout()
        
        return doc

# transformation1.execute()
# doc = transformation1.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof