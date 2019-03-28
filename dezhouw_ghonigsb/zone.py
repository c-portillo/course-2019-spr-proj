# zone.py
# created on Mar 8, 2019

import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import ssl
import sys
import traceback
import csv
import xmltodict
import io
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

class zone(dml.Algorithm):
	contributor = "dezhouw_ghonigsb"
	reads       = []
	writes      = ["zone"]

	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()

		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo   = client.repo
		repo.authenticate("dezhouw_ghonigsb", "dezhouw_ghonigsb")

		# # Drop all collections
		# collection_names = repo.list_collection_names()
		# for collection_name in collection_names:
		# 	repo.dropCollection(collection_name)

		# zoning_subdistricts
		collection_name = "zoning_subdistricts"
		url             = "https://opendata.arcgis.com/datasets/b601516d0af44d1c9c7695571a7dca80_0.geojson"
		gcontext        = ssl.SSLContext()
		response        = urllib.request.urlopen(url, context=gcontext).read().decode("utf-8")
		r_zone          = json.loads(response)
		print("Success: [{}]".format(collection_name))

		# zillow_boston_neighborhood
		collection_name = "zillow_boston_neighborhood"
		params          = {
			'zws-id'   : dml.auth["census"]["Zillow API"]["zws-id"],
			'state'    : 'ma',
			'city'     : 'boston',
			'childtype': 'neighborhood'
		}
		args            = urllib.parse.urlencode(params).encode('UTF-8')
		url             = "https://www.zillow.com/webservice/GetRegionChildren.htm?"
		gcontext        = ssl.SSLContext()
		response        = urllib.request.urlopen(url, args, context=gcontext).read().decode("utf-8")
		r_zillow        = xmltodict.parse(response)
		print("Success: [{}]".format(collection_name))

		collection_name = "zone"
		repo.dropCollection(collection_name)
		repo.createCollection(collection_name)

		for region in r_zillow["RegionChildren:regionchildren"]["response"]["list"]["region"]:
			name = region["name"]
			if ("zindex" not in region.keys()):
				continue
			money = float(region["zindex"]["#text"])
			x = float(region["latitude"])
			y = float(region["longitude"])
			point = Point(x, y)
			found = False
			for zone in r_zone["features"]:
				district_name = zone["properties"]["DISTRICT"]
				for list_coord in zone["geometry"]["coordinates"]:
					try:
						polygon = Polygon(list_coord)
						if (polygon.contains(point)):
							found = True
							entry = {
								"name": name,
								"money": money,
								"latitude": x,
								"longitude": y,
								"district": district_name
							}
							repo["dezhouw_ghonigsb."+collection_name].insert_one(entry)
							break
					except:
						continue
				if (found):
					break

		repo["dezhouw_ghonigsb."+collection_name].metadata({'complete':True})


        # Disconnect database for data safety
		repo.logout()

		endTime = datetime.datetime.now()
		return {"start":startTime, "end":endTime}

	@staticmethod
	def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
		client = dml.pymongo.MongoClient()
		repo   = client.repo
		repo.authenticate("dezhouw_ghonigsb", "dezhouw_ghonigsb")

		doc.add_namespace('alg', 'http://datamechanics.io/algorithm/')
		doc.add_namespace('dat', 'http://datamechanics.io/data/')
		doc.add_namespace('ont', 'http://datamechanics.io/ontology#')
		doc.add_namespace('log', 'http://datamechanics.io/log/')

		# extra resources
		doc.add_namespace('opd', 'https://opendata.arcgis.com/datasets/')
		doc.add_namespace('zil', 'https://www.zillow.com/webservice/')

		this_script   = doc.agent('alg:dezhouw_ghonigsb#zone', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		resource1     = doc.entity('opd:boston', {'prov:label':'Opendata Website', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
		resource2     = doc.entity('zil:boston', {'prov:label':'Zillow API',       prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'xml'})
		get_zoning    = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_zillow    = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

		doc.wasAssociatedWith(get_zoning, this_script)
		doc.wasAssociatedWith(get_zillow, this_script)

		doc.usage(get_zoning,    resource1, startTime, None,
			      {prov.model.PROV_TYPE:'ont:Retrieval',
			      'ont:Query':'?type=Boston+Neighborhood'})
		doc.usage(get_zillow,    resource2, startTime, None,
			      {prov.model.PROV_TYPE:'ont:Retrieval',
			      'ont:Query':'?type=Boston+Neighborhood'})


		zone    = doc.entity('dat:dezhouw_ghonigsb#zone',
								{prov.model.PROV_LABEL:'Zone Price Info',
								 prov.model.PROV_TYPE:'ont:DataSet'})

		doc.wasAttributedTo(zone, this_script)
		doc.wasGeneratedBy(zone, get_zoning, endTime)
		doc.wasDerivedFrom(zone, resource1, get_zoning, get_zoning, get_zoning)
		doc.wasGeneratedBy(zone, get_zillow, endTime)
		doc.wasDerivedFrom(zone, resource1, get_zillow, get_zillow, get_zillow)

		repo.logout()

		return doc

if __name__ == '__main__':
	try:
		print(zone.execute())
		doc = zone.provenance()
		print(doc.get_provn())
		print(json.dumps(json.loads(doc.serialize()), indent=4))
	except Exception as e:
		traceback.print_exc(file = sys.stdout)
	finally:
		print("Safely close")
