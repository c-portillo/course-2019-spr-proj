
# Calculate the average number of alerts as compared to the
# temperature outside

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

from tqdm import tqdm

class alerts_and_weather(dml.Algorithm):
    contributor = 'kgarber'
    reads = ['kgarber.weather', 'kgarber.mbta.alerts']
    writes = ['kgarber.alerts_and_weather']
    @staticmethod
    def execute(trial = False):
        print("Starting alerts_and_weather algorithm.")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgarber', 'kgarber')
        repo.dropCollection("alerts_and_weather")
        repo.createCollection("alerts_and_weather")

        repo['kgarber.mbta.alerts'].aggregate([
            {"$project": {
                "date": 1,
                "numAlerts": {"$literal": 1}
            }},
            {"$group": {
                "_id": "$date",
                "totalAlerts": {"$sum": "$numAlerts"}
            }},
            {"$lookup": {
                "from": "kgarber.weather",
                "localField": "_id",
                "foreignField": "date",
                "as": "weather"
            }},
            {"$project":
                {
                    "_id": 0, "date": "$date", "totalAlerts": 1,
                    "tempMin": "$weather.tmin",
                    "tempMax": "$weather.tmax",
                    "tempAvg": "$weather.tavg"
                }
            },
            {"$unwind": "$tempMin"},
            {"$unwind": "$tempMax"},
            {"$unwind": "$tempAvg"},
            {"$project": 
                {
                    "date": 1, "totalAlerts": 1, "tempMin": 1, "tempMax": 1, "tempAvg": 1,
                    "tempMinBucket": {"$multiply": [{"$trunc": {"$divide": ["$tempMin", 10]}}, 10]},
                    "tempMaxBucket": {"$multiply": [{"$trunc": {"$divide": ["$tempMax", 10]}}, 10]},
                    "tempAvgBucket": {"$multiply": [{"$trunc": {"$divide": ["$tempAvg", 10]}}, 10]},
                }
            },
            {"$group": {
                "_id": "$tempAvgBucket",
                "avgAlertsAtTemp": {"$avg": "$totalAlerts"},
                "count": {"$sum": 1}
            }},
            {"$project": {
                "tempAvgBucket": "$_id",
                "_id": 0,
                "avgAlertsAtTemp": {"$trunc": "$avgAlertsAtTemp"},
                "count": 1
            }},
            {"$sort": {"tempAvgBucket": 1}},
            {"$out": "kgarber.alerts_and_weather"}
        ])

        # indicate that the collection is complete
        repo['kgarber.alerts_and_weather'].metadata({'complete':True})
        
        repo.logout()
        endTime = datetime.datetime.now()
        print("Finished alerts_and_weather algorithm.")
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # our data mechanics class namespaces
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')

        this_script = doc.agent(
            'alg:kgarber#alerts_and_weather', 
            {
                prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 
                'ont:Extension':'py'
            })
        alerts = doc.entity(
            'dat:kgarber#mbta.alerts', 
            {
                prov.model.PROV_LABEL:'MBTA Alerts', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        weather = doc.entity(
            'dat:kgarber#weather', 
            {
                prov.model.PROV_LABEL:'Boston Weather 2018', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        alert_weather_aggregate = doc.entity(
            'dat:kgarber#alerts_and_weather', 
            {
                prov.model.PROV_LABEL:'Alerts and Weather', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })

        get_averages = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_averages, this_script)
        doc.usage(get_averages, alerts, startTime, None,
            {prov.model.PROV_TYPE:'ont:Select'})
        doc.usage(get_averages, weather, startTime, None,
            {prov.model.PROV_TYPE:'ont:Join'})
        doc.wasAttributedTo(alert_weather_aggregate, this_script)
        doc.wasGeneratedBy(alert_weather_aggregate, get_averages, endTime)
        doc.wasDerivedFrom(alert_weather_aggregate, weather,
                get_averages, get_averages, get_averages)
        doc.wasDerivedFrom(alert_weather_aggregate, alerts,
                get_averages, get_averages, get_averages)
        
        # return the generated provenance document
        return doc

# alerts_and_weather.execute()
# alerts_and_weather.provenance()

