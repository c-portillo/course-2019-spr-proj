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

class DataCollection(dml.Algorithm):
	contributor = 'charr_hu38'
	reads = []
	writes = ['charr_hu38.chattanooga', 'charr_hu38.washington', 'charr_hu38.newyork', 'charr_hu38.chicago', 'charr_hu38.census']

	@staticmethod
	def execute(trial = False):
		'''Retrieve some data sets (not using the API here for the sake of simplicity).'''
		startTime = datetime.datetime.now()

		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('charr_hu38', 'charr_hu38')

		url = 'https://data.chattlibrary.org/resource/sahz-tkbn.json'													
		response = urllib.request.urlopen(url).read().decode("utf-8")
		r = json.loads(response)
		data_arry=[]
		for i in list(range(len(r))):
			month = r[i]['startdate'][:7]
			duration = str(int(float(r[i]['tripdurationmin'])))
			if month=='2018-09':																						#Trivial Selection
				data_arry.append({"duration":duration,"month":month})													#Trivial Projection
		repo.dropCollection("chattanooga")
		repo.createCollection("chattanooga")
		repo['charr_hu38.chattanooga'].insert_many(data_arry)															#Data set 1: Chattanooga Bike data
		repo['charr_hu38.chattanooga'].metadata({'complete':True})

		resp = urlopen("https://s3.amazonaws.com/capitalbikeshare-data/201809-capitalbikeshare-tripdata.zip")			
		zipfile = ZipFile(BytesIO(resp.read()))
		filename = zipfile.namelist()[0]
		repo.dropCollection("washington")
		repo.createCollection("washington")
		data_arry=[]
		heading=True
		for line in tqdm(zipfile.open(filename).readlines()):
			if heading:
				heading=False
				continue
			tmp = line.decode('utf-8').split(',')
			month=tmp[1][1:-1].split(' ')[0][:-3]
			data_arry.append({"duration":tmp[0],"month":month})															#Trivial Projection

		repo['charr_hu38.washington'].insert_many(data_arry)															#Data set 2: Washington Bike data
		repo['charr_hu38.washington'].metadata({'complete':True})
		
		resp = urlopen("https://s3.amazonaws.com/tripdata/201809-citibike-tripdata.csv.zip")							
		zipfile = ZipFile(BytesIO(resp.read()))
		filename = zipfile.namelist()[0]
		repo.dropCollection("newyork")
		repo.createCollection("newyork")
		data_arry=[]
		heading=True
		for line in tqdm(zipfile.open(filename).readlines()):
			if heading:
				heading=False
				continue
			tmp = line.decode('utf-8').split(',')
			month=tmp[1][1:-1].split(' ')[0][:-3]
			data_arry.append({"duration":tmp[0],"month":month})															#Trivial Projection

		repo['charr_hu38.newyork'].insert_many(data_arry)																#Data set 3: New York Bike data
		repo['charr_hu38.newyork'].metadata({'complete':True})
		
		resp = urlopen("https://s3.amazonaws.com/divvy-data/tripdata/Divvy_Trips_2018_Q3.zip")						
		zipfile = ZipFile(BytesIO(resp.read()))
		filename = zipfile.namelist()[0]
		repo.dropCollection("chicago")
		repo.createCollection("chicago")
		data_arry=[]
		heading=True
		for line in tqdm(zipfile.open(filename).readlines()):
			if heading:
				heading=False
				continue
			tmp = line.decode('utf-8').split(',')
			if len(tmp) is 13:
				x = tmp[4] + tmp[5]
				duration = str(int(float(x.replace('"', ''))))
			else: duration = str(int(float(tmp[4].replace('"', ''))))
			month=tmp[1].split(' ')[0][:-3]
			if month=="2018-09":																						#Trivial Selection
				data_arry.append({"duration":duration,"month":month})													#Trivial Projection

		repo['charr_hu38.chicago'].insert_many(data_arry)																#Data set 4: Chicago Bike data
		repo['charr_hu38.chicago'].metadata({'complete':True})

		url = 'https://data.cdc.gov/api/views/dxpw-cm5u/rows.csv?accessType=DOWNLOAD'									
		repo.dropCollection("census")
		repo.createCollection("census")
		data_arry=[]
		r=requests.get(url)
		lines = (line.decode('utf-8') for line in r.iter_lines())
		heading=True
		for row in csv.reader(lines):
			if heading:
				heading=False
				continue
			location = row[1] + ", " + row[0]
			population = row[3]
			data_arry.append({"location":location,"population":population})												#Trivial Projection
				
		repo['charr_hu38.census'].insert_many(data_arry)																#Data set 5: Census(population) data
		repo['charr_hu38.census'].metadata({'complete':True})

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

		this_script = doc.agent('alg:charr_hu38#DataCollection', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		resource = doc.entity('bdp:wc8w-nujj', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
		get_chattanooga = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_newyork = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_washington = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_chicago = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_census = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		doc.wasAssociatedWith(get_chattanooga, this_script)
		doc.wasAssociatedWith(get_newyork, this_script)
		doc.wasAssociatedWith(get_washington, this_script)
		doc.wasAssociatedWith(get_chicago, this_script)
		doc.wasAssociatedWith(get_census, this_script)
		doc.usage(get_chattanooga, resource, startTime, None,
				  {prov.model.PROV_TYPE:'ont:Retrieval'
				  }
				  )
		doc.usage(get_newyork, resource, startTime, None,
				  {prov.model.PROV_TYPE:'ont:Retrieval'
				  }
				  )
		doc.usage(get_washington, resource, startTime, None,
				  {prov.model.PROV_TYPE:'ont:Retrieval',
				  }
				  )
		doc.usage(get_chicago, resource, startTime, None,
				  {prov.model.PROV_TYPE:'ont:Retrieval',
				  }
				  )
		doc.usage(get_census, resource, startTime, None,
				  {prov.model.PROV_TYPE:'ont:Retrieval',
				  }
				  )

		chattanooga = doc.entity('dat:charr_hu38#chattanooga', {prov.model.PROV_LABEL:'Chattanooga Bike Data', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(chattanooga, this_script)
		doc.wasGeneratedBy(chattanooga, get_chattanooga, endTime)
		doc.wasDerivedFrom(chattanooga, resource, get_chattanooga, get_chattanooga, get_chattanooga)
				  
		newyork = doc.entity('dat:charr_hu38#newyork', {prov.model.PROV_LABEL:'New York Bike Data', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(newyork, this_script)
		doc.wasGeneratedBy(newyork, get_newyork, endTime)
		doc.wasDerivedFrom(newyork, resource, get_newyork, get_newyork, get_newyork)

		washington = doc.entity('dat:charr_hu38#washington', {prov.model.PROV_LABEL:'Washington Bike Data', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(washington, this_script)
		doc.wasGeneratedBy(washington, get_washington, endTime)
		doc.wasDerivedFrom(washington, resource, get_washington, get_washington, get_washington)
		
		chicago = doc.entity('dat:charr_hu38#chicago', {prov.model.PROV_LABEL:'Chicago Bike Data', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(chicago, this_script)
		doc.wasGeneratedBy(chicago, get_chicago, endTime)
		doc.wasDerivedFrom(chicago, resource, get_chicago, get_chicago, get_chicago)
		
		census = doc.entity('dat:charr_hu38#census', {prov.model.PROV_LABEL:'Census data', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(census, this_script)
		doc.wasGeneratedBy(census, get_census, endTime)
		doc.wasDerivedFrom(census, resource, get_census, get_census, get_census)
		
		repo.logout()
				  
		return doc

'''
# This is DataCollection code you might use for debugging this module.
# Please remove all top-level function calls before submitting.
DataCollection.execute()
doc = DataCollection.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

## eof