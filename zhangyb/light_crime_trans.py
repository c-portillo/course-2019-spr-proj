import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from math import acos, sin, cos, radians


class light_crime_trans(dml.Algorithm):
    contributor = 'zhangyb'
    reads = ['zhangyb.street_light_location',
             'zhangyb.crime_report']
    writes = ['zhangyb.light_crime']

    @staticmethod
    def execute(trial = False):

        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zhangyb', 'zhangyb')

        repo.dropPermanent("light_crime")
        repo.createPermanent("light_crime")

        # Retrieve data from MongoDB
        light = repo['zhangyb.street_light_location']
        crime = repo['zhangyb.crime_report']

        light_json = light.find()
        crime_json = crime.find()
        

        '''
        Tranformation 2:
        Calculate distances between street light locations and crime locations
        Although having street lights near the Hubway station is convenient, It might not be appropreate to set up a Hubway station near a crime location
        Differenciate the street light locations that are far from areas with high crime rate 
        '''

        light_data = {'Data': []}
        light_data_agg = {'Data': []}
        crime_data = {'Data': []}
        final_data = {'Data': []}
        # Used for custom ID
        count = 0
        # Used to form the data so that latitudes and longitudes from both datasets will have the same precision
        precision = '%.8f'
        # Average radius(km) of earth, used in distance() function
        earth_radius = 6371
        # Latitudes and Longitudes of the center of a circle used to lower the size of the dataset
        center_lat_lon = {'Latitudes': 42.3505, 'Longitudes': -71.1054} # BU by default
        # Radius(km) of the circle
        circle_radius = 3
        # Set a minimum distance(km) used to differenciate safer areas
        min_dist = 0.3
        # Set a limit to the size of the datasets for faster runtime. Also large limit will cause pymongo.errors.DocumentTooLarge(>= 500 approximately)
        limit = 400
        # Used to retrieve crime reports of a specific year
        crime_year = 2019

        # Helper function which calculates distance between two points given latitudes and longitudes 
        def distance(obj1, obj2):
            lat1 = radians(float(obj1['Latitudes']))
            lon1 = radians(float(obj1['Longitudes']))
            lat2 = radians(float(obj2['Latitudes']))
            lon2 = radians(float(obj2['Longitudes']))
            d = acos(sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(lon1 - lon2))
            return earth_radius*d

        # Helper function to differntiate datasets
        def difference(R, S):
            return [i for i in R for j in S if distance(i ,j) > min_dist]

        for obj in light_json:
            light_data['Data'] += [{'ID': count, 'Type': obj['TYPE'], 'Latitudes': precision%(obj['Lat']), 'Longitudes': precision%(obj['Long'])}]
            count += 1

        for obj in crime_json:
            if obj['year'] == crime_year:
                # Remove datasets with null
                if obj['lat'] is not None:
                    crime_data['Data'] += [{'ID': count, 'Type': 'Crime', 'Latitudes': obj['lat'], 'Longitudes': obj['long']}]
                    count += 1

        # Select datasets within a certain area
        light_data_agg['Data'] += [i for i in light_data['Data'] if distance(i, center_lat_lon) < circle_radius]

        final_data['Data'] += difference(light_data_agg['Data'][0:limit], crime_data['Data'][0:limit])

        repo['zhangyb.light_crime'].insert_one(final_data)
        repo['zhangyb.light_crime'].metadata({'complete':True})

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

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format. 
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format. 
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:zhangyb#light_crime_trans',{prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        get_light_crime = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_light_crime, this_script)

        light = doc.entity('dat:zhangyb#street_light_location', {prov.model.PROV_LABEL:'Street Light Locations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.usage(get_light_crime, light, startTime)

        crime = doc.entity('dat:zhangyb#crime_report', {prov.model.PROV_LABEL:'Crime Reports', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.usage(get_light_crime, crime, startTime)

        light_crime = doc.entity('dat:zhangyb#light_crime', {'prov:label':'Crime and Street Light Stations', prov.model.PROV_TYPE:'ont:Dataset'})

        doc.wasAttributedTo(light_crime, this_script)
        doc.wasGeneratedBy(light_crime, get_light_crime, endTime)
        doc.wasDerivedFrom(light_crime, light, get_light_crime, get_light_crime, get_light_crime)
        doc.wasDerivedFrom(light_crime, crime, get_light_crime, get_light_crime, get_light_crime)

        #repo.logout()

        return doc


light_crime_trans.execute()
doc = light_crime_trans.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))


