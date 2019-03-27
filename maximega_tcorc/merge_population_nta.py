import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class merge_population_nta(dml.Algorithm):
	contributor = 'maximega_tcorc'
	reads = ['maximega_tcorc.population', 'maximega_tcorc.neighborhoods_with_stations']
	writes = ['maximega_tcorc.population_with_neighborhoods']
	
	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()

		repo_name = merge_population_nta.writes[0]
		# ----------------- Set up the database connection -----------------
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('maximega_tcorc', 'maximega_tcorc')

		populations = repo.maximega_tcorc.population
		neighborhoods = repo.maximega_tcorc.neighborhoods_with_stations
		
		# ----------------- NTA info with NTA populations -----------------
		insert_many_arr = []
		for neighborhood in neighborhoods.find():
			for population in populations.find():
				if neighborhood['ntacode'] == population['nta_code']:
					insert_many_arr.append({
						'ntacode': neighborhood['ntacode'], 
						'ntaname': neighborhood['ntaname'], 
						'the_geom': neighborhood['the_geom'], 
						'stations': neighborhood['stations'], 
						'population': population['population']
					})
					break

		#----------------- Data insertion into Mongodb ------------------
		repo.dropCollection('population_with_neighborhoods')
		repo.createCollection('population_with_neighborhoods')
		repo[repo_name].insert_many(insert_many_arr)
		repo[repo_name].metadata({'complete':True})
		print(repo[repo_name].metadata())

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
		repo.authenticate('maximega_tcorc', 'maximega_tcorc')
		doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
		doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
		doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
		doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

		#agent
		this_script = doc.agent('alg:maximega_tcorc#merge_population_nta', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		#resource
		population = doc.entity('dat:maximega_tcorc#population', {prov.model.PROV_LABEL:'NYC Neighborhood Population Info', prov.model.PROV_TYPE:'ont:DataSet'})
		neighborhoods_with_stations = doc.entity('dat:maximega_tcorc#neighborhoods_with_stations', {prov.model.PROV_LABEL:'NYC Neighborhoods + Subway Station Info', prov.model.PROV_TYPE:'ont:DataSet'})
		#agent
		merging_populations_neighborhoods = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

		doc.wasAssociatedWith(merging_populations_neighborhoods, this_script)

		doc.usage(merging_populations_neighborhoods, population, startTime, None,
					{prov.model.PROV_TYPE:'ont:Computation'
					}
					)
		doc.usage(merging_populations_neighborhoods, neighborhoods_with_stations, startTime, None,
					{prov.model.PROV_TYPE:'ont:Computation'
					}
					)
		#reasource
		population_with_neighborhoods = doc.entity('dat:maximega_tcorc#population_with_neighborhoods', {prov.model.PROV_LABEL:'NYC Neighborhood Info + Population Info', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(population_with_neighborhoods, this_script)
		doc.wasGeneratedBy(population_with_neighborhoods, merging_populations_neighborhoods, endTime)
		doc.wasDerivedFrom(population_with_neighborhoods, population, merging_populations_neighborhoods, merging_populations_neighborhoods, merging_populations_neighborhoods)
		doc.wasDerivedFrom(population_with_neighborhoods, neighborhoods_with_stations, merging_populations_neighborhoods, merging_populations_neighborhoods, merging_populations_neighborhoods)

		repo.logout()
				
		return doc

