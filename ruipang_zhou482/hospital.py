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
class hospital(dml.Algorithm):

	contributor = 'ruipang_zhou482'
	reads = []
	writes = ['ruipang_zhou482.hospital']



	@staticmethod
	def execute(trial = False):

		startTime = datetime.datetime.now()

		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('ruipang_zhou482', 'ruipang_zhou482')


		filename = "hospital.csv"
		url = "https://data.boston.gov/dataset/d9871e89-2d1e-4ecf-b0de-046f553027c0/resource/6222085d-ee88-45c6-ae40-0c7464620d64/download/hospital-locations.csv"
		urllib.request.urlretrieve(url, filename)
		file = open(filename, "r")
		cleaned = ""
		counter = 0
		for line in file:
			if (counter - 1) % 3 == 0:
				pos = line.rfind(',')
				cleaned = cleaned + line[:pos] + "\n"
			counter += 1
		file.close()
		file = open(filename, "w")
		file.write(cleaned)
		file.close()
		file = open(filename, "r")
		hospital = np.genfromtxt(file, delimiter = ",", dtype = "S")
		hospital = np.delete(hospital, [0, 1, 3, 4, 5, 6], axis = 1)
		hospital = ["0" + zipcode[0].decode("utf-8") for zipcode in hospital]
		zipcode1 = [(zipcode, 1) for zipcode in hospital]
		hospitalPerZipcode = aggregate(zipcode1, sum)

		repo.dropCollection('ruipang_zhou482.hospital')
		repo.createCollection('ruipang_zhou482.hospital')
		for hospital in hospitalPerZipcode:
			dic = {}
			dic["zipcode"] = hospital[0]
			dic["count"] = hospital[1]
			repo['ruipang_zhou482.hospital'].insert_one(dic)
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
		
		this_script = doc.agent('alg:ruipang_zhou482#hospital', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':"py"})
		resource = doc.entity('bdp:hospital-locations', {'prov:label':'hospital', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
		
		get_hospital = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
		doc.wasAssociatedWith(get_hospital, this_script)
		doc.usage(get_hospital, resource, startTime, None, {prov.model.PROV_TYPE:'ont:Retrieval'})
		
		hospital = doc.entity('dat:ruipang_zhou482#hospital', {prov.model.PROV_LABEL:'Hospital Information', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(hospital, this_script)
		doc.wasGeneratedBy(hospital, get_hospital, endTime)
		doc.wasDerivedFrom(hospital, resource, get_hospital, get_hospital, get_hospital)
		
		repo.logout()

		return doc

hospital = hospital()
hospital.execute()
doc = hospital.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))