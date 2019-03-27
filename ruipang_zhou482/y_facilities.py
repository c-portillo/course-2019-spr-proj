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
class y_facilities(dml.Algorithm):

	contributor = 'ruipang_zhou482'
	reads = ["ruipang_zhou482.hospital", "ruipang_zhou482.police"]
	writes = ['ruipang_zhou482.facilities']



	@staticmethod
	def execute(trial = False):

		startTime = datetime.datetime.now()

		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('ruipang_zhou482', 'ruipang_zhou482')

		police = []
		for i in repo['ruipang_zhou482.police'].find():
			police.append(i)
		hospital = []
		for i in repo['ruipang_zhou482.hospital'].find():
			hospital.append(i)

		total = police + hospital

		s = []
		keys = {r['zipcode'] for r in total}
		for k in keys:
			dic = {}
			sum = 0
			for r in total:
				if r['zipcode'] == k:
					sum += r['count']
			dic['zipcode'] = k
			dic['count'] = sum
			s.append(dic)

		repo.dropCollection('ruipang_zhou482.facilities')
		repo.createCollection('ruipang_zhou482.facilities')
		repo['ruipang_zhou482.facilities'].insert_many(s)
		repo.logout()

		endTime = datetime.datetime.now()
		return {"start": startTime, "end": endTime}

	@staticmethod
	def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('ruipang_zhou482', 'ruipang_zhou482')
		doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
		doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
		doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
		doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
		doc.add_namespace('bdp', 'https://data.boston.gov/dataset/d9871e89-2d1e-4ecf-b0de-046f553027c0/resource/6222085d-ee88-45c6-ae40-0c7464620d64/download/')
		
		this_script = doc.agent('alg:ruipang_zhou482#y_facilities', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':"py"})
		resource = doc.entity('dat:hospital and police', {'prov:label':'hospital', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
		
		get_facilities = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
		doc.wasAssociatedWith(get_facilities, this_script)
		doc.usage(get_facilities, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
		
		facilities = doc.entity('dat:ruipang_zhou482#facilities', {prov.model.PROV_LABEL:'Hospital Information', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(facilities, this_script)
		doc.wasGeneratedBy(facilities, get_facilities, endTime)
		doc.wasDerivedFrom(facilities, resource, get_facilities, get_facilities, get_facilities)
		
		repo.logout()

		return doc
