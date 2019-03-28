import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

# my imports
import bson.code

# This algorithm calculates the number of bluebike rides per day in 2018.
# It uses a mongodb MapReduce approach.
# Every ride turns into a {date -> 1} pair, then we aggregate with a sum
# for all rides.

class rides_per_day(dml.Algorithm):
    contributor = 'kgarber'
    reads = ['kgarber.bluebikes']
    writes = ['kgarber.bluebikes.rides_per_day']
    @staticmethod
    def execute(trial = False):
        print("Starting rides_per_day algorithm.")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgarber', 'kgarber')
        repo.dropCollection("bluebikes.rides_per_day")
        repo.createCollection("bluebikes.rides_per_day")

        # describe the aggregation
        # group by day, get the total trips and average trip duration per day
        # remove _id field, create a date field, and truncate average trip duration
        # sort by date
        pipeline = [
            {"$group": 
                {
                    "_id": "$startday", 
                    "numTrips": {"$sum": 1},
                    "avgDuration": {"$avg": "$tripduration"}
                }
            },
            {"$project": 
                {
                "date": "$_id", 
                "_id": 0,
                "numTrips": 1,
                "avgDuration": {"$trunc": "$avgDuration"}
                }
            },
            {"$sort": {"date": 1}},
            {"$out": "kgarber.bluebikes.rides_per_day"}
        ]
        # run the aggregation in mongodb
        repo['kgarber.bluebikes'].aggregate(pipeline)
        # indicate that the collection is complete
        repo['kgarber.bluebikes.rides_per_day'].metadata({'complete':True})
        
        repo.logout()
        endTime = datetime.datetime.now()
        print("Finished rides_per_day algorithm.")
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # our data mechanics class namespaces
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')

        this_script = doc.agent(
            'alg:kgarber#rides_per_day', 
            {
                prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 
                'ont:Extension':'py'
            })
        bluebikes = doc.entity(
            'dat:kgarber#bluebikes', 
            {
                prov.model.PROV_LABEL:'Bluebikes', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        bb_rides_per_day = doc.entity(
            'dat:kgarber#rides_per_day', 
            {
                prov.model.PROV_LABEL:'Rides Per Day', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        generate_rides = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(generate_rides, this_script)
        doc.usage(generate_rides, bluebikes, startTime, None,
                {prov.model.PROV_TYPE:'ont:Aggregate'})
        doc.wasAttributedTo(bb_rides_per_day, this_script)
        doc.wasGeneratedBy(bb_rides_per_day, generate_rides, endTime)
        doc.wasDerivedFrom(bb_rides_per_day, bluebikes, 
                generate_rides, generate_rides, generate_rides)
        
        return doc

# rides_per_day.execute()
