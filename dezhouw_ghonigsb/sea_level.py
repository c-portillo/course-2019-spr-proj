# sea_level.py
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

class sea_level(dml.Algorithm):
	contributor = "dezhouw_ghonigsb"
	reads       = []
	writes      = ["sea_level"]

	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()

		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo   = client.repo
		repo.authenticate("dezhouw_ghonigsb", "dezhouw_ghonigsb")

		# nine_inch_sea_level_rise_1pct_annual_flood
		c1              = "nine_inch_sea_level_rise_1pct_annual_flood"
		url             = "https://opendata.arcgis.com/datasets/74692fe1b9b24f3c9419cd61b87e4e3b_7.geojson"
		gcontext        = ssl.SSLContext()
		response        = urllib.request.urlopen(url, context=gcontext).read().decode("utf-8")
		s1              = json.loads(response)
		print("Success: [{}]".format(c1))

		# nine_inch_sea_level_rise_high_tide
		c2              = "nine_inch_sea_level_rise_high_tide"
		url             = "https://opendata.arcgis.com/datasets/74692fe1b9b24f3c9419cd61b87e4e3b_8.geojson"
		gcontext        = ssl.SSLContext()
		response        = urllib.request.urlopen(url, context=gcontext).read().decode("utf-8")
		s2              = json.loads(response)
		print("Success: [{}]".format(c2))

		# thirty_six_inch_sea_level_rise_high_tide
		c3              = "thirty_six_inch_sea_level_rise_high_tide"
		url             = "https://opendata.arcgis.com/datasets/74692fe1b9b24f3c9419cd61b87e4e3b_8.geojson"
		gcontext        = ssl.SSLContext()
		response        = urllib.request.urlopen(url, context=gcontext).read().decode("utf-8")
		s3              = json.loads(response)
		print("Success: [{}]".format(c3))

		# thirty_six_inch_sea_level_rise_10_pct_annual_flood
		c4              = "thirty_six_inch_sea_level_rise_10_pct_annual_flood"
		url             = "https://opendata.arcgis.com/datasets/74692fe1b9b24f3c9419cd61b87e4e3b_3.geojson"
		gcontext        = ssl.SSLContext()
		response        = urllib.request.urlopen(url, context=gcontext).read().decode("utf-8")
		s4              = json.loads(response)
		print("Success: [{}]".format(c4))

		# Datasets Transformation
		# >>> Combine sea level datasets
		collection_name = "sea_level"
		repo.dropCollection(collection_name)
		repo.createCollection(collection_name)

		repo["dezhouw_ghonigsb."+collection_name].insert_one({c1: s1})
		repo["dezhouw_ghonigsb."+collection_name].insert_one({c2: s2})
		repo["dezhouw_ghonigsb."+collection_name].insert_one({c3: s3})
		repo["dezhouw_ghonigsb."+collection_name].insert_one({c4: s4})

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

		this_script   = doc.agent('alg:dezhouw_ghonigsb#sea_level', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		resource      = doc.entity('opd:boston', {'prov:label':'Opendata Website', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'geojson'})
		get_seaAnnual = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_seaTide   = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_seaAnnual2= doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_seaTide2  = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

		doc.wasAssociatedWith(get_seaAnnual, this_script)
		doc.wasAssociatedWith(get_seaTide,   this_script)
		doc.wasAssociatedWith(get_seaAnnual2,this_script)
		doc.wasAssociatedWith(get_seaTide2,  this_script)

		doc.usage(get_seaAnnual, resource, startTime, None,
			      {prov.model.PROV_TYPE:'ont:Retrieval',
			      'ont:Query':'?type=Sea+Level+Annual+9'})
		doc.usage(get_seaTide,   resource, startTime, None,
			      {prov.model.PROV_TYPE:'ont:Retrieval',
			      'ont:Query':'?type=Sea+High+Tide+9'})
		doc.usage(get_seaAnnual2,resource, startTime, None,
			      {prov.model.PROV_TYPE:'ont:Retrieval',
			      'ont:Query':'?type=Sea+Level+Annual+36'})
		doc.usage(get_seaTide2,  resource, startTime, None,
			      {prov.model.PROV_TYPE:'ont:Retrieval',
			      'ont:Query':'?type=Sea+High+Tide+36'})

		seaLevel = doc.entity('dat:dezhouw_ghonigsb#sea_level',
								{prov.model.PROV_LABEL:'Sea Level',
								 prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(seaLevel, this_script)
		doc.wasGeneratedBy(seaLevel, get_seaAnnual, endTime)
		doc.wasDerivedFrom(seaLevel, resource, get_seaAnnual, get_seaAnnual, get_seaAnnual)


		doc.wasGeneratedBy(seaLevel, get_seaTide, endTime)
		doc.wasDerivedFrom(seaLevel, resource, get_seaTide, get_seaTide, get_seaTide)

		doc.wasGeneratedBy(seaLevel, get_seaAnnual2, endTime)
		doc.wasDerivedFrom(seaLevel, resource, get_seaAnnual2, get_seaAnnual2, get_seaAnnual2)

		doc.wasGeneratedBy(seaLevel, get_seaTide2, endTime)
		doc.wasDerivedFrom(seaLevel, resource, get_seaTide2, get_seaTide2, get_seaTide2)

		repo.logout()

		return doc

if __name__ == '__main__':
	try:
		print(sea_level.execute())
		# doc = sea_level.provenance()
		# print(doc.get_provn())
		# print(json.dumps(json.loads(doc.serialize()), indent=4))
	except Exception as e:
		traceback.print_exc(file = sys.stdout)
	finally:
		print("Safely close")
