import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
from maximega_tcorc.helper_functions.within_polygon import point_inside_polygon

class merge_stations_nta(dml.Algorithm):
	contributor = 'maximega_tcorc'
	reads = ['maximega_tcorc.stations', 'maximega_tcorc.neighborhoods']
	writes = ['maximega_tcorc.neighborhoods_with_stations']
	
	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()

		repo_name = merge_stations_nta.writes[0]
		# ----------------- Set up the database connection -----------------
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('maximega_tcorc', 'maximega_tcorc')

		stations = repo.maximega_tcorc.stations.find()
		ntas = repo.maximega_tcorc.neighborhoods.find()

		duplicates = []
		filtered_stations = []
		# ----------------- Create a list of unique stations (stations data contains many duplicates) -----------------
		for station in stations:
			name = station['Station Name']
			if name not in duplicates:
				duplicates.append(name)
				filtered_stations.append(station)

		nta_objects = {}
		nta_count = 0
		station_count = 0
		# ----------------- Merge NTA info with station info if the subway station is inside of NTA multi polygon -----------------
		for nta in ntas:
			nta_objects[nta['ntacode']] = {'ntacode': nta['ntacode'],'ntaname': nta['ntaname'], 'the_geom': nta['the_geom'], 'stations': []}
			nta_multipolygon = nta['the_geom']['coordinates'][0][0]

			for station in filtered_stations:
				# ----------------- station coordinates come in form: (lat, long) as a string -----------------
				# ----------------- retreive lat and long points, cast them to floats to be passed into point_inside_polygon function -----------------				
				station_coordinates = station['Entrance Location']
				lat_coord = ''
				long_coord = ''
				i = 1
				while(station_coordinates[i] != ','):
					lat_coord += station_coordinates[i]
					i += 1
				i += 2
				while(station_coordinates[i] != ')'):
					long_coord += station_coordinates[i]
					i += 1
				lat_coord = float(lat_coord)
				long_coord = float(long_coord)
				#print(type(nta_multipolygon[0][0]))
				is_in_nta = point_inside_polygon(long_coord, lat_coord, nta_multipolygon)
				if is_in_nta:
					nta_objects[nta['ntacode']]['stations'].append({
						'station_name': station['Station Name']
					})
		# ----------------- Reformat data for mongodb insertion -----------------
		insert_many_arr = []
		for key in nta_objects.keys():
			insert_many_arr.append(nta_objects[key])

		#----------------- Data insertion into Mongodb ------------------
		repo.dropCollection('neighborhoods_with_stations')
		repo.createCollection('neighborhoods_with_stations')
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
		this_script = doc.agent('alg:maximega_tcorc#merge_stations_nta', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		#resource
		stations = doc.entity('dat:maximega_tcorc#stations', {prov.model.PROV_LABEL:'NYC Subway Stations Info', prov.model.PROV_TYPE:'ont:DataSet'})
		neighborhoods = doc.entity('dat:maximega_tcorc#neighborhoods', {prov.model.PROV_LABEL:'NYC Neighborhoods Info', prov.model.PROV_TYPE:'ont:DataSet'})
		#agent
		merging_stations_neighborhoods = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

		doc.wasAssociatedWith(merging_stations_neighborhoods, this_script)

		doc.usage(merging_stations_neighborhoods, stations, startTime, None,
					{prov.model.PROV_TYPE:'ont:Computation'
					}
					)
		doc.usage(merging_stations_neighborhoods, neighborhoods, startTime, None,
					{prov.model.PROV_TYPE:'ont:Computation'
					}
					)
		#reasource
		neighborhoods_with_stations = doc.entity('dat:maximega_tcorc#neighborhoods_with_stations', {prov.model.PROV_LABEL:'NYC Neighborhood Info + Subway Station Info', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(neighborhoods_with_stations, this_script)
		doc.wasGeneratedBy(neighborhoods_with_stations, merging_stations_neighborhoods, endTime)
		doc.wasDerivedFrom(neighborhoods_with_stations, stations, merging_stations_neighborhoods, merging_stations_neighborhoods, merging_stations_neighborhoods)
		doc.wasDerivedFrom(neighborhoods_with_stations, neighborhoods, merging_stations_neighborhoods, merging_stations_neighborhoods, merging_stations_neighborhoods)

		repo.logout()
				
		return doc


