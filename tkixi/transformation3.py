import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from pprint import pprint
from collections import defaultdict
from opencage.geocoder import OpenCageGeocode




#Bike Collisions + Weather (bike_weather)
    # how strong boston wind is during bike collisions or not on a monthly basis along with the
    # number of accidents per month
class transformation3(dml.Algorithm):
    contributor = 'tkixi'
    reads = ['tkixi.boston_collisions', 'tkixi.boston_weather']
    writes = ['tkixi.weather_collision']


    @staticmethod
    def execute(trial = False):

        def select(R, s):
            return [t for t in R if s(t)]
        def project(R, p):
            return [p(t) for t in R]
            

        print("in transformation 3")
        
        
        startTime = datetime.datetime.now()
        
        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('tkixi', 'tkixi')

        bc = repo.tkixi.boston_collisions
        bw = repo.tkixi.boston_weather



        # Boston Collisions 
        # mode_type, xstreet1, xstreet2
        bostonCollisions = bc.find()
        print("###PRINTED Bike Collisions###")

        # select to get all bike collisions
        bikeCollisions = select(bostonCollisions, lambda x: x['mode_type'] == 'bike')

        # get lat lng
        collision_filter = lambda x: {'timestamp': x['dispatch_ts'],
                                        'lat': x['lat'],
                                        'lng': x['long']
                                     }
        collision_project = project(bikeCollisions, collision_filter)
        # {"dispatch_ts": "2015-01-01 03:50:33",
        # "lat": 42.2570810965,
        # "long": -71.1201108871
        #  }
        api_key = dml.auth['services']['openCagePortal']['api_key']
        geocoder = OpenCageGeocode(api_key)

        # dictionary of street names with hubway stations in Boston
        selected = {}
        api_limit = 0
        collisionCity = []
        for x in collision_project:
            lat = x['lat']
            lng = x['lng']
            api_limit+=1
            # x.update({'city': 'Boston'})
            # collisionCity.append(x)
            
            # reverse geocode the lat lng of the collision and cross reference the city with city's weather
            results = geocoder.reverse_geocode(lat, lng)
            if 'city' in results[0]['components']:
                x.update({'city': (results[0]['components']['city'])})
                collisionCity.append(x)

            if api_limit >= 2500: # exceed api requests per day -- reduce to 100 if you want it to run faster
                break


        # Boston Weather
          #  {
          #   "STATION": "USW00014739",
          #   "NAME": "BOSTON, MA US",
          #   "DATE": "2015-01-01",
          #   "AWND": 14.32,
          #   "PGTM": "",
          #   "PRCP": 0,
          #   "SNOW": 0,
          #   "TAVG": 26,
          #   "TMAX": 33,
          #   "TMIN": 22,
          #   "WDF2": 230,
          #   "WDF5": 210,
          #   "WSF2": 23,
          #   "WSF5": 29.1,
          #   "WT01": "",
          #   "WT02": "",
          #   "WT03": "",
          #   "WT04": "",
          #   "WT05": "",
          #   "WT06": "",
          #   "WT08": "",
          #   "WT09": ""
          # },
        bostonWeather = bw.find()

        collision_weather = []
        # iterate boston's weather
        for k in bostonWeather:
            for l in collisionCity:
                date = l['timestamp'].split()[0]
                city = k['NAME'].split()[0][:-1]
                if l['city'].upper() == city and date == k['DATE']:
                    # found collision day's weather
                    # we want to find out average wind speed and the month
                    month = date[5:7] #month
                    wind_collisions = {}
                    wind_collisions.update({'month': month, 'wind': k['AWND']})
                    collision_weather.append(wind_collisions)
        # pprint(collision_weather)
        months = ['01','02','03','04','05','06','07','08','09','10','11','12']
        avg_wind = {}
        monthly_wind =[]
        for x in months:
            count = 0
            total_wind = 0
            avg_wind = {}
            for y in collision_weather: 
                if y['month'] == x:
                    count+=1
                    total_wind += y['wind']
                    avg_wind.update({'month': x, 'wind': total_wind, 'accidents': count})
                    monthly_wind.append(avg_wind)
        
        # averaging wind speed
        minify = []

        for x in months:
            for y in monthly_wind:
                if x == y['month']:
                    avg = y['wind'] / y['accidents']
                    minify.append({'month': x, 'average_wind': avg, 'accidents': y['accidents']})
        result = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in minify)]
        pprint(result)

        repo.dropCollection("tkixi.weather_collision")
        repo.createCollection("tkixi.weather_collision")

        repo['tkixi.weather_collision'].insert_many(result)
        print("Done with Transformation 3")

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
        
        this_script = doc.agent('alg:tkixi#transformation3', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        resource1 = doc.entity('dat:tkixi#crashRecords', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        resource2 = doc.entity('dat:tkixi#bostonWeather', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        
        transformation3 = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(transformation3, this_script)

        doc.usage(transformation3, resource1, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Calculation',
                  'ont:Query':''
                  }
                  )
        doc.usage(transformation3, resource2, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Calculation',
                  'ont:Query':''
                  }
                  )

        weatherCollision = doc.entity('dat:tkixi#weatherCollision', {prov.model.PROV_LABEL:'Average Wind Speed on a monthly basis in regards to bike collisions', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.wasAttributedTo(weatherCollision, this_script)
        doc.wasGeneratedBy(weatherCollision, transformation3, endTime)
        doc.wasDerivedFrom(weatherCollision, resource1, transformation3, transformation3, transformation3)
        doc.wasDerivedFrom(weatherCollision, resource2, transformation3, transformation3, transformation3)
        


        repo.logout()
        
        return doc

# transformation3.execute()
# doc = transformation3.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof