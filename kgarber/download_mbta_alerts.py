# Download alerts for all of the MBTA in 20 day windows (the API max is 31 days).

# Only keep alerts which satisfy one of the following:
# 1) stop_id is within a certain number of miles of Boston
# 2) route_id is green, blue, orange, or red
# 3) it's a bus which operates within Boston

# You may want to clean up the alerts by alert version (only keep the last version?)

# You may want to do some string searching for "delay" - the "effect" field only offers
# "DETOUR"s, not delay info (shows up as "OTHER_EFFECT").

# May want to string search for "weather", "snow", "rain", or "wind"

# May want to also read in files "lines" and "routes" (in the stops script) to better 
# find relevant alerts ("informed_entity" has a route and trip ID, which you can use to filter 
# out to boston trains or something of the sort)

# ........

# download data in 20 day intervals for the whole year, merge it all together in memory, 
# filter out data not from the Blue, Red, Green, or Orange line, filter out alert versions so 
# we keep only the most recent alert version (via alert_id?), only then insert to Mongo

# maybe have a separate collection of all alerts due to weather and traffic (this script can 
# generate two collections - one of boston trains and one of traffic and weather related delays)

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

from tqdm import tqdm

class download_mbta_alerts(dml.Algorithm):
    contributor = 'kgarber'
    reads = ['kgarber.mbta.stops', 'kgarber.mbta.lines', 'kgarber.mbta.routes']
    writes = ['kgarber.mbta.alerts']
    @staticmethod
    def execute(trial = False):
        print("Starting download_mbta_alerts algorithm.")
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('kgarber', 'kgarber')

        # get the relevant routes (green, orange, red, blue)
        lines = ["line-Blue", "line-Red", "line-Green", "line-Orange"]
        lines = repo['kgarber.mbta.routes'].find({"line_id": {"$in": lines}})
        routes = [l["route_id"] for l in lines]
        print("Related routes:", routes)

        repo.dropCollection("mbta.alerts")
        repo.createCollection("mbta.alerts")

        # timestamps for beginning of 2018 and 2019
        # split the year into 20 segments, since the API limits you to 1 month
        timestamp_2018 = 1514784800
        timestamp_2019 = 1546315800
        step_size = int((timestamp_2019 - timestamp_2018) / 20)

        # tqdm update strings
        # padded so that they're the same size (loading bar appearance)
        update_strs = ["downloading", "parsing", "counting"]
        longest = max([len(s) for s in update_strs])
        update_strs = [s.ljust(longest) for s in update_strs]

        total_lines = 0
        relevant_lines = 0
        times = tqdm(range(timestamp_2018, timestamp_2019, step_size))
        for t in times:
        	start_time = t
        	end_time = t + step_size
        	dev_key = dml.auth["services"]["mbta"]["dev-API-key"]
        	times.set_description(("(%s, %s) " % (relevant_lines, total_lines)) + update_strs[0])
        	url = (
        		"http://realtime.mbta.com/developer/api/v2.1/pastAlerts?" + 
        		"api_key=%s&format=json&from_datetime=%s&to_datetime=%s"
        	) % (dev_key, start_time, end_time)
        	response = urllib.request.urlopen(url).read().decode("utf-8")
        	r = json.loads(response)

        	relevant_alerts = []
        	past_alerts = r["past_alerts"]
        	for alert in past_alerts:
        		total_lines += 1
        		if len(alert["alert_versions"]) > 0:
        			for ent in alert["alert_versions"][-1]["informed_entity"]:
        				if "route_id" in ent and ent["route_id"] in routes:
        					relevant_lines += 1
        					# only the last relevant alert
        					this_alert = alert["alert_versions"][-1]
        					this_alert["date"] = (datetime.datetime.
        							fromtimestamp(int(this_alert["valid_from"])).
        							isoformat()[0:10])
        					relevant_alerts.append(this_alert)
        					break
        	if len(relevant_alerts) > 0:
        		repo['kgarber.mbta.alerts'].insert_many(relevant_alerts)

        # indicate that the collection is complete
        repo['kgarber.mbta.alerts'].metadata({'complete':True})
        
        repo.logout()
        endTime = datetime.datetime.now()
        print("Finished download_mbta_alerts algorithm.")
        return {"start":startTime, "end":endTime}
    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        # our data mechanics class namespaces
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
        doc.add_namespace('dat', 'http://datamechanics.io/data/')
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
        doc.add_namespace('log', 'http://datamechanics.io/log/')

        doc.add_namespace('mbta', 'https://www.mbta.com/developers')

        this_script = doc.agent(
            'alg:kgarber#download_mbta_alerts', 
            {
                prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 
                'ont:Extension':'py'
            })
       	resource = doc.entity(
            'mbta:alerts',
            {
                'prov:label':'MBTA Alerts Portal', 
                prov.model.PROV_TYPE:'ont:DataResource', 
                'ont:Extension':'json'
            })
        routes = doc.entity(
            'dat:kgarber#mbta_routes', 
            {
                prov.model.PROV_LABEL:'MBTA Routes', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })
        alerts = doc.entity(
            'dat:kgarber#mbta.alerts', 
            {
                prov.model.PROV_LABEL:'MBTA Alerts', 
                prov.model.PROV_TYPE:'ont:DataSet'
            })

        get_alerts = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_alerts, this_script)
        doc.usage(get_alerts, routes, startTime, None,
            {prov.model.PROV_TYPE:'ont:Select'})
        doc.usage(get_alerts, resource, startTime, None,
            {
                prov.model.PROV_TYPE:'ont:Retrieval',
                'ont:Query':('/api/v2.1/pastAlerts?api_key=ABCXYZ&format=json' +
                		'&from_datetime=timestamp&to_datetime=timestamp')
            })
        doc.wasAttributedTo(alerts, this_script)
        doc.wasGeneratedBy(alerts, get_alerts, endTime)
        doc.wasDerivedFrom(alerts, routes,
                get_alerts, get_alerts, get_alerts)
        doc.wasDerivedFrom(alerts, resource,
                get_alerts, get_alerts, get_alerts)
        
        # return the generated provenance document
        return doc

# download_mbta_alerts.execute()
# download_mbta_alerts.provenance()

