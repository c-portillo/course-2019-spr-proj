import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class merge_income(dml.Algorithm):
	contributor = 'maximega_tcorc'
	reads = ['maximega_tcorc.income_with_tracts', 'maximega_tcorc.population_with_neighborhoods']
	writes = ['maximega_tcorc.income_with_neighborhoods']
	
	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()

		repo_name = merge_income.writes[0]
		# ----------------- Set up the database connection -----------------
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('maximega_tcorc', 'maximega_tcorc')

        # ----------------- Retrieve data from Mongodb -----------------
		incomes = repo.maximega_tcorc.income_with_tracts
		neighborhoods = repo.maximega_tcorc.population_with_neighborhoods
		
		# ----------------- Merge Census Tract incomes with NTA info, aggregate and average incomes for NTA -----------------
		insert_many_arr = []
		count_tracts = 0
		total_income = 0
		for neighborhood in neighborhoods.find():
			for income in incomes.find():
				if neighborhood['ntacode'] == income['nta']:
					count_tracts += 1
					total_income += float(income['income'])
					if(income['income'] == 'None'):
						print(income['nta'])
			avg_income = total_income/count_tracts
			insert_many_arr.append({
				'ntacode': neighborhood['ntacode'], 
				'ntaname': neighborhood['ntaname'],  
				'stations': neighborhood['stations'], 
				'population': neighborhood['population'],
				'income': avg_income
			})

		#----------------- Data insertion into Mongodb ------------------
		repo.dropCollection('income_with_neighborhoods')
		repo.createCollection('income_with_neighborhoods')
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
		this_script = doc.agent('alg:maximega_tcorc#merge_census_data', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		#resource
		income_with_tracts = doc.entity('dat:maximega_tcorc#income_with_tracts', {prov.model.PROV_LABEL:'NYC Census Tracts + Income Info', prov.model.PROV_TYPE:'ont:DataSet'})
		population_with_neighborhoods = doc.entity('dat:maximega_tcorc#population_with_neighborhoods', {prov.model.PROV_LABEL:'NYC Neighborhoods + Subway Stations', prov.model.PROV_TYPE:'ont:DataSet'})
		#agent
		merging_income_NTA = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

		doc.wasAssociatedWith(merging_income_NTA, this_script)

		doc.usage(merging_income_NTA, income_with_tracts, startTime, None,
					{prov.model.PROV_TYPE:'ont:Computation'
					}
					)
		doc.usage(merging_income_NTA, population_with_neighborhoods, startTime, None,
					{prov.model.PROV_TYPE:'ont:Computation'
					}
					)
		#reasource
		income_with_NTA = doc.entity('dat:maximega_tcorc#income_with_neighborhoods', {prov.model.PROV_LABEL:'NYC Census Info + AVG Income per Tract', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(income_with_NTA, this_script)
		doc.wasGeneratedBy(income_with_NTA, merging_income_NTA, endTime)
		doc.wasDerivedFrom(income_with_NTA, income_with_tracts, merging_income_NTA, merging_income_NTA, merging_income_NTA)
		doc.wasDerivedFrom(income_with_NTA, population_with_neighborhoods, merging_income_NTA, merging_income_NTA, merging_income_NTA)

		repo.logout()
				
		return doc

