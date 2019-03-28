import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import numpy as np
import os
def aggregate(R, f):
	keys = {r[0] for r in R}
	return [(key, f([v for (k,v) in R if k == key])) for key in keys]

def project(R, p):
	return [p(t) for t in R]

class police(dml.Algorithm):

	contributor = 'ruipang_zhou482'
	reads = []
	writes = ['ruipang_zhou482.police']



	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()

		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('ruipang_zhou482', 'ruipang_zhou482')


		filename = "police.csv"
		url = "http://bostonopendata-boston.opendata.arcgis.com/datasets/e5a0066d38ac4e2abbc7918197a4f6af_6.csv"
		urllib.request.urlretrieve(url, filename)
		file = open(filename, "r")
		police = np.genfromtxt(file, delimiter = ",", dtype = "S")
		police = police[1:, :]
		zipcode = project(police, lambda t: t[11])
		zipcode1 = [(z.decode('utf-8'), 1) for z in zipcode]
		policePerZipcode = aggregate(zipcode1, sum)
		repo.dropCollection('ruipang_zhou482.police')
		repo.createCollection('ruipang_zhou482.police')
		for police in policePerZipcode:
			dic = {}
			dic["zipcode"] = police[0]
			dic["count"] = police[1]
			repo['ruipang_zhou482.police'].insert_one(dic)
		repo.logout()

		endTime = datetime.datetime.now()



		return {"startTime": startTime, "endTime":endTime}

	@staticmethod
	def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('ruipang_zhou482', 'ruipang_zhou482')
		doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
		doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
		doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
		doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
		doc.add_namespace('bdp', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')
		
		this_script = doc.agent('alg:ruipang_zhou482#police', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':"py"})
		resource = doc.entity('bdp:police', {'prov:label':'police', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
		
		get_police = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
		doc.wasAssociatedWith(get_police, this_script)
		doc.usage(get_police, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
		
		police = doc.entity('dat:ruipang_zhou482#police', {prov.model.PROV_LABEL:'Police Station Information', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(police, this_script)
		doc.wasGeneratedBy(police, get_police, endTime)
		doc.wasDerivedFrom(police, resource, get_police, get_police, get_police)
		
		repo.logout()

		return doc