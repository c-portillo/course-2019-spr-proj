import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

# my imports
import csv

# This algorithm downloads historical weather data for Boston in 2018.
# The data is supplied by the NOAA (National Ocean and Atmospheric Association).
# The data is emailed to the requestor, so I will upload the data to the class
# dropbox and download it from there.

# after downlaoding the file, filter for a "NAME" of "BOSTON, MA US"
# keep the fields NAME, LATITUDE, LONGITUDE, DATE,
# PRCP (percipitation), TAVG, TMAX, TMIN.
# Transform the relevant fields from strings to numbers:
# lat, long, prcp = floats
# tmax, tmin, tavg = ints

class download_weather(dml.Algorithm):
    contributor = 'kgarber'
    reads = []
    writes = ['kgarber.weather']

    @staticmethod
    def execute(trial = False):
        print("Starting download_weather algorithm.")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgarber', 'kgarber')

        # download the data and insert it into MongoDB
        # https://data.boston.gov/dataset/colleges-and-universities
        url = 'http://datamechanics.io/data/kgarber/boston-weather-2018.csv'
        print("Downloading weather dataset.")
        response = urllib.request.urlopen(url).read().decode("utf-8")
        weather_csv = csv.DictReader(response.splitlines())
        result_rows = []
        for row in weather_csv:
            if row["NAME"] == "BOSTON, MA US":
                new_row = {
                    "name": row["NAME"],
                    "date": row["DATE"],
                    "latitude": float(row["LATITUDE"]),
                    "longitude": float(row["LONGITUDE"]),
                    "prcp": float(row["PRCP"]),
                    "tmax": int(row["TMAX"]),
                    "tmin": int(row["TMIN"]),
                    "tavg": int(row["TAVG"]),

                }
                result_rows.append(new_row)
        print("Saving weather dataset to MongoDB.")
        repo.dropCollection("weather")
        repo.createCollection("weather")
        repo['kgarber.weather'].insert_many(result_rows)
        repo['kgarber.weather'].metadata({'complete':True})

        # close the database connection and end the algorithm
        repo.logout()
        endTime = datetime.datetime.now()
        print("Done with download_weather algorithm.")
        return {"start":startTime, "end":endTime}
    
    # https://www.ncdc.noaa.gov/
    # https://www.ncdc.noaa.gov/cdo-web/
    # https://www.ncdc.noaa.gov/cdo-web/search
    # search queries: all of 2018, boston, temperature and percipitation
    # actual location: http://datamechanics.io/data/kgarber/boston-weather-2018.csv

    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # our data mechanics class namespaces
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')

        # the namespace for weather data
        doc.add_namespace('wth', 'https://www.ncdc.noaa.gov/cdo-web/')

        # the agent which is my algorithn
        this_script = doc.agent(
            'alg:kgarber#download_weather', 
            {
                prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 
                'ont:Extension':'py'
            })
        # the entity I am downloading
        resource = doc.entity(
            'wth:boston2018',
            {
                'prov:label':'Weather 2018', 
                prov.model.PROV_TYPE:'ont:DataResource', 
                'ont:Extension':'csv'
            })
        # the activity of downloading this dataset (log the timing)
        get_weather = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        # the activity is associated with the agent
        doc.wasAssociatedWith(get_weather, this_script)
        # log an invocation of the activity
        doc.usage(get_weather, resource, startTime, None,
            {
                prov.model.PROV_TYPE:'ont:Retrieval',
                'ont:Query':'?city=boston&date=2018'
            })
        # the newly generated entity
        weather = doc.entity(
            'dat:kgarber#weather', 
            {
                prov.model.PROV_LABEL:'Boston Weather 2018', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        # relations for the above entity
        doc.wasAttributedTo(weather, this_script)
        doc.wasGeneratedBy(weather, get_weather, endTime)
        doc.wasDerivedFrom(weather, resource, get_weather, get_weather, get_weather)
        
        # return the generated provenance document
        return doc
