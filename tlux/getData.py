import urllib.request
import json
import dml
import prov.model
import datetime
import csv
import codecs
import uuid

class getData(dml.Algorithm):
    contributor = 'tlux'
    reads = []
    writes = ['tlux.Raw_Age_Demo', 'tlux.Raw_Race_Demo',
              'tlux.Raw_CDC_Health', 'tlux.Raw_Open_Spaces', 'tlux.Raw_Neighborhoods']

    @staticmethod
    def execute(trial=False):
        '''Retrieve some data sets '''
        startTime = datetime.datetime.now()

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('tlux', 'tlux')

        # first dataset
        url = "https://data.boston.gov/dataset/" \
              "8202abf2-8434-4934-959b-94643c7dac18/resource/c53f0204-3b39-4a33-8068-64168dbe9847/download/age.csv"
        response = urllib.request.urlopen(url)
        response = codecs.iterdecode(response, 'utf-8', errors='ignore')
        reader = csv.DictReader(response)
        collection = []
        for row in reader:
            collection.append(dict(row))
        repo.dropCollection("Raw_Age_Demo")
        repo.createCollection("Raw_Age_Demo")
        repo['tlux.Raw_Age_Demo'].insert_many(collection)
        repo['tlux.Raw_Age_Demo'].metadata({'complete': True})

        # second dataset
        url = "https://data.boston.gov/dataset/" \
              "8202abf2-8434-4934-959b-94643c7dac18/resource/20f64c02-6023-4280-8131-e8c0cedcae9b/download/race-and-or-ethnicity.csv"
        response = urllib.request.urlopen(url)
        response = codecs.iterdecode(response, 'utf-8', errors='ignore')
        reader = csv.DictReader(response)
        collection = []
        for row in reader:
            collection.append(dict(row))
        repo.dropCollection("Raw_Race_Demo")
        repo.createCollection("Raw_Race_Demo")
        repo['tlux.Raw_Race_Demo'].insert_many(collection)
        repo['tlux.Raw_Race_Demo'].metadata({'complete': True})

        # third dataset
        url = "https://chronicdata.cdc.gov/resource/csmm-fdhi.json?cityname=Boston"
        response = json.loads(urllib.request.urlopen(url).read().decode('utf-8'))
        repo.dropCollection("Raw_CDC_Health")
        repo.createCollection("Raw_CDC_Health")
        repo['tlux.Raw_CDC_Health'].insert_many(response)
        repo['tlux.Raw_CDC_Health'].metadata({'complete': True})

        # fourth dataset
        url = "http://bostonopendata-boston.opendata.arcgis.com/datasets/2868d370c55d4d458d4ae2224ef8cddd_7.geojson"
        response = json.loads(urllib.request.urlopen(url).read())
        repo.dropCollection("Raw_Open_Spaces")
        repo.createCollection("Raw_Open_Spaces")
        repo['tlux.Raw_Open_Spaces'].insert_many(response['features'])
        repo['tlux.Raw_Open_Spaces'].metadata({'complete': True})

        # fifth dataset
        url = "http://bostonopendata-boston.opendata.arcgis.com/datasets/3525b0ee6e6b427f9aab5d0a1d0a1a28_0.geojson"
        response = json.loads(urllib.request.urlopen(url).read())
        repo.dropCollection("Raw_Neighborhoods")
        repo.createCollection("Raw_Neighborhoods")
        repo['tlux.Raw_Neighborhoods'].insert_many(response['features'])
        repo['tlux.Raw_Neighborhoods'].metadata({'complete': True})
        repo.logout()

        endTime = datetime.datetime.now()

        return {"start": startTime, "end": endTime}

    @staticmethod
    def provenance(doc=prov.model.ProvDocument(), startTime=None, endTime=None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
        client = dml.pymongo.MongoClient()
        repo = client.repo
        repo.authenticate('tlux', 'tlux')
        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.

        this_script = doc.agent('alg:tlux#getData',
                                {prov.model.PROV_TYPE: prov.model.PROV['SoftwareAgent'], 'ont:Extension': 'py'})

        # Analyze Boston Data Portal
        doc.add_namespace('bdp', 'https://data.boston.gov/dataset/')

        age_demo_resource = doc.entity('bdp:8202abf2-8434-4934-959b-94643c7dac18/resource/c53f0204-3b39-4a33-8068-64168dbe9847/download/age',
                                       {'prov:label':'Age demographics by neighborhood in Boston measured every decade',
                                                prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})
        race_demo_resource = doc.entity('bdp:8202abf2-8434-4934-959b-94643c7dac18/resource/20f64c02-6023-4280-8131-e8c0cedcae9b/download/race-and-or-ethnicity',
                                        {'prov:label':'Race demographics by neighborhood in Boston measured every decade',
                                                 prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'csv'})

        get_age_demo = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_race_demo = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_age_demo, this_script)
        doc.wasAssociatedWith(get_race_demo, this_script)

        doc.usage(get_age_demo, age_demo_resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'}
                  )
        doc.usage(get_race_demo, race_demo_resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'}
                  )
        age_demo = doc.entity('dat:tlux#Raw_Age_Demo',
                              {prov.model.PROV_LABEL: 'Age Demographics',
                               prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(age_demo, this_script)
        doc.wasGeneratedBy(age_demo, get_age_demo, endTime)
        doc.wasDerivedFrom(age_demo, age_demo_resource, get_age_demo, get_age_demo, get_age_demo)

        race_demo = doc.entity('dat:tlux#Raw_Race_Demo',
                              {prov.model.PROV_LABEL: 'Race Demographics',
                               prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(race_demo, this_script)
        doc.wasGeneratedBy(race_demo, get_race_demo, endTime)
        doc.wasDerivedFrom(race_demo, race_demo_resource, get_race_demo, get_race_demo, get_race_demo)

        # Boston-Open-Data Data Portal
        doc.add_namespace('odp', 'http://bostonopendata-boston.opendata.arcgis.com/datasets/')

        open_space_resource = doc.entity('odp:2868d370c55d4d458d4ae2224ef8cddd_7', {'prov:label': 'Open space data in Boston',
                                                  prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'geojson'})
        neighborhoods_resource = doc.entity('odp:3525b0ee6e6b427f9aab5d0a1d0a1a28_0', {'prov:label': 'Layout of Boston\'s neighborhoods',
                                                                                       prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'geojson'})

        get_open_space = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        get_neighborhoods = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)

        doc.wasAssociatedWith(get_open_space, this_script)
        doc.wasAssociatedWith(get_neighborhoods, this_script)

        doc.usage(get_open_space, open_space_resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'}
                  )
        doc.usage(get_neighborhoods, neighborhoods_resource, startTime, None,
                  {prov.model.PROV_TYPE: 'ont:Retrieval'}
                  )

        open_space = doc.entity('dat:tlux#Raw_Open_Spaces',
                               {prov.model.PROV_LABEL: 'Open Spaces in Boston', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(open_space, this_script)
        doc.wasGeneratedBy(open_space, get_open_space, endTime)
        doc.wasDerivedFrom(open_space, open_space_resource, get_open_space, get_open_space, get_open_space)

        neighborhoods = doc.entity('dat:tlux#Raw_Neighborhoods',
                               {prov.model.PROV_LABEL: 'Neighborhoods Boston', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(neighborhoods, this_script)
        doc.wasGeneratedBy(neighborhoods, get_neighborhoods, endTime)
        doc.wasDerivedFrom(neighborhoods, neighborhoods_resource, get_neighborhoods, get_neighborhoods, get_neighborhoods)

        # CDC Data Portal
        doc.add_namespace('cdc', 'https://chronicdata.cdc.gov/resource/')
        cdc_health_resource = doc.entity('cdc:csmm-fdhi', {'prov:label': 'Health survey data in Boston', prov.model.PROV_TYPE: 'ont:DataResource', 'ont:Extension': 'json'})

        get_cdc_health = doc.activity('log:uuid' + str(uuid.uuid4()), startTime, endTime)
        doc.wasAssociatedWith(get_cdc_health, this_script)
        doc.usage(get_cdc_health, cdc_health_resource, startTime, None,
                  {prov.model.PROV_TYPE:'ont:Retrieval','ont:Query':'?cityname=Boston'}
                  )
        cdc_health = doc.entity('dat:tlux#Raw_CDC_Health',
                                {prov.model.PROV_LABEL: 'Health survey data', prov.model.PROV_TYPE: 'ont:DataSet'})
        doc.wasAttributedTo(cdc_health, this_script)
        doc.wasGeneratedBy(cdc_health, get_cdc_health, endTime)
        doc.wasDerivedFrom(cdc_health, cdc_health_resource, get_cdc_health, get_cdc_health, get_cdc_health)

        repo.logout()

        return doc

