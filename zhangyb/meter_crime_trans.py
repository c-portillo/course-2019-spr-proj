import urllib.request
import json
import dml
import prov.model
import datetime
import uuid

class meter_crime_trans(dml.Algorithm):
    contributor = 'zhangyb'
    reads = ['zhangyb.parking_meter_location',
             'zhangyb.crime_report']
    writes = ['zhangyb.meter_crime']

    @staticmethod
    def execute(trial = False):

        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('zhangyb', 'zhangyb')

        repo.dropPermanent("meter_crime")
        repo.createPermanent("meter_crime")

        # Retrieve data from MongoDB
        parking_meter = repo['zhangyb.parking_meter_location']
        crime = repo['zhangyb.crime_report']

        meter_json = parking_meter.find()
        crime_json = crime.find()

        # Used to retrieve crime reports of a specific year
        crime_year = 2019

        '''
        Tranformation 3:
        It is not appropreate to set up a Hubway station on a place with parking meters
        It is also not appropreate to set it up near a crime location
        Merge the crime location and parking meter location datasets to get locations that are not appropreate for setting up Hubway stations
        '''

        data = {'Data': []}
        count = 0

        for obj in crime_json:
            if obj['year'] == crime_year:
                # Remove datasets with null
                if obj['lat'] is not None:
                    data['Data'] += [{'ID': count, 'Type': 'Crime', 'Latitudes': obj['lat'], 'Longitudes': obj['long']}]
                    count += 1

        for obj in meter_json:
            data['Data'] += [{'ID': count,'Type': 'Meter', 'Latitudes':obj['Y'], 'Longitudes':obj['X']}]
            count += 1

        repo['zhangyb.meter_crime'].insert_one(data)
        repo['zhangyb.meter_crime'].metadata({'complete':True})

        #repo.logout()

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
        repo.authenticate('zhangyb', 'zhangyb')

        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format. 
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format. 
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:zhangyb#meter_crime_trans',{prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
        get_meter_crime = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_meter_crime, this_script)

        meter = doc.entity('dat:zhangyb#parking_meter_location', {prov.model.PROV_LABEL:'Parking Meter Locations', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.usage(get_meter_crime, meter, startTime)

        crime = doc.entity('dat:zhangyb#crime_report', {prov.model.PROV_LABEL:'Crime Reports', prov.model.PROV_TYPE:'ont:DataSet'})
        doc.usage(get_meter_crime, crime, startTime)

        meter_crime = doc.entity('dat:zhangyb#meter_crime', {'prov:label':'Parking Meter and Crime Locations', prov.model.PROV_TYPE:'ont:Dataset'})

        doc.wasAttributedTo(meter_crime, this_script)
        doc.wasGeneratedBy(meter_crime, get_meter_crime, endTime)
        doc.wasDerivedFrom(meter_crime, meter, get_meter_crime, get_meter_crime, get_meter_crime)
        doc.wasDerivedFrom(meter_crime, crime, get_meter_crime, get_meter_crime, get_meter_crime)

        #repo.logout()

        return doc

'''
meter_crime_trans.execute()
doc = meter_crime_trans.provenance()
print(doc.get_provn())
print(json.dumps(json.loads(doc.serialize()), indent=4))
'''

