import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

# This algorithm creates 10 degree buckets from 0 to 100 and calculates the
# average day stats for each of those temperatures (average duration and 
# number of rides).

class rides_and_weather(dml.Algorithm):
    contributor = 'kgarber'
    reads = ['kgarber.bluebikes.rides_per_day', 'kgarber.weather']
    writes = [
        'kgarber.bluebikes.rides_and_weather',
        'kgarber.bluebikes.ride_weather_aggregate'
    ]
    @staticmethod
    def execute(trial = False):
        print("Starting rides_and_weather algorithm.")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgarber', 'kgarber')
        repo.dropCollection("bluebikes.rides_and_weather")
        repo.createCollection("bluebikes.rides_and_weather")
        repo.dropCollection("kgarber.bluebikes.ride_weather_aggregate")
        repo.createCollection("kgarber.bluebikes.ride_weather_aggregate")

        # describe the aggregation 
        # (applied to kgarber.bluebikes.rides_per_day)
        pipeline = [
            {"$lookup": 
                {
                    "from": "kgarber.weather",
                    "localField": "date",
                    "foreignField": "date",
                    "as": "weather"
                }
            },
            {"$project":
                {
                    "_id": 0, "date": 1, "numTrips": 1, "avgDuration": 1,
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
                    "date": 1, "numTrips": 1, "avgDuration": 1, "tempMin": 1, "tempMax": 1, "tempAvg": 1,
                    "tempMinBucket": {"$multiply": [{"$trunc": {"$divide": ["$tempMin", 10]}}, 10]},
                    "tempMaxBucket": {"$multiply": [{"$trunc": {"$divide": ["$tempMax", 10]}}, 10]},
                    "tempAvgBucket": {"$multiply": [{"$trunc": {"$divide": ["$tempAvg", 10]}}, 10]},
                }
            },
            {"$out": "kgarber.bluebikes.rides_and_weather"}
        ]
        # run the aggregation in mongodb
        repo['kgarber.bluebikes.rides_per_day'].aggregate(pipeline)
        # sort the rides into the buckets in a new collection
        pipeline2 = [
            {"$group": {
                "_id": "$tempAvgBucket",
                "avgTripsAtTemp": {"$avg": "$numTrips"},
                "avgTripDurationAtTemp": {"$avg": "$avgDuration"},
                "count": {"$sum": 1}
            }},
            {"$project": {
                "tempAvgBucket": "$_id",
                "_id": 0,
                "avgTripsAtTemp": {"$trunc": "$avgTripsAtTemp"},
                "avgTripDurationAtTemp": {"$trunc": "$avgTripDurationAtTemp"},
                "count": 1
            }},
            {"$sort": {"tempAvgBucket": 1}},
            {"$out": "kgarber.bluebikes.ride_weather_aggregate"}
        ]
        repo['kgarber.bluebikes.rides_and_weather'].aggregate(pipeline2)
        # indicate that the collection is complete
        repo['kgarber.bluebikes.rides_and_weather'].metadata({'complete':True})
        
        repo.logout()
        endTime = datetime.datetime.now()
        print("Finished rides_and_weather algorithm.")
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # our data mechanics class namespaces
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')

        this_script = doc.agent(
            'alg:kgarber#rides_and_weather', 
            {
                prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 
                'ont:Extension':'py'
            })
        bb_rides_per_day = doc.entity(
            'dat:kgarber#rides_per_day',
            {
                prov.model.PROV_LABEL:'Rides Per Day',
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        weather = doc.entity(
            'dat:kgarber#weather', 
            {
                prov.model.PROV_LABEL:'Boston Weather 2018', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        ride_weather_agg = doc.entity(
            'dat:kgarber#ride_weather_aggregate',
            {
                prov.model.PROV_LABEL: 'Ride Weather Aggregate',
                prov.model.PROV_TYPE: 'ont:DataSet'
            })

        gen_aggregate = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(gen_aggregate, this_script)
        doc.usage(gen_aggregate, bb_rides_per_day, startTime, None,
                {prov.model.PROV_TYPE:'ont:Aggregate'})
        doc.usage(gen_aggregate, weather, startTime, None,
                {prov.model.PROV_TYPE:'ont:Aggregate'})
        doc.wasAttributedTo(ride_weather_agg, this_script)
        doc.wasGeneratedBy(ride_weather_agg, gen_aggregate, endTime)
        doc.wasDerivedFrom(ride_weather_agg, bb_rides_per_day, gen_aggregate, gen_aggregate, gen_aggregate)
        doc.wasDerivedFrom(ride_weather_agg, weather, gen_aggregate, gen_aggregate, gen_aggregate)
        
        return doc

# rides_and_weather.execute()
# rides_and_weather.provenance()
