## This python file is under cdeng file

import json
import dml
import prov.model
import datetime
import uuid
import pandas as pd
import csv
import io

from bson.son import SON


class Find_popular_stations(dml.Algorithm):
	contributor = 'cdeng'
	reads = ['cdeng.bike_trip', 'cdeng.stations_info', 'cdeng.Boston_bike_lane']
	writes = ['cdeng.stations_popular_start', 'cdeng.stations_popular_end',
				'cdeng.stations_near_bikelane_Boston']

	@staticmethod
	def execute(trial = False):
		'''Retrieve some data sets (not using the API here for the sake of simplicity).'''
		startTime = datetime.datetime.now()

		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo = client.repo
		# (username, password)
		repo.authenticate('cdeng', 'cdeng')

		################################### Begin Operations here ###################################
		print('Here we go, algorithm 2: Find_popular_stations')
		
		# #1 Find the stations high really high outgoing trip
		repo.dropCollection('cdeng.stations_popular_start')
		repo.createCollection('cdeng.stations_popular_start')

		pipeline = [
			{'$lookup': {
				'from' : 'cdeng.bike_trip',
				'localField' : 'Station',
				'foreignField' : 'start station name',
				'as' : 'start_trip'
				}
			},

			{'$project': {
					'_id': '$Station',
					'Outgoing_Trip': {'$size': '$start_trip'},
					'Dock': '$# of Docks',
					'Coordinate': {'Lat': '$Latitude', 'Long': '$Longitude'}
				}
			},

			{'$sort': SON([("Outgoing_Trip", -1), ("Dock", -1)])},
			{ '$out' : 'cdeng.stations_popular_start' }
		]

		repo['cdeng.stations_info'].aggregate(pipeline)


		# #2 Find the stations high really high incoming trip
		repo.dropCollection('cdeng.stations_popular_end')
		repo.createCollection('cdeng.stations_popular_end')

		pipeline2 = [
			{'$lookup': {
				'from' : 'cdeng.bike_trip',
				'localField' : 'Station',
				'foreignField' : 'end station name',
				'as' : 'end_trip'
				}
			},

			{'$project': {
					'_id': '$Station',
					'Incoming_Trip': {'$size': '$end_trip'},
					'Dock': '$# of Docks',
					'Coordinate': {'Lat': '$Latitude', 'Long': '$Longitude'}
				}
			},

			{'$sort': SON([("Incoming_Trip", -1), ("Dock", -1)])},
			{ '$out' : 'cdeng.stations_popular_end' }
		]

		repo['cdeng.stations_info'].aggregate(pipeline2)


		# #3 Find stations that locate at streets which have bike lane in Boston
		repo.dropCollection('cdeng.stations_near_bikelane_Boston')
		repo.createCollection('cdeng.stations_near_bikelane_Boston')

		pipeline3 = [
			{ '$lookup': {
					'from': 'cdeng.Boston_bike_lane',
					'localField': 'Station',
					'foreignField': 'STREET_NAM',
					'as': 'bikelane_street'
				}
			},

			{'$project': {
					'_id': '$Station',
					'Dock': '$# of Docks',
					'Coordinate': {'Lat': '$Latitude', 'Long': '$Longitude'},
					'Bike_lane_num': {'$size': '$bikelane_street'},
				}
			},

			{'$sort': SON([("Incoming_Trip", -1), ("Dock", -1)])},
			{ '$out' : 'cdeng.stations_near_bikelane_Boston' }	
		]

		repo['cdeng.stations_info'].aggregate(pipeline3)

		# Can do it later for Cambridge...
		################################### End Operations here ###################################
		repo.logout()

		endTime = datetime.datetime.now()
		return {"start": startTime, "end": endTime}

	def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
			
		'''
		Create the provenance document describing everything happening
		in this script. Each run of the script will generate a new
		document describing that invocation event.
		'''

		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('cdeng', 'cdeng')

		################################### Finish data rprovenance here
		print("Finish data provenance here...")

		doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') 
		doc.add_namespace('dat', 'http://datamechanics.io/data/')
		doc.add_namespace('ont', 'http://datamechanics.io/ontology#') 
		doc.add_namespace('log', 'http://datamechanics.io/log/') 

		doc.add_namespace('bdp', 'http://datamechanics.io/data/')
		doc.add_namespace('bdp2', 'https://s3.amazonaws.com/hubway-data')
		doc.add_namespace('bdp3', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')

		resource1 = doc.entity('bdp:201801_hubway_tripdata', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
		resource2 = doc.entity('bdp:201802_hubway_tripdata', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
		resource3 = doc.entity('bdp2:Hubway_Stations_as_of_July_2017', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
		resource4 = doc.entity('bdp3:d02c9d2003af455fbc37f550cc53d3a4_0', {'prov:label':'311, Service Requests', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})

		get_most_outcoming = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_most_incoming = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		get_station_bikelane = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)

		this_script = doc.agent('alg:cdeng#Find_popular_stations', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

		doc.wasAssociatedWith(get_most_outcoming, this_script)
		doc.wasAssociatedWith(get_most_incoming, this_script)
		doc.wasAssociatedWith(get_station_bikelane, this_script)

		doc.usage(get_most_outcoming, resource1, startTime, None,
			{prov.model.PROV_TYPE:'ont:Retrieval',
			'ont:Query':''
			}
			)

		doc.usage(get_most_outcoming, resource2, startTime, None,
			{prov.model.PROV_TYPE:'ont:Retrieval',
			'ont:Query':''
			}
			)

		doc.usage(get_most_outcoming, resource3, startTime, None,
			{prov.model.PROV_TYPE:'ont:Retrieval',
			'ont:Query':''
			}
			)

		doc.usage(get_most_incoming, resource1, startTime, None,
			{prov.model.PROV_TYPE:'ont:Retrieval',
			'ont:Query':''
			}
			)

		doc.usage(get_most_incoming, resource2, startTime, None,
			{prov.model.PROV_TYPE:'ont:Retrieval',
			'ont:Query':''
			}
			)

		doc.usage(get_most_incoming, resource3, startTime, None,
			{prov.model.PROV_TYPE:'ont:Retrieval',
			'ont:Query':''
			}
			)

		doc.usage(get_station_bikelane, resource3, startTime, None,
			{prov.model.PROV_TYPE:'ont:Retrieval',
			'ont:Query':''
			}
			)

		doc.usage(get_station_bikelane, resource4, startTime, None,
			{prov.model.PROV_TYPE:'ont:Retrieval',
			'ont:Query':''
			}
			)

		stations_popular_start = doc.entity('dat:cdeng#stations_popular_start', {prov.model.PROV_LABEL:'stations_popular_start', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(stations_popular_start, this_script)
		doc.wasGeneratedBy(stations_popular_start, get_most_outcoming, endTime)
		doc.wasDerivedFrom(stations_popular_start, resource1, get_most_outcoming, get_most_outcoming, get_most_outcoming)
		doc.wasDerivedFrom(stations_popular_start, resource2, get_most_outcoming, get_most_outcoming, get_most_outcoming)
		doc.wasDerivedFrom(stations_popular_start, resource3, get_most_outcoming, get_most_outcoming, get_most_outcoming)

		stations_popular_end = doc.entity('dat:cdeng#stations_popular_end', {prov.model.PROV_LABEL:'stations_popular_end', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(stations_popular_end, this_script)
		doc.wasGeneratedBy(stations_popular_end, get_most_incoming, endTime)
		doc.wasDerivedFrom(stations_popular_end, resource1, get_most_incoming, get_most_incoming, get_most_incoming)
		doc.wasDerivedFrom(stations_popular_end, resource2, get_most_incoming, get_most_incoming, get_most_incoming)
		doc.wasDerivedFrom(stations_popular_end, resource3, get_most_incoming, get_most_incoming, get_most_incoming)

		stations_near_bikelane_Boston = doc.entity('dat:cdeng#stations_near_bikelane_Boston', {prov.model.PROV_LABEL:'stations_near_bikelane_Boston', prov.model.PROV_TYPE:'ont:DataSet'})
		doc.wasAttributedTo(stations_near_bikelane_Boston, this_script)
		doc.wasGeneratedBy(stations_near_bikelane_Boston, get_station_bikelane, endTime)
		doc.wasDerivedFrom(stations_near_bikelane_Boston, resource3, get_station_bikelane, get_station_bikelane, get_station_bikelane)
		doc.wasDerivedFrom(stations_near_bikelane_Boston, resource4, get_station_bikelane, get_station_bikelane, get_station_bikelane)

		repo.logout()
		return doc

# This is example code you might use for debugging this module.
# Please remove all top-level function calls before submitting.

# print('\n\n####################Begin playground####################\n\n')
# Find_popular_stations.execute()
# doc = Find_popular_stations.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
# print('\n\n####################End pslayground####################\n\n')









## eof