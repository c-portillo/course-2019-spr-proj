import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import requests
import csv
from tqdm import tqdm

class AggBikeData(dml.Algorithm):
	contributor = 'charr_hu38'
	reads = ['charr_hu38.chattanooga', 'charr_hu38.washington', 'charr_hu38.newyork', 'charr_hu38.chicago']
	writes = ['charr_hu38.aggbikedata']

	@staticmethod
	def execute(trial = False):
		'''Aggregate total city bike use data into one dataset'''
		startTime = datetime.datetime.now()

		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('charr_hu38', 'charr_hu38')

		repo.dropCollection("aggbikedata")
		repo.createCollection("aggbikedata")
		
		data_arry=[]
		chattanooga = list(repo.charr_hu38.chattanooga.find())
		total_duration=0
		for entry in chattanooga:
			total_duration+=int(entry['duration'])
		data_arry.append({"city":"Chattanooga, TN","tot_bike_time":total_duration})			#Aggsum (Non Trivial transformation #1)
		
		washington = list(repo.charr_hu38.washington.find())
		total_duration=0
		for entry in washington:
			total_duration+=int(entry['duration'])
		data_arry.append({"city":"Washington, DC","tot_bike_time":total_duration})			#Aggsum
		
		newyork = list(repo.charr_hu38.newyork.find())
		total_duration=0
		for entry in newyork:
			total_duration+=int(entry['duration'])
		data_arry.append({"city":"New York, NY","tot_bike_time":total_duration})			#Aggsum
		
		chicago = list(repo.charr_hu38.chicago.find())
		total_duration=0
		for entry in chicago:
			total_duration+=int(entry['duration'])
		data_arry.append({"city":"Chicago, IL","tot_bike_time":total_duration})				#Aggsum
		
		repo['charr_hu38.aggbikedata'].insert_many(data_arry)								#Union of 4 aggregations (Non Trivial transformation #2)
		repo['charr_hu38.aggbikedata'].metadata({'complete':True})
		
		#We treat the 4 aggregations as 1 single non trivial transformation, and we treat the union operation as a second nontrivial transformation

		repo.logout()

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
		repo.authenticate('charr_hu38', 'charr_hu38')
		doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
		doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
		doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
		doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
		doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')

		this_script = doc.agent('alg:charr_hu38#AggBikeData', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'Total Time Spent on Rented Bikes per City', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
		
		get_aggbikedata = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		doc.wasAssociatedWith(get_aggbikedata, this_script)
		doc.usage(get_aggbikedata, resource, startTime, None,
				  {prov.model.PROV_TYPE:'ont:Computation'
				  }
				  )

		aggbikedata = doc.entity('dat:charr_hu38#aggbikedata', {prov.model.PROV_LABEL:'Total Bike Time per City studied', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(aggbikedata, this_script)
		doc.wasGeneratedBy(aggbikedata, get_aggbikedata, endTime)
		doc.wasDerivedFrom(aggbikedata, resource, get_aggbikedata, get_aggbikedata, get_aggbikedata)
		
		repo.logout()
				  
		return doc

'''
# This is AggBikeData code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
AggBikeData.execute()
doc = AggBikeData.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof