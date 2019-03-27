import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

from tqdm import tqdm

class university_bluebike_stations(dml.Algorithm):
    contributor = 'kgarber'
    reads = ['kgarber.bluebikes', 'kgarber.bluebikes.stations', 'kgarber.university']
    writes = ['kgarber.university_bluebike_stations']
    @staticmethod
    def execute(trial = False):
        print("Starting university_bluebike_stations algorithm.")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgarber', 'kgarber')

        repo.dropCollection("university_bluebike_stations")
        repo.createCollection("university_bluebike_stations")

        # describe the aggregation
        # get the universities with more than 500 students
        # find all bluebike stations within 1 mile of the university
        # run the aggregation in mongodb
        print("Finding universities of significant size.")
        repo['kgarber.university'].aggregate([
            {"$match": {"properties.NumStudent": {"$gt": 500}}},
            {"$out": "kgarber.university_bluebike_stations"}
        ])

        print("Finding nearest bike stations to each university")
        num_unis = 0
        for uni in repo['kgarber.university_bluebike_stations'].find():
            num_unis += 1
            nearest = repo['kgarber.bluebikes.stations'].find({"location.geometry": 
                {"$near": {
                    "$geometry": uni["geometry"],
                    "$maxDistance": 500  # 1/2 km. 1600m = 1 mile
                }}
            })
            nearest_stations = [n["stationId"] for n in nearest]
            repo['kgarber.university_bluebike_stations'].update(
                {"properties.Name": uni["properties"]["Name"]},
                {"$set":{"nearbyStations": nearest_stations}}
            )

        # For each university, find bluebike rides on monday through friday
        # which arrive at a station of the university between 7 and 11 AM. Count 
        # the most frequent stations to depart from to get to the university
        print("Finding most common departure location for getting to each university.")
        unis = [uni for uni in repo['kgarber.university_bluebike_stations'].find()]
        for uni in tqdm(unis):
            common_stations = repo['kgarber.bluebikes'].aggregate([
                {"$addFields": {
                    "startHour": {"$hour": {"$toDate": "$starttime"}},  # hour of the day
                    "startDay": {"$dayOfWeek": {"$toDate": "$starttime"}}  # day of the week
                }},
                {"$match": {
                    "end station id": {"$in": uni["nearbyStations"]},
                    "startHour": {"$gte": 7, "$lt": 11},  # between 7 and 11 AM
                    "startDay": {"$gte": 2, "$lte": 6}  # monday through friday
                }},
                {"$group": {
                    "_id": "$start station id",
                    "stationName": {"$first": "$start station name"},
                    "stationCount": {"$sum": 1}
                }},
                {"$sort": {"stationCount": -1}},
                {"$limit": 10}
            ])
            common = [cs for cs in common_stations]
            repo['kgarber.university_bluebike_stations'].update(
                {"properties.Name": uni["properties"]["Name"]},
                {"$set":{"commonStations": common}}
            )

        # indicate that the collection is complete
        repo['kgarber.university_bluebike_stations'].metadata({'complete':True})
        
        repo.logout()
        endTime = datetime.datetime.now()
        print("Finished university_bluebike_stations algorithm.")
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # our data mechanics class namespaces
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')

        this_script = doc.agent(
            'alg:kgarber#university_bluebike_stations', 
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
        bluebikes_stations = doc.entity(
            'dat:kgarber#bluebikes_stations', 
            {
                prov.model.PROV_LABEL:'Bluebikes Stations', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        university = doc.entity(
            'dat:kgarber#university', 
            {
                prov.model.PROV_LABEL:'Universities In Boston', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        common_stations = doc.entity(
            'dat:kgarber#common_stations',
            {
                prov.model.PROV_LABEL: 'Common BB Stations',
                prov.model.PROV_TYPE: 'ont:DataSet'
            })

        gen_stations = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(gen_stations, this_script)
        doc.usage(gen_stations, bluebikes, startTime, None,
            {prov.model.PROV_TYPE:'ont:Aggregate'})
        doc.usage(gen_stations, bluebikes_stations, startTime, None,
            {prov.model.PROV_TYPE:'ont:Aggregate'})
        doc.usage(gen_stations, university, startTime, None,
            {prov.model.PROV_TYPE:'ont:Aggregate'})
        doc.wasAttributedTo(common_stations, this_script)
        doc.wasGeneratedBy(common_stations, gen_stations, endTime)
        doc.wasDerivedFrom(common_stations, bluebikes,
                gen_stations, gen_stations, gen_stations)
        doc.wasDerivedFrom(common_stations, bluebikes_stations,
                gen_stations, gen_stations, gen_stations)
        doc.wasDerivedFrom(common_stations, university,
                gen_stations, gen_stations, gen_stations)
        
        # return the generated provenance document
        return doc

# university_bluebike_stations.execute()
# university_bluebike_stations.provenance()
