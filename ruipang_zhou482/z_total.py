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
class z_total(dml.Algorithm):

	contributor = 'ruipang_zhou482'
	reads = ["ruipang_zhou482.facilities", "ruipang_zhou482.TotalSchool", "ruipang_zhou482.PropertyAssessment"]
	writes = ['ruipang_zhou482.total']



	@staticmethod
	def execute(trial = False):

		startTime = datetime.datetime.now()

		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('ruipang_zhou482', 'ruipang_zhou482')

		school = []
		for i in repo['ruipang_zhou482.TotalSchool'].find():
			school.append({"zipcode": i["zipcode"], "count": i["total_school"]})
		facilities = []
		for i in repo['ruipang_zhou482.facilities'].find():
			facilities.append(i)
		properties = []
		for i in repo['ruipang_zhou482.PropertyAssessment'].find():
			properties.append(i)

		keys = {r['zipcode'] for r in school}
		s = []
		for k in keys:
			dic = {}
			for r in school:
				if r['zipcode'] == k:
					dic["zipcode"] = k
					dic["num_school"] = r["count"]
			foundFacilities = False
			for r in facilities:
				if r['zipcode'] == k:
					dic["num_facilities"] = r["count"]
					foundFacilities = True
			if foundFacilities == False:
				dic["num_facilities"] = 0
			for r in properties:
				if r['zipcode'] == k:
					dic["avg_value"] = r['avg_value']

			s.append(dic)
		repo.dropCollection('ruipang_zhou482.total')
		repo.createCollection('ruipang_zhou482.total')
		repo['ruipang_zhou482.total'].insert_many(s)
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
		doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
		
		this_script = doc.agent('alg:ruipang_zhou482#z_total', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':"py"})
		resource = doc.entity('dat:facilities and schools', {'prov:label':'facilities', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
		
		get_total = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
		doc.wasAssociatedWith(get_total, this_script)
		doc.usage(get_total, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
		
		total = doc.entity('dat:ruipang_zhou482#total', {prov.model.PROV_LABEL:'Hospital Information', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(total, this_script)
		doc.wasGeneratedBy(total, get_total, endTime)
		doc.wasDerivedFrom(total, resource, get_total, get_total, get_total)
		
		repo.logout()

		return doc
