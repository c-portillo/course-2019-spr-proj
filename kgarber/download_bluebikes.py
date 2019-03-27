import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

# my imports
import csv
from tqdm import tqdm
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile

# This algorithm downloads the hubway dataset and stores it in mongodb.

# This is somewhat challenging as the dataset is split into months and I want
# all of 2018, so I loop through the months and format the URL to get all of 
# the months.

# It's also challenging because the dataset is stored in "zip" format, so I need
# to unzip it in python, read the file from the archive, parse it (it's in CSV 
# format), then save the data in MongoDB.

# To make matters worse, in the middle of 2018 hubway changed their name to
# "bluebikes", so now I have some logic which handles that... we'll refer to 
# all the data as bluebikes

class download_bluebikes(dml.Algorithm):
    contributor = 'kgarber'
    reads = []
    writes = ['kgarber.bluebikes', 'kgarber.bluebikes.stations']
    # fields to cast to int or float after downloading them
    fields_to_int = [
        "tripduration", 
        "start station id", 
        "end station id", 
        "bikeid", 
        "birth year", 
        "gender",
    ]
    fields_to_float = [
        "start station latitude",
        "start station longitude",
        "end station latitude",
        "end station longitude",
    ]

    @staticmethod
    def execute(trial = False):
        print("Starting download_bluebikes algorithm.")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgarber', 'kgarber')

        repo.dropCollection("bluebikes")
        repo.createCollection("bluebikes")

        # download the data for each month and insert it into MongoDB
        # https://s3.amazonaws.com/hubway-data/201812-hubway-tripdata.zip
        # [01, 02, 03, ... 10, 11, 12]
        # in month "05", the company name changed from hubway to bluebikes
        months = ["0" + str(i) if i < 10 else str(i) for i in range(1, 13)]
        name_from_month = lambda m: "hubway" if m < "05" else "bluebikes"
        month_tqdm = tqdm(months)
        for month in month_tqdm:
            company_name = name_from_month(month)
            month_tqdm.set_description("month %s - downloading" % month)
            url = "https://s3.amazonaws.com/hubway-data/2018%s-%s-tripdata.zip" % \
                (month, company_name)
            zip_urlopen = urllib.request.urlopen(url)
            # read the zip archive
            with ZipFile(BytesIO(zip_urlopen.read())) as current_zip_file:
                # we only have one file in the archive, get it
                filename = current_zip_file.namelist()[0]
                # open the file and parse the CSV
                with current_zip_file.open(filename) as opened_file:
                    current_csv = csv.DictReader(TextIOWrapper(opened_file))
                    # process the rows as necessary, this includes:
                    # 1) changing start time, stop time, and trip duration to timestamp
                    # 2) change start/end station ID to integer
                    # 3) change gender and birth year to int
                    # 4) change start/stop latitude/logitude to int
                    # additionally, build a list of dictionaries we can insert into mongodb
                    # also, for now, skip changing start and stop time so we dont' mess up time zones
                    result_rows = []
                    month_tqdm.set_description("month %s - parsing" % month)
                    for row_dict in current_csv:
                        row = {field: row_dict[field] for field in row_dict}
                        # format "2018-01-19 14:20:10"
                        # starttime = datetime.datetime.strptime(row["starttime"], "%Y-%m-%d %H:%M:%S").timestamp()
                        # cast strings to rows and ints
                        for field in download_bluebikes.fields_to_int:
                            # some birth years will be null, ignore it
                            if row[field] == "NULL":
                                if field != "birth year":
                                    print("caught null:", row)
                                row[field] = None
                            else:
                                row[field] = int(row[field])
                        for field in download_bluebikes.fields_to_float:
                            if row[field] == "NULL":
                                print("caught null:", row)
                                row[field] = None
                            else:
                                row[field] = float(row[field])
                        # one more thing - create a "startday" field which has just y/m/d
                        row["startday"] = row["starttime"][0:10];
                        result_rows.append(row)
                    month_tqdm.set_description("month %s - inserting" % month)
                    repo['kgarber.bluebikes'].insert_many(result_rows)
                    repo['kgarber.bluebikes'].metadata({'complete':True})

        # parse all of the bike stations from this data
        print("Parsing bike stations")
        repo.dropCollection("bluebikes.stations")
        repo.createCollection("bluebikes.stations")

        pipeline = [
            {"$project": 
                {
                    "stationId": "$start station id",
                    "name": "$start station name",
                    "stationLocation": {
                        "geometry": {
                            "type": "Point",  # GeoJson type
                            "coordinates": [  # GeoJson coordinates
                                "$start station longitude",
                                "$start station latitude"
                            ]
                        }
                    }
                }
            },
            {"$group": {
                "_id": "$stationId", 
                "stationId": {"$first": "$stationId"},
                "name": {"$first": "$name"},
                "location": {"$first": "$stationLocation"}
            }},
            {"$project": {"_id": 0}},
            {"$out": "kgarber.bluebikes.stations"}
        ]
        repo['kgarber.bluebikes'].aggregate(pipeline)
        # create index so we can do geojson search
        repo['kgarber.bluebikes.stations'].ensure_index([
            ("location.geometry", dml.pymongo.GEOSPHERE)
        ])
        repo['kgarber.bluebikes.stations'].metadata({'complete':True})

        repo.logout()
        endTime = datetime.datetime.now()
        print("Finished download_bluebikes algorithm.")
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # our data mechanics class namespaces
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')

        # specific namespaces
        doc.add_namespace('blb', 'https://www.bluebikes.com/system-data')

        # agent
        this_script = doc.agent(
            'alg:kgarber#download_bluebikes', 
            {
                prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 
                'ont:Extension':'py'
            })

        # entities
        resource = doc.entity(
            'blb:data2018',
            {
                'prov:label':'Bluebikes Dataset', 
                prov.model.PROV_TYPE:'ont:DataResource', 
                'ont:Extension':'csv'
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

        # activities
        get_bluebikes = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        generate_stations = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

        # wasAssociatedWith
        doc.wasAssociatedWith(get_bluebikes, this_script)
        doc.wasAssociatedWith(generate_stations, this_script)

        # usage
        doc.usage(get_bluebikes, resource, startTime, None,
            {
                prov.model.PROV_TYPE:'ont:Retrieval',
                'ont:Query':'https://s3.amazonaws.com/hubway-data/index.html'
            })
        doc.usage(generate_stations, resource, startTime, None,
                {prov.model.PROV_TYPE:'ont:Aggregate'})

        # relations for entities
        doc.wasAttributedTo(bluebikes, this_script)
        doc.wasGeneratedBy(bluebikes, get_bluebikes, endTime)
        doc.wasDerivedFrom(bluebikes, resource, get_bluebikes, get_bluebikes, get_bluebikes)

        doc.wasAttributedTo(bluebikes_stations, this_script)
        doc.wasGeneratedBy(bluebikes_stations, generate_stations, endTime)
        doc.wasDerivedFrom(bluebikes_stations, bluebikes, generate_stations, \
                generate_stations, generate_stations)

        # return the generated provenance document
        return doc

# download_bluebikes.execute()
