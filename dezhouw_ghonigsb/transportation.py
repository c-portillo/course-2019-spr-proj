# transportation.py
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

class transportation(dml.Algorithm):
	contributor = "dezhouw_ghonigsb"
	reads       = []
	writes      = ["transportation"]

	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()

		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo   = client.repo
		repo.authenticate("dezhouw_ghonigsb", "dezhouw_ghonigsb")

		# MassGov
		collection_name = "transportation"
		url             = "http://datamechanics.io/data/ghonigsb_dezhouw/MostRecentPeakHrByYearVolume.csv"
		response        = urllib.request.urlopen(url).read().decode("utf-8")

		repo.dropCollection(collection_name)
		repo.createCollection(collection_name)

		# Datasets Transformation
		# >>> Do select on "MassGov"
		reader = csv.DictReader(io.StringIO(response))
		next(reader, None)
		for row in reader:
			data = list(row.values())
			entry = {
				"local_id": data[0],
				"daily": int(data[8]),
				"x": float(data[9]),
				"y": float(data[10])
			}
			repo["dezhouw_ghonigsb."+collection_name].insert_one(entry)
		repo["dezhouw_ghonigsb."+collection_name].metadata({'complete':True})
		print("Success: [{}]".format(collection_name))

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
		doc.add_namespace('gov', 'http://datamechanics.io/data/ghonigsb_dezhouw/')

		this_script   = doc.agent('alg:dezhouw_ghonigsb#transportation', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		resource     = doc.entity('gov:boston', {'prov:label':'MassGov', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
		get_massGov   = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

		doc.wasAssociatedWith(get_massGov, this_script)

		doc.usage(get_massGov, resource, startTime, None,
			      {prov.model.PROV_TYPE:'ont:Retrieval',
			      'ont:Query':'?type=Peak+Hours&select=LOCAL_ID+DAILY+LATITUDE+LONGITUDE'})

		massGov   = doc.entity('dat:dezhouw_ghonigsb#transportation',
								{prov.model.PROV_LABEL:'Peak Hours',
								 prov.model.PROV_TYPE:'ont:DataSet'})

		doc.wasAttributedTo(massGov, this_script)
		doc.wasGeneratedBy(massGov, get_massGov, endTime)
		doc.wasDerivedFrom(massGov, resource, get_massGov, get_massGov, get_massGov)

		repo.logout()

		return doc

if __name__ == '__main__':
	try:
		print(transportation.execute())
		doc = transportation.provenance()
		print(doc.get_provn())
		print(json.dumps(json.loads(doc.serialize()), indent=4))
	except Exception as e:
		traceback.print_exc(file = sys.stdout)
	finally:
		print("Safely close")
